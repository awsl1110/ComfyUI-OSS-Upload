import hashlib
import os
import re
import mimetypes
import random
import string
import tempfile
from datetime import datetime
from pathlib import PurePosixPath

import numpy as np
from PIL import Image

import alibabacloud_oss_v2 as oss

try:
    import scipy.io.wavfile as _wav
except ImportError:
    _wav = None


_ENDPOINT_RE = re.compile(r"oss-([a-z0-9-]+?)(?:-internal)?\.aliyuncs\.com")


def _region_from_endpoint(endpoint: str) -> str:
    m = _ENDPOINT_RE.search(endpoint)
    return m.group(1) if m else ""


def _resolve_region(endpoint: str, region: str) -> str:
    derived = _region_from_endpoint(endpoint.strip())
    return derived if derived else region


def _get_oss_client(region: str, access_key_id: str, access_key_secret: str, endpoint: str = ""):
    credentials_provider = oss.credentials.StaticCredentialsProvider(access_key_id, access_key_secret)
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.retry_max_attempts = 3
    ep = endpoint.strip()
    if ep:
        cfg.endpoint = ep
        cfg.region = _resolve_region(ep, region)
    else:
        cfg.region = region
    return oss.Client(cfg)


def _random_filename(ext: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{ts}_{suffix}.{ext.lstrip('.')}"


def _make_key(oss_path: str, use_random: bool, filename: str, ext: str) -> str:
    fname = _random_filename(ext) if use_random or not filename.strip() else filename.strip()
    return str(PurePosixPath(oss_path.strip("/")) / fname)


def _build_url(endpoint: str, region: str, bucket: str, key: str) -> str:
    ep = endpoint.strip()
    if not ep:
        return f"https://{bucket}.oss-{region}.aliyuncs.com/{key}"
    derived = _region_from_endpoint(ep)
    if derived:
        return f"https://{bucket}.oss-{derived}.aliyuncs.com/{key}"
    host = ep.rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    return f"{host}/{key}"


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _object_exists(client, bucket: str, key: str) -> bool:
    try:
        client.head_object(oss.HeadObjectRequest(bucket=bucket, key=key))
        return True
    except Exception as e:
        # OperationError wraps ServiceError; unwrap to reach status_code
        inner = e.unwrap() if hasattr(e, "unwrap") else e
        if getattr(inner, "status_code", None) == 404:
            return False
        raise


# ---------------------------------------------------------------------------
# Login node
# ---------------------------------------------------------------------------

class OSSLogin:
    CATEGORY = "OSS Upload"
    FUNCTION = "login"
    RETURN_TYPES = ("OSS_CONNECTION",)
    RETURN_NAMES = ("oss_connection",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "region": ("STRING", {"default": "cn-hangzhou", "tooltip": "OSS region, e.g. cn-hangzhou"}),
                "endpoint": ("STRING", {"default": "", "tooltip": "Custom endpoint (leave blank to auto-build from region)"}),
                "bucket": ("STRING", {"default": "", "tooltip": "OSS bucket name"}),
                "access_key_id": ("STRING", {"default": "", "tooltip": "Alibaba Cloud AccessKey ID"}),
                "access_key_secret": ("STRING", {"default": "", "tooltip": "Alibaba Cloud AccessKey Secret", "password": True}),
            }
        }

    def login(self, region, endpoint, bucket, access_key_id, access_key_secret):
        client = _get_oss_client(region, access_key_id, access_key_secret, endpoint)
        return ({"client": client, "bucket": bucket, "region": region, "endpoint": endpoint},)


# ---------------------------------------------------------------------------
# Shared upload inputs (path/filename only)
# ---------------------------------------------------------------------------

_UPLOAD_INPUTS = {
    "oss_path": ("STRING", {"default": "comfyui/", "tooltip": "Object key prefix / folder path in OSS"}),
    "random_filename": ("BOOLEAN", {"default": True}),
    "filename": ("STRING", {"default": "", "tooltip": "Custom filename (used when random_filename is False)"}),
    "skip_duplicate": ("BOOLEAN", {"default": True, "tooltip": "若 OSS 中已存在相同内容则跳过上传（基于 SHA-256）。需要 oss:GetObject 权限。"}),
}


# ---------------------------------------------------------------------------
# Image uploader
# ---------------------------------------------------------------------------

class OSSImageUploader:
    CATEGORY = "OSS Upload"
    FUNCTION = "upload"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",), "oss_connection": ("OSS_CONNECTION",), **_UPLOAD_INPUTS}}

    def upload(self, image, oss_connection, oss_path, random_filename, filename, skip_duplicate):
        if len(image.shape) == 4:
            image = image[0]
        arr = (image.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        pil_img = Image.fromarray(arr)

        client = oss_connection["client"]
        bucket = oss_connection["bucket"]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, "image.png")
            pil_img.save(tmp_path, format="PNG")

            if skip_duplicate:
                digest = _sha256_file(tmp_path)
                key = str(PurePosixPath(oss_path.strip("/")) / f"{digest}.png")
                if _object_exists(client, bucket, key):
                    return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)
            else:
                key = _make_key(oss_path, random_filename, filename, "png")

            client.put_object_from_file(
                oss.PutObjectRequest(bucket=bucket, key=key, content_type="image/png"),
                tmp_path,
            )

        return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)


# ---------------------------------------------------------------------------
# Video uploader
# ---------------------------------------------------------------------------

class OSSVideoUploader:
    CATEGORY = "OSS Upload"
    FUNCTION = "upload"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"video": ("VIDEO",), "oss_connection": ("OSS_CONNECTION",), **_UPLOAD_INPUTS}}

    def upload(self, video, oss_connection, oss_path, random_filename, filename, skip_duplicate):
        from comfy_api.latest import Types

        fmt = "auto"
        ext = Types.VideoContainer.get_extension(fmt)
        client = oss_connection["client"]
        bucket = oss_connection["bucket"]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, f"video.{ext}")
            video.save_to(tmp_path, format=Types.VideoContainer(fmt), codec="auto", metadata=None)

            if skip_duplicate:
                digest = _sha256_file(tmp_path)
                key = str(PurePosixPath(oss_path.strip("/")) / f"{digest}.{ext}")
                if _object_exists(client, bucket, key):
                    return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)
            else:
                key = _make_key(oss_path, random_filename, filename, ext)

            client.uploader().upload_file(
                oss.PutObjectRequest(bucket=bucket, key=key, content_type=mimetypes.guess_type(tmp_path)[0]),
                tmp_path,
            )

        return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)


# ---------------------------------------------------------------------------
# Audio uploader
# ---------------------------------------------------------------------------

class OSSAudioUploader:
    CATEGORY = "OSS Upload"
    FUNCTION = "upload"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio": ("AUDIO",), "oss_connection": ("OSS_CONNECTION",), **_UPLOAD_INPUTS}}

    def upload(self, audio, oss_connection, oss_path, random_filename, filename, skip_duplicate):
        if _wav is None:
            raise RuntimeError("scipy is not installed. Run: pip install scipy")

        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        if len(waveform.shape) == 3:
            waveform = waveform[0]
        arr = waveform.cpu().numpy().T
        if arr.shape[1] == 1:
            arr = arr[:, 0]
        audio_data = arr if arr.dtype == np.float32 else arr.astype(np.float32)

        client = oss_connection["client"]
        bucket = oss_connection["bucket"]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, "audio.wav")
            _wav.write(tmp_path, sample_rate, audio_data)

            if skip_duplicate:
                digest = _sha256_file(tmp_path)
                key = str(PurePosixPath(oss_path.strip("/")) / f"{digest}.wav")
                if _object_exists(client, bucket, key):
                    return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)
            else:
                key = _make_key(oss_path, random_filename, filename, "wav")

            client.uploader().upload_file(
                oss.PutObjectRequest(bucket=bucket, key=key, content_type="audio/wav"),
                tmp_path,
            )

        return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)


# ---------------------------------------------------------------------------
# Generic file uploader
# ---------------------------------------------------------------------------

class OSSFileUploader:
    CATEGORY = "OSS Upload"
    FUNCTION = "upload"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "", "tooltip": "Absolute path to the local file"}),
                "oss_connection": ("OSS_CONNECTION",),
                **_UPLOAD_INPUTS,
            }
        }

    def upload(self, file_path, oss_connection, oss_path, random_filename, filename, skip_duplicate):
        file_path = file_path.strip()
        if not file_path or not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lstrip(".")
        client = oss_connection["client"]
        bucket = oss_connection["bucket"]

        if skip_duplicate:
            digest = _sha256_file(file_path)
            key = str(PurePosixPath(oss_path.strip("/")) / f"{digest}.{ext}")
            if _object_exists(client, bucket, key):
                return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)
        else:
            key = _make_key(oss_path, random_filename, filename, ext)

        client.uploader().upload_file(
            oss.PutObjectRequest(bucket=bucket, key=key, content_type=mimetypes.guess_type(file_path)[0]),
            file_path,
        )

        return (_build_url(oss_connection["endpoint"], oss_connection["region"], bucket, key),)


# ---------------------------------------------------------------------------
# Node registry
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "OSSLogin": OSSLogin,
    "OSSImageUploader": OSSImageUploader,
    "OSSVideoUploader": OSSVideoUploader,
    "OSSAudioUploader": OSSAudioUploader,
    "OSSFileUploader": OSSFileUploader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OSSLogin": "OSS Login",
    "OSSImageUploader": "OSS Image Uploader",
    "OSSVideoUploader": "OSS Video Uploader",
    "OSSAudioUploader": "OSS Audio Uploader",
    "OSSFileUploader": "OSS File Uploader",
}

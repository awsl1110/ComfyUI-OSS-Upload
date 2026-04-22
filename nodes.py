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
        # signing region must match the endpoint's embedded region
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
    # Custom domain (CDN / CNAME)
    host = ep.rstrip("/")
    if not host.startswith("http"):
        host = f"https://{host}"
    return f"{host}/{key}"


# ---------------------------------------------------------------------------
# Shared input definitions
# ---------------------------------------------------------------------------

_OSS_INPUTS = {
    "region": ("STRING", {"default": "cn-hangzhou", "tooltip": "OSS region, e.g. cn-hangzhou"}),
    "endpoint": ("STRING", {"default": "", "tooltip": "Custom endpoint (leave blank to auto-build from region)"}),
    "bucket": ("STRING", {"default": "", "tooltip": "OSS bucket name"}),
    "access_key_id": ("STRING", {"default": "", "tooltip": "Alibaba Cloud AccessKey ID"}),
    "access_key_secret": ("STRING", {"default": "", "tooltip": "Alibaba Cloud AccessKey Secret", "password": True}),
    "oss_path": ("STRING", {"default": "comfyui/", "tooltip": "Object key prefix / folder path in OSS"}),
    "random_filename": ("BOOLEAN", {"default": True}),
    "filename": ("STRING", {"default": "", "tooltip": "Custom filename (used when random_filename is False)"}),
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
        return {"required": {"image": ("IMAGE",), **_OSS_INPUTS}}

    def upload(self, image, region, endpoint, bucket, access_key_id, access_key_secret,
               oss_path, random_filename, filename):
        if len(image.shape) == 4:
            image = image[0]  # take first frame from batch
        arr = (image.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        pil_img = Image.fromarray(arr)

        key = _make_key(oss_path, random_filename, filename, "png")
        client = _get_oss_client(region, access_key_id, access_key_secret, endpoint)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, os.path.basename(key))
            pil_img.save(tmp_path, format="PNG")
            client.put_object_from_file(
                oss.PutObjectRequest(bucket=bucket, key=key, content_type="image/png"),
                tmp_path,
            )

        return (_build_url(endpoint, region, bucket, key),)


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
        return {"required": {"video": ("VIDEO",), **_OSS_INPUTS}}

    def upload(self, video, region, endpoint, bucket, access_key_id, access_key_secret,
               oss_path, random_filename, filename):
        from comfy_api.latest import Types

        fmt = "auto"
        ext = Types.VideoContainer.get_extension(fmt)
        key = _make_key(oss_path, random_filename, filename, ext)
        client = _get_oss_client(region, access_key_id, access_key_secret, endpoint)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, os.path.basename(key))
            video.save_to(tmp_path, format=Types.VideoContainer(fmt), codec="auto", metadata=None)
            client.uploader().upload_file(
                oss.PutObjectRequest(bucket=bucket, key=key, content_type=mimetypes.guess_type(tmp_path)[0]),
                tmp_path,
            )

        return (_build_url(endpoint, region, bucket, key),)


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
        return {"required": {"audio": ("AUDIO",), **_OSS_INPUTS}}

    def upload(self, audio, region, endpoint, bucket, access_key_id, access_key_secret,
               oss_path, random_filename, filename):
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

        key = _make_key(oss_path, random_filename, filename, "wav")
        client = _get_oss_client(region, access_key_id, access_key_secret, endpoint)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, os.path.basename(key))
            _wav.write(tmp_path, sample_rate, audio_data)
            client.uploader().upload_file(
                oss.PutObjectRequest(bucket=bucket, key=key, content_type="audio/wav"),
                tmp_path,
            )

        return (_build_url(endpoint, region, bucket, key),)


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
                **_OSS_INPUTS,
            }
        }

    def upload(self, file_path, region, endpoint, bucket, access_key_id, access_key_secret,
               oss_path, random_filename, filename):
        file_path = file_path.strip()
        if not file_path or not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lstrip(".")
        key = _make_key(oss_path, random_filename, filename, ext)
        client = _get_oss_client(region, access_key_id, access_key_secret, endpoint)
        client.uploader().upload_file(
            oss.PutObjectRequest(bucket=bucket, key=key, content_type=mimetypes.guess_type(file_path)[0]),
            file_path,
        )

        return (_build_url(endpoint, region, bucket, key),)


# ---------------------------------------------------------------------------
# Node registry
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "OSSImageUploader": OSSImageUploader,
    "OSSVideoUploader": OSSVideoUploader,
    "OSSAudioUploader": OSSAudioUploader,
    "OSSFileUploader": OSSFileUploader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OSSImageUploader": "OSS Image Uploader",
    "OSSVideoUploader": "OSS Video Uploader",
    "OSSAudioUploader": "OSS Audio Uploader",
    "OSSFileUploader": "OSS File Uploader",
}

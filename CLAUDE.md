# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A ComfyUI custom node pack that uploads generated assets (images, videos, audio, arbitrary files) to **Alibaba Cloud OSS** from within ComfyUI workflows. Each node returns the public URL of the uploaded object.

## Installation & dependencies

```bash
pip install -r requirements.txt   # alibabacloud_oss_v2, numpy
pip install scipy                  # required only for OSSAudioUploader
```

There is no build step. ComfyUI loads the package by importing `__init__.py` from the `custom_nodes/` directory.

## Publishing

Bumping the version in `pyproject.toml` and pushing to `master` triggers the GitHub Actions workflow (`.github/workflows/publish_action.yml`) that publishes to the Comfy Registry. The secret `REGISTRY_ACCESS_TOKEN` must be set in the repo settings.

## Architecture

All logic lives in **`nodes.py`**. `__init__.py` only re-exports `NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS`, and sets `WEB_DIRECTORY = "web"` (pointing ComfyUI at the `web/` docs folder).

### Node classes (`nodes.py`)

**`OSSLogin`** — takes region, endpoint, bucket, access_key_id, access_key_secret and returns an `OSS_CONNECTION` object (a plain dict holding the `oss.Client` instance plus bucket/region/endpoint). Wire this once; all uploader nodes accept it as their `oss_connection` input.

| Uploader class | ComfyUI input type | Upload method | Format |
|---|---|---|---|
| `OSSImageUploader` | `IMAGE` (tensor) | `put_object_from_file` | PNG |
| `OSSVideoUploader` | `VIDEO` | `uploader().upload_file` | auto-detected |
| `OSSAudioUploader` | `AUDIO` (dict with `waveform`/`sample_rate`) | `uploader().upload_file` | WAV (float32) |
| `OSSFileUploader` | `file_path` (string) | `uploader().upload_file` | passthrough |

Uploaders share `_UPLOAD_INPUTS` (oss_path, random_filename, filename) and all five nodes are registered in `NODE_CLASS_MAPPINGS` / `NODE_DISPLAY_NAME_MAPPINGS`.

### Key helpers

- **`_get_oss_client`** — builds an `alibabacloud_oss_v2.Client` with static credentials; sets `retry_max_attempts = 3`; if an endpoint is provided it sets `cfg.endpoint` and derives the signing region from the endpoint string.
- **`_region_from_endpoint`** — extracts the region code from a standard `oss-<region>[-internal].aliyuncs.com` endpoint via regex.
- **`_build_url`** — returns the public URL: standard OSS URL when no/standard endpoint is given, or `https://<custom-domain>/<key>` for CDN/CNAME endpoints.
- **`_make_key`** — joins `oss_path` and a filename (random timestamp+suffix or user-supplied) into a POSIX object key.

### ComfyUI tensor conventions

- `IMAGE` tensors arrive as `(batch, H, W, C)` float32 in [0, 1]; the uploader takes `image[0]`, multiplies by 255, and converts to uint8 for PIL.
- `AUDIO` is a dict `{"waveform": Tensor(batch, channels, samples), "sample_rate": int}`.
- `VIDEO` is handled via `comfy_api.latest.Types` (imported lazily inside the method).

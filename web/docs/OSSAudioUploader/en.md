# OSS Audio Uploader

Upload a ComfyUI audio tensor to **Alibaba Cloud OSS** and return its public URL.

The audio waveform is encoded as **WAV** (32-bit float, preserving the original sample rate) before upload. Multi-channel audio is supported; mono audio is handled automatically.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `audio` | AUDIO | Input audio dict containing `waveform` (tensor) and `sample_rate` |
| `oss_connection` | OSS_CONNECTION | Connection from the **OSS Login** node |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/audio/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix. When **False**, the `filename` field is used. Ignored when `skip_duplicate` is enabled |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled and `skip_duplicate` is off). Include the extension, e.g. `output.wav` |
| `skip_duplicate` | BOOLEAN | When **True**, computes a SHA-256 hash of the audio and skips the upload if identical content already exists in OSS. The existing URL is returned immediately. Requires `oss:GetObject` permission |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded audio file |

## Notes

- Requires `scipy` to be installed (`pip install scipy`).
- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- When `skip_duplicate` is **True**, the object key is `<oss_path>/<sha256>.wav` (content-addressed). `random_filename` and `filename` have no effect.
- Audio is always saved as WAV regardless of the `filename` extension.

## Usage Example

Connect a TTS or audio generation node → **OSS Audio Uploader** → use the returned `url` in a downstream node to play or reference the audio.

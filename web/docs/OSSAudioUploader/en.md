# OSS Audio Uploader

Upload a ComfyUI audio tensor to **Alibaba Cloud OSS** and return its public URL.

The audio waveform is encoded as **WAV** (32-bit float, preserving the original sample rate) before upload. Multi-channel audio is supported; mono audio is handled automatically.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `audio` | AUDIO | Input audio dict containing `waveform` (tensor) and `sample_rate` |
| `region` | STRING | OSS region code, e.g. `cn-hangzhou`, `us-west-1` |
| `endpoint` | STRING | Custom endpoint URL. Leave blank to auto-build the standard endpoint from `region`. Use this for VPC internal endpoints or CDN/CNAME custom domains |
| `bucket` | STRING | Target OSS bucket name |
| `access_key_id` | STRING | Alibaba Cloud RAM AccessKey ID |
| `access_key_secret` | STRING | Alibaba Cloud RAM AccessKey Secret |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/audio/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix. When **False**, the `filename` field is used |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled). Include the extension, e.g. `output.wav` |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded audio file |

## Notes

- Requires `scipy` to be installed (`pip install scipy`).
- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- Upload is retried up to **10 times** with a 3-second delay on failure.
- Audio is always saved as WAV regardless of the `filename` extension for consistency.

## Usage Example

Connect a TTS or audio generation node → **OSS Audio Uploader** → use the returned `url` in a downstream node to play or reference the audio.

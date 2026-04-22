# OSS Video Uploader

Upload a ComfyUI video to **Alibaba Cloud OSS** and return its public URL.

The node delegates format detection and encoding to ComfyUI's built-in `VideoContainer` API (`format="auto"`), so the output file extension is determined automatically.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `video` | VIDEO | Input video from any ComfyUI video-producing node |
| `region` | STRING | OSS region code, e.g. `cn-hangzhou`, `us-west-1` |
| `endpoint` | STRING | Custom endpoint URL. Leave blank to auto-build the standard endpoint from `region`. Use this for VPC internal endpoints or CDN/CNAME custom domains |
| `bucket` | STRING | Target OSS bucket name |
| `access_key_id` | STRING | Alibaba Cloud RAM AccessKey ID |
| `access_key_secret` | STRING | Alibaba Cloud RAM AccessKey Secret |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/videos/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix. When **False**, the `filename` field is used |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled). Include the extension, e.g. `output.mp4` |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded video |

## Notes

- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- Upload is retried up to **10 times** with a 3-second delay on failure.
- The video is temporarily written to disk in a system temp directory before upload, then cleaned up automatically.

## Usage Example

Connect a video generation node (e.g. **Video Combine**) → **OSS Video Uploader** → use the returned `url` in an API call or text display node.

# OSS Video Uploader

Upload a ComfyUI video to **Alibaba Cloud OSS** and return its public URL.

The node delegates format detection and encoding to ComfyUI's built-in `VideoContainer` API (`format="auto"`), so the output file extension is determined automatically.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `video` | VIDEO | Input video from any ComfyUI video-producing node |
| `oss_connection` | OSS_CONNECTION | Connection from the **OSS Login** node |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/videos/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix. When **False**, the `filename` field is used. Ignored when `skip_duplicate` is enabled |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled and `skip_duplicate` is off). Include the extension, e.g. `output.mp4` |
| `skip_duplicate` | BOOLEAN | When **True**, computes a SHA-256 hash of the video and skips the upload if identical content already exists in OSS. The existing URL is returned immediately. Requires `oss:GetObject` permission |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded video |

## Notes

- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- When `skip_duplicate` is **True**, the object key is `<oss_path>/<sha256>.<ext>` (content-addressed). `random_filename` and `filename` have no effect.
- The video is temporarily written to disk in a system temp directory before upload, then cleaned up automatically.

## Usage Example

Connect a video generation node (e.g. **Video Combine**) → **OSS Video Uploader** → use the returned `url` in an API call or text display node.

# OSS Image Uploader

Upload a ComfyUI image tensor to **Alibaba Cloud OSS** and return its public URL.

The node accepts a batch of images but only uploads the **first frame**. The image is automatically encoded as **PNG** before upload.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `image` | IMAGE | Input image (or image batch — first frame is used) |
| `oss_connection` | OSS_CONNECTION | Connection from the **OSS Login** node |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/images/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix. When **False**, the `filename` field is used. Ignored when `skip_duplicate` is enabled |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled and `skip_duplicate` is off). Include the extension, e.g. `output.png` |
| `skip_duplicate` | BOOLEAN | When **True**, computes a SHA-256 hash of the image and skips the upload if identical content already exists in OSS. The existing URL is returned immediately. Requires `oss:GetObject` permission |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded image |

## Notes

- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- When `skip_duplicate` is **True**, the object key is `<oss_path>/<sha256>.png` (content-addressed). `random_filename` and `filename` have no effect.
- The returned URL format depends on the `endpoint` setting in **OSS Login**:
  - No endpoint → `https://<bucket>.oss-<region>.aliyuncs.com/<key>`
  - Standard OSS endpoint → derived from embedded region
  - Custom domain/CDN → `https://<custom-domain>/<key>`

## Usage Example

Connect a **Save Image** or any node that outputs `IMAGE` → **OSS Image Uploader** → use the returned `url` string in downstream text or API call nodes.

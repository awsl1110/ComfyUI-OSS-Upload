# OSS Image Uploader

Upload a ComfyUI image tensor to **Alibaba Cloud OSS** and return its public URL.

The node accepts a batch of images but only uploads the **first frame**. The image is automatically encoded as **PNG** before upload.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `image` | IMAGE | Input image (or image batch — first frame is used) |
| `region` | STRING | OSS region code, e.g. `cn-hangzhou`, `us-west-1` |
| `endpoint` | STRING | Custom endpoint URL. Leave blank to auto-build the standard endpoint from `region`. Use this for VPC internal endpoints (e.g. `oss-cn-hangzhou-internal.aliyuncs.com`) or CDN/CNAME custom domains |
| `bucket` | STRING | Target OSS bucket name |
| `access_key_id` | STRING | Alibaba Cloud RAM AccessKey ID |
| `access_key_secret` | STRING | Alibaba Cloud RAM AccessKey Secret |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/images/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix. When **False**, the `filename` field is used |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled). Include the extension, e.g. `output.png` |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded image |

## Notes

- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- Upload is retried up to **10 times** with a 3-second delay on failure.
- The returned URL format depends on the `endpoint` setting:
  - No endpoint → `https://<bucket>.oss-<region>.aliyuncs.com/<key>`
  - Standard OSS endpoint → derived from embedded region
  - Custom domain/CDN → `https://<custom-domain>/<key>`

## Usage Example

Connect a **Save Image** or any node that outputs `IMAGE` → **OSS Image Uploader** → use the returned `url` string in downstream text or API call nodes.

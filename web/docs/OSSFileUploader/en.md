# OSS File Uploader

Upload **any local file** to **Alibaba Cloud OSS** by specifying its absolute path, and return the public URL.

This is a generic uploader — the file is sent as-is without any re-encoding. The file extension is preserved automatically.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `file_path` | STRING | Absolute path to the local file, e.g. `/home/user/output/model.safetensors` |
| `region` | STRING | OSS region code, e.g. `cn-hangzhou`, `us-west-1` |
| `endpoint` | STRING | Custom endpoint URL. Leave blank to auto-build the standard endpoint from `region`. Use this for VPC internal endpoints or CDN/CNAME custom domains |
| `bucket` | STRING | Target OSS bucket name |
| `access_key_id` | STRING | Alibaba Cloud RAM AccessKey ID |
| `access_key_secret` | STRING | Alibaba Cloud RAM AccessKey Secret |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/files/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix (original extension kept). When **False**, the `filename` field is used |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled). Include the extension, e.g. `my-model.safetensors` |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded file |

## Notes

- Raises `FileNotFoundError` immediately if `file_path` does not point to an existing file.
- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- Upload is retried up to **10 times** with a 3-second delay on failure.
- Unlike the other upload nodes, this node reads directly from disk — no temporary copy is made.

## Usage Example

Use a **String** constant node to provide the path → **OSS File Uploader** → use the returned `url` to reference the file from external services or store it in metadata.

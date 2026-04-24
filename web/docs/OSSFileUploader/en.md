# OSS File Uploader

Upload **any local file** to **Alibaba Cloud OSS** by specifying its absolute path, and return the public URL.

This is a generic uploader — the file is sent as-is without any re-encoding. The file extension is preserved automatically.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `file_path` | STRING | Absolute path to the local file, e.g. `/home/user/output/model.safetensors` |
| `oss_connection` | OSS_CONNECTION | Connection from the **OSS Login** node |
| `oss_path` | STRING | Key prefix (folder path) inside the bucket, e.g. `comfyui/files/` |
| `random_filename` | BOOLEAN | When **True**, generates a unique filename with timestamp + random suffix (original extension kept). When **False**, the `filename` field is used. Ignored when `skip_duplicate` is enabled |
| `filename` | STRING | Custom filename (only applied when `random_filename` is disabled and `skip_duplicate` is off). Include the extension, e.g. `my-model.safetensors` |
| `skip_duplicate` | BOOLEAN | When **True**, computes a SHA-256 hash of the file and skips the upload if identical content already exists in OSS. The existing URL is returned immediately. Requires `oss:GetObject` permission |

## Outputs

| Name | Type | Description |
|---|---|---|
| `url` | STRING | Public URL of the uploaded file |

## Notes

- Raises `FileNotFoundError` immediately if `file_path` does not point to an existing file.
- Requires the bucket to allow public read, or use a signed URL / CDN in front of OSS for private buckets.
- When `skip_duplicate` is **True**, the object key is `<oss_path>/<sha256>.<ext>` (content-addressed). `random_filename` and `filename` have no effect.
- Unlike the other upload nodes, this node reads directly from disk — no temporary copy is made.

## Usage Example

Use a **String** constant node to provide the path → **OSS File Uploader** → use the returned `url` to reference the file from external services or store it in metadata.

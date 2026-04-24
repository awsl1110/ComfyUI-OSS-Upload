# OSS Login

Create an **Alibaba Cloud OSS** connection and pass it to any uploader node.

Configure credentials once here and wire the `oss_connection` output to one or more uploader nodes — no need to enter credentials in each uploader individually.

## Inputs

| Parameter | Type | Description |
|---|---|---|
| `region` | STRING | OSS region code, e.g. `cn-hangzhou`, `us-west-1`, `ap-southeast-1` |
| `endpoint` | STRING | Custom endpoint URL. Leave blank to auto-build the standard endpoint from `region`. Use this for VPC internal endpoints (e.g. `oss-cn-hangzhou-internal.aliyuncs.com`) or CDN/CNAME custom domains |
| `bucket` | STRING | Target OSS bucket name |
| `access_key_id` | STRING | Alibaba Cloud RAM AccessKey ID |
| `access_key_secret` | STRING | Alibaba Cloud RAM AccessKey Secret |

## Outputs

| Name | Type | Description |
|---|---|---|
| `oss_connection` | OSS_CONNECTION | Connection object carrying the OSS client, bucket, region, and endpoint — pass to any uploader node |

## Notes

- The RAM user needs **`oss:PutObject`** to upload files.
- If **Skip Duplicate** is enabled on any uploader, the RAM user additionally needs **`oss:GetObject`** (used by the `HeadObject` existence check).
- Create a dedicated RAM sub-account scoped to the target bucket rather than using your root account AccessKey.

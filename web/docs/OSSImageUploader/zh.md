# OSS 图片上传节点

将 ComfyUI 图像张量上传到**阿里云 OSS**，并返回其公网访问 URL。

节点接受批量图像输入，但仅上传**第一帧**。图像在上传前会自动编码为 **PNG** 格式。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `image` | IMAGE | 输入图像（或图像批次，取第一帧） |
| `region` | STRING | OSS 地域代码，例如 `cn-hangzhou`、`us-west-1` |
| `endpoint` | STRING | 自定义 Endpoint URL。留空则根据 `region` 自动构建标准 Endpoint。可用于 VPC 内网 Endpoint（如 `oss-cn-hangzhou-internal.aliyuncs.com`）或 CDN / CNAME 自定义域名 |
| `bucket` | STRING | 目标 OSS Bucket 名称 |
| `access_key_id` | STRING | 阿里云 RAM 访问密钥 ID |
| `access_key_secret` | STRING | 阿里云 RAM 访问密钥 Secret |
| `oss_path` | STRING | Bucket 内的键前缀（目录路径），例如 `comfyui/images/` |
| `random_filename` | BOOLEAN | 为 **True** 时自动生成带时间戳和随机后缀的唯一文件名；为 **False** 时使用 `filename` 字段指定的文件名 |
| `filename` | STRING | 自定义文件名（仅在 `random_filename` 关闭时生效），需包含扩展名，例如 `output.png` |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `url` | STRING | 上传成功后的图片公网 URL |

## 注意事项

- 需要 Bucket 开启公共读权限，或在 OSS 前方挂载 CDN / 签名 URL 以支持私有 Bucket 访问。
- 上传失败时最多自动重试 **10 次**，每次间隔 3 秒。
- 返回 URL 的格式取决于 `endpoint` 设置：
  - 未填写 Endpoint → `https://<bucket>.oss-<region>.aliyuncs.com/<key>`
  - 标准 OSS Endpoint → 从 Endpoint 中提取地域代码后构建
  - 自定义域名 / CDN → `https://<自定义域名>/<key>`

## 使用示例

将任意输出 `IMAGE` 类型的节点连接到 **OSS 图片上传节点**，即可获得图片的 URL 字符串，供下游文本节点或 API 调用节点使用。

# OSS 视频上传节点

将 ComfyUI 视频上传到**阿里云 OSS**，并返回其公网访问 URL。

节点通过 ComfyUI 内置的 `VideoContainer` API（`format="auto"`）自动完成格式检测与编码，输出文件扩展名由此自动决定。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `video` | VIDEO | 来自任意 ComfyUI 视频生成节点的视频输入 |
| `region` | STRING | OSS 地域代码，例如 `cn-hangzhou`、`us-west-1` |
| `endpoint` | STRING | 自定义 Endpoint URL。留空则根据 `region` 自动构建标准 Endpoint。可用于 VPC 内网 Endpoint 或 CDN / CNAME 自定义域名 |
| `bucket` | STRING | 目标 OSS Bucket 名称 |
| `access_key_id` | STRING | 阿里云 RAM 访问密钥 ID |
| `access_key_secret` | STRING | 阿里云 RAM 访问密钥 Secret |
| `oss_path` | STRING | Bucket 内的键前缀（目录路径），例如 `comfyui/videos/` |
| `random_filename` | BOOLEAN | 为 **True** 时自动生成带时间戳和随机后缀的唯一文件名；为 **False** 时使用 `filename` 字段指定的文件名 |
| `filename` | STRING | 自定义文件名（仅在 `random_filename` 关闭时生效），需包含扩展名，例如 `output.mp4` |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `url` | STRING | 上传成功后的视频公网 URL |

## 注意事项

- 需要 Bucket 开启公共读权限，或在 OSS 前方挂载 CDN / 签名 URL 以支持私有 Bucket 访问。
- 上传失败时最多自动重试 **10 次**，每次间隔 3 秒。
- 视频在上传前会临时写入系统临时目录，上传完成后自动清理。

## 使用示例

将视频生成节点（如 **Video Combine**）连接到 **OSS 视频上传节点**，即可获得视频的 URL 字符串，供下游 API 调用或文本显示节点使用。

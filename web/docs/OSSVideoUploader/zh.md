# OSS 视频上传节点

将 ComfyUI 视频上传到**阿里云 OSS**，并返回其公网访问 URL。

节点通过 ComfyUI 内置的 `VideoContainer` API（`format="auto"`）自动完成格式检测与编码，输出文件扩展名由此自动决定。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `video` | VIDEO | 来自任意 ComfyUI 视频生成节点的视频输入 |
| `oss_connection` | OSS_CONNECTION | 来自 **OSS 登录节点** 的连接对象 |
| `oss_path` | STRING | Bucket 内的键前缀（目录路径），例如 `comfyui/videos/` |
| `random_filename` | BOOLEAN | 为 **True** 时自动生成带时间戳和随机后缀的唯一文件名；为 **False** 时使用 `filename` 字段。启用 `skip_duplicate` 时此参数无效 |
| `filename` | STRING | 自定义文件名（仅在 `random_filename` 关闭且 `skip_duplicate` 未启用时生效），需包含扩展名，例如 `output.mp4` |
| `skip_duplicate` | BOOLEAN | 为 **True** 时，计算视频的 SHA-256 哈希值，若 OSS 中已存在相同内容则跳过上传并直接返回已有 URL。需要 `oss:GetObject` 权限 |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `url` | STRING | 上传成功后的视频公网 URL |

## 注意事项

- 需要 Bucket 开启公共读权限，或在 OSS 前方挂载 CDN / 签名 URL 以支持私有 Bucket 访问。
- 启用 `skip_duplicate` 时，对象键为 `<oss_path>/<sha256>.<ext>`（基于内容寻址），`random_filename` 和 `filename` 不再生效。
- 视频在上传前会临时写入系统临时目录，上传完成后自动清理。

## 使用示例

将视频生成节点（如 **Video Combine**）连接到 **OSS 视频上传节点**，即可获得视频的 URL 字符串，供下游 API 调用或文本显示节点使用。

# OSS 图片上传节点

将 ComfyUI 图像张量上传到**阿里云 OSS**，并返回其公网访问 URL。

节点接受批量图像输入，但仅上传**第一帧**。图像在上传前会自动编码为 **PNG** 格式。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `image` | IMAGE | 输入图像（或图像批次，取第一帧） |
| `oss_connection` | OSS_CONNECTION | 来自 **OSS 登录节点** 的连接对象 |
| `oss_path` | STRING | Bucket 内的键前缀（目录路径），例如 `comfyui/images/` |
| `random_filename` | BOOLEAN | 为 **True** 时自动生成带时间戳和随机后缀的唯一文件名；为 **False** 时使用 `filename` 字段。启用 `skip_duplicate` 时此参数无效 |
| `filename` | STRING | 自定义文件名（仅在 `random_filename` 关闭且 `skip_duplicate` 未启用时生效），需包含扩展名，例如 `output.png` |
| `skip_duplicate` | BOOLEAN | 为 **True** 时，计算图像的 SHA-256 哈希值，若 OSS 中已存在相同内容则跳过上传并直接返回已有 URL。需要 `oss:GetObject` 权限 |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `url` | STRING | 上传成功后的图片公网 URL |

## 注意事项

- 需要 Bucket 开启公共读权限，或在 OSS 前方挂载 CDN / 签名 URL 以支持私有 Bucket 访问。
- 启用 `skip_duplicate` 时，对象键为 `<oss_path>/<sha256>.png`（基于内容寻址），`random_filename` 和 `filename` 不再生效。
- 返回 URL 的格式取决于 **OSS 登录节点** 中的 `endpoint` 设置：
  - 未填写 Endpoint → `https://<bucket>.oss-<region>.aliyuncs.com/<key>`
  - 标准 OSS Endpoint → 从 Endpoint 中提取地域代码后构建
  - 自定义域名 / CDN → `https://<自定义域名>/<key>`

## 使用示例

将任意输出 `IMAGE` 类型的节点连接到 **OSS 图片上传节点**，即可获得图片的 URL 字符串，供下游文本节点或 API 调用节点使用。

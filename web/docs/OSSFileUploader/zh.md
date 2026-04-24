# OSS 文件上传节点

通过指定本地文件的绝对路径，将**任意本地文件**上传到**阿里云 OSS**，并返回其公网访问 URL。

这是一个通用上传节点，文件会原样上传，不做任何重新编码，文件扩展名自动保留。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `file_path` | STRING | 本地文件的绝对路径，例如 `/home/user/output/model.safetensors` |
| `oss_connection` | OSS_CONNECTION | 来自 **OSS 登录节点** 的连接对象 |
| `oss_path` | STRING | Bucket 内的键前缀（目录路径），例如 `comfyui/files/` |
| `random_filename` | BOOLEAN | 为 **True** 时自动生成带时间戳和随机后缀的唯一文件名（保留原始扩展名）；为 **False** 时使用 `filename` 字段。启用 `skip_duplicate` 时此参数无效 |
| `filename` | STRING | 自定义文件名（仅在 `random_filename` 关闭且 `skip_duplicate` 未启用时生效），需包含扩展名，例如 `my-model.safetensors` |
| `skip_duplicate` | BOOLEAN | 为 **True** 时，计算文件的 SHA-256 哈希值，若 OSS 中已存在相同内容则跳过上传并直接返回已有 URL。需要 `oss:GetObject` 权限 |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `url` | STRING | 上传成功后的文件公网 URL |

## 注意事项

- 若 `file_path` 指向的文件不存在，节点会立即抛出 `FileNotFoundError`。
- 需要 Bucket 开启公共读权限，或在 OSS 前方挂载 CDN / 签名 URL 以支持私有 Bucket 访问。
- 启用 `skip_duplicate` 时，对象键为 `<oss_path>/<sha256>.<ext>`（基于内容寻址），`random_filename` 和 `filename` 不再生效。
- 与其他上传节点不同，本节点直接从磁盘读取文件，无需创建临时副本。

## 使用示例

使用**字符串常量节点**提供文件路径 → **OSS 文件上传节点**，即可获得文件的 URL 字符串，供外部服务引用或存储到元数据中。

# OSS 音频上传节点

将 ComfyUI 音频张量上传到**阿里云 OSS**，并返回其公网访问 URL。

音频波形在上传前会以 **WAV** 格式（32 位浮点，保留原始采样率）进行编码。支持多声道音频，单声道音频会自动处理。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `audio` | AUDIO | 包含 `waveform`（张量）和 `sample_rate` 的音频字典 |
| `region` | STRING | OSS 地域代码，例如 `cn-hangzhou`、`us-west-1` |
| `endpoint` | STRING | 自定义 Endpoint URL。留空则根据 `region` 自动构建标准 Endpoint。可用于 VPC 内网 Endpoint 或 CDN / CNAME 自定义域名 |
| `bucket` | STRING | 目标 OSS Bucket 名称 |
| `access_key_id` | STRING | 阿里云 RAM 访问密钥 ID |
| `access_key_secret` | STRING | 阿里云 RAM 访问密钥 Secret |
| `oss_path` | STRING | Bucket 内的键前缀（目录路径），例如 `comfyui/audio/` |
| `random_filename` | BOOLEAN | 为 **True** 时自动生成带时间戳和随机后缀的唯一文件名；为 **False** 时使用 `filename` 字段指定的文件名 |
| `filename` | STRING | 自定义文件名（仅在 `random_filename` 关闭时生效），需包含扩展名，例如 `output.wav` |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `url` | STRING | 上传成功后的音频文件公网 URL |

## 注意事项

- 需要安装 `scipy`（`pip install scipy`）。
- 需要 Bucket 开启公共读权限，或在 OSS 前方挂载 CDN / 签名 URL 以支持私有 Bucket 访问。
- 上传失败时最多自动重试 **10 次**，每次间隔 3 秒。
- 无论 `filename` 填写何种扩展名，音频始终以 WAV 格式保存，以保持一致性。

## 使用示例

将 TTS 或音频生成节点连接到 **OSS 音频上传节点**，即可获得音频文件的 URL 字符串，供下游节点播放或引用。

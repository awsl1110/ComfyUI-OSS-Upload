# OSS 登录节点

创建**阿里云 OSS** 连接，并将其传递给任意上传节点。

在此处统一配置凭证，将 `oss_connection` 输出连接到一个或多个上传节点，无需在每个上传节点中分别填写凭证。

## 输入参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `region` | STRING | OSS 地域代码，例如 `cn-hangzhou`、`us-west-1`、`ap-southeast-1` |
| `endpoint` | STRING | 自定义 Endpoint URL。留空则根据 `region` 自动构建标准 Endpoint。可用于 VPC 内网 Endpoint（如 `oss-cn-hangzhou-internal.aliyuncs.com`）或 CDN / CNAME 自定义域名 |
| `bucket` | STRING | 目标 OSS Bucket 名称 |
| `access_key_id` | STRING | 阿里云 RAM 访问密钥 ID |
| `access_key_secret` | STRING | 阿里云 RAM 访问密钥 Secret |

## 输出

| 名称 | 类型 | 说明 |
|---|---|---|
| `oss_connection` | OSS_CONNECTION | 包含 OSS 客户端、Bucket、地域和 Endpoint 的连接对象，传递给任意上传节点使用 |

## 注意事项

- RAM 用户需具备 **`oss:PutObject`** 权限才能上传文件。
- 若任意上传节点启用了**跳过重复内容**功能，RAM 用户还需具备 **`oss:GetObject`** 权限（用于 `HeadObject` 存在性检查）。
- 建议创建专用 RAM 子账号并将权限范围限定到目标 Bucket，切勿使用主账号 AccessKey。

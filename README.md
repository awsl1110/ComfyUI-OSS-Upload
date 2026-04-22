# ComfyUI-OSS-Upload

[English](#english) | [中文](#中文)

---

## English

A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) custom node pack for uploading generated assets (images, videos, audio, and arbitrary files) directly to **Alibaba Cloud OSS** from within your workflow. Each node returns the public URL of the uploaded file, making it easy to chain with API call or text display nodes.

### Nodes

| Node | Input | Output | Description |
|---|---|---|---|
| **OSS Image Uploader** | `IMAGE` | `url` | Encodes the first frame as PNG and uploads it |
| **OSS Video Uploader** | `VIDEO` | `url` | Auto-detects format and uploads the video |
| **OSS Audio Uploader** | `AUDIO` | `url` | Encodes as WAV (32-bit float) and uploads |
| **OSS File Uploader** | `file_path` | `url` | Uploads any local file by absolute path |

All nodes live in the **OSS Upload** category.

### Requirements

- Python packages: `alibabacloud_oss_v2`, `numpy`
- `scipy` is required for **OSS Audio Uploader** (`pip install scipy`)
- An Alibaba Cloud account with OSS enabled and a RAM AccessKey pair

### Installation

**Via ComfyUI Manager** (recommended): search for `ComfyUI-OSS-Upload` and install.

**Manual:**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/awsl1110/ComfyUI-OSS-Upload.git
cd ComfyUI-OSS-Upload
pip install -r requirements.txt
```

### Configuration

Every node shares the same set of OSS connection parameters:

| Parameter | Description |
|---|---|
| `region` | OSS region code, e.g. `cn-hangzhou`, `us-west-1`, `ap-southeast-1` |
| `endpoint` | Custom endpoint. Leave blank for standard OSS endpoints. Use for VPC internal access (`oss-<region>-internal.aliyuncs.com`) or CDN/CNAME custom domains |
| `bucket` | OSS bucket name |
| `access_key_id` | Alibaba Cloud RAM AccessKey ID |
| `access_key_secret` | Alibaba Cloud RAM AccessKey Secret |
| `oss_path` | Key prefix / folder path inside the bucket, e.g. `comfyui/images/` |
| `random_filename` | `True` → timestamp + random suffix filename; `False` → use the `filename` field |
| `filename` | Custom filename (used when `random_filename` is off), e.g. `result.png` |

> **Security tip:** Create a dedicated RAM sub-account with `oss:PutObject` permission scoped to the target bucket. Do not use your root account AccessKey.

### Returned URL format

| Endpoint setting | URL pattern |
|---|---|
| Blank | `https://<bucket>.oss-<region>.aliyuncs.com/<key>` |
| Standard OSS endpoint | Region extracted from endpoint, same pattern above |
| Custom domain / CDN | `https://<custom-domain>/<key>` |

### Reliability

All uploads are retried up to **10 times** with a 3-second delay between attempts before raising an error.

### License

MIT

---

## 中文

一个 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 自定义节点包，用于在工作流中将生成的素材（图片、视频、音频及任意文件）直接上传到**阿里云 OSS**。每个节点上传成功后返回文件的公网 URL，可方便地与 API 调用节点或文本显示节点串联。

### 节点列表

| 节点 | 输入 | 输出 | 说明 |
|---|---|---|---|
| **OSS 图片上传** | `IMAGE` | `url` | 取第一帧编码为 PNG 后上传 |
| **OSS 视频上传** | `VIDEO` | `url` | 自动检测格式后上传视频 |
| **OSS 音频上传** | `AUDIO` | `url` | 编码为 WAV（32 位浮点）后上传 |
| **OSS 文件上传** | `file_path` | `url` | 通过绝对路径上传任意本地文件 |

所有节点位于 **OSS Upload** 分类下。

### 依赖

- Python 包：`alibabacloud_oss_v2`、`numpy`
- **OSS 音频上传**节点额外需要 `scipy`（`pip install scipy`）
- 已开通 OSS 的阿里云账号，及具有相应权限的 RAM AccessKey

### 安装

**通过 ComfyUI Manager**（推荐）：搜索 `ComfyUI-OSS-Upload` 直接安装。

**手动安装：**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/awsl1110/ComfyUI-OSS-Upload.git
cd ComfyUI-OSS-Upload
pip install -r requirements.txt
```

### 参数说明

所有节点共享以下 OSS 连接参数：

| 参数 | 说明 |
|---|---|
| `region` | OSS 地域代码，例如 `cn-hangzhou`、`us-west-1`、`ap-southeast-1` |
| `endpoint` | 自定义 Endpoint，标准 OSS 可留空。VPC 内网访问填 `oss-<region>-internal.aliyuncs.com`，CDN/CNAME 自定义域名直接填域名 |
| `bucket` | OSS Bucket 名称 |
| `access_key_id` | 阿里云 RAM 访问密钥 ID |
| `access_key_secret` | 阿里云 RAM 访问密钥 Secret |
| `oss_path` | Bucket 内的键前缀（目录路径），例如 `comfyui/images/` |
| `random_filename` | `True` → 自动生成带时间戳和随机后缀的文件名；`False` → 使用 `filename` 字段 |
| `filename` | 自定义文件名（`random_filename` 关闭时生效），例如 `result.png` |

> **安全建议：** 创建专用 RAM 子账号，授予仅限目标 Bucket 的 `oss:PutObject` 权限，切勿使用主账号 AccessKey。

### 返回 URL 格式

| Endpoint 设置 | URL 格式 |
|---|---|
| 留空 | `https://<bucket>.oss-<region>.aliyuncs.com/<key>` |
| 标准 OSS Endpoint | 从 Endpoint 提取地域后同上 |
| 自定义域名 / CDN | `https://<自定义域名>/<key>` |

### 上传可靠性

所有上传操作在失败时最多自动重试 **10 次**，每次间隔 3 秒，超出后抛出异常。

### 开源协议

MIT

# AI文献阅读助手 (Paper Reader AI) — 免费使用 DeepSeek 模型

> 用于阅读长文献，并提取出有助于写作时能使用的部分
> **现已默认支持 DeepSeek 免费额度，无需信用卡即可使用！**

## 功能特点

- 支持PDF、TXT、Markdown等格式的文献上传
- 自动分块处理长文献，避免超出AI上下文限制
- 智能提取关键信息：研究问题、方法、核心结论、重要数据
- 生成写作素材卡片：可引用语句、论点支持、方法参考
- 支持批量处理多篇文献
- 提供结构化输出，便于直接用于论文写作
- **🎉 免费使用**：默认接入 DeepSeek 模型，新用户注册即享免费额度

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥（推荐 DeepSeek，免费！）

复制 `.env.example` 为 `.env`，并填入你的API密钥：

```bash
cp .env.example .env
# 编辑 .env 文件
```

#### 推荐方案：DeepSeek（免费额度）

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册账号
2. 新用户注册即赠送 **10 元免费额度**（约 50 万 Token）
3. 在 `.env` 中填入：
   ```
   DEEPSEEK_API_KEY=sk-xxxxxxxx
   ```

#### 备选方案

- **Moonshot (Kimi)**：填入 `MOONSHOT_API_KEY`
- **OpenAI**：填入 `OPENAI_API_KEY`（需海外信用卡，按量付费）
- **本地模型**：通过 `OPENAI_BASE_URL` 配置兼容 OpenAI API 的本地模型

### 3. 使用方式

#### 命令行方式（推荐）

```bash
# 单篇文献分析
python main.py --input paper.pdf --output result.md

# 批量处理文件夹
python main.py --input ./papers/ --output ./results/

# 指定分析深度（brief / detailed / comprehensive）
python main.py --input paper.pdf --mode detailed --output result.md
```

#### 作为Python库使用

```python
from paper_reader import PaperReader

reader = PaperReader()
result = reader.analyze("paper.pdf")
print(result.writing_materials)
```

## 输出示例

分析完成后，会生成包含以下内容的结构化报告：

```markdown
# 文献深度分析报告

> **文献**: xxx
> **文件**: paper.pdf

---

## 1. 文献概览
- 研究主题/问题
- 核心贡献

## 2. 核心论点总结（适合用于文献综述）
- 分点列出，每个论点带简要说明

## 3. 可引用素材（按主题分类）
- 直接可用于引用的句子（带建议的引用位置说明）

## 4. 研究方法参考
- 使用了什么方法
- 适合借鉴到我研究中的方法

## 5. 数据与证据
- 关键实验结果和数据
- 可用于支撑我论点的证据

## 6. 写作应用建议
- 在我的写作中，可以如何使用这篇文献
- 可以与哪些观点形成对比/支撑
- 潜在的批评角度
```

## 项目结构

```
paper-reader-ai/
├── main.py                  # 主入口（CLI）
├── config.py                # 配置管理（默认 DeepSeek）
├── requirements.txt         # 依赖
├── .env.example            # 环境变量示例（推荐 DeepSeek）
├── README.md               # 本文件
├── paper_reader/           # 核心库
│   ├── __init__.py
│   ├── pdf_parser.py       # PDF解析器
│   ├── text_processor.py   # 文本分块与预处理
│   ├── ai_analyzer.py      # AI分析引擎
│   ├── writing_helper.py   # 写作素材整理
│   └── models.py           # 数据模型
└── examples/               # 示例输出
```

## 部署方式

### 方式一：本地使用（最简单，免费）

直接克隆仓库，配置 DeepSeek 免费额度即可使用。

```bash
git clone https://github.com/xiaoming-good/paper-reader-ai.git
cd paper-reader-ai
pip install -r requirements.txt
# 配置 .env 中的 DEEPSEEK_API_KEY
python main.py --input your_paper.pdf
```

### 方式二：部署为Web服务（可选）

项目支持通过 `gradio` 快速搭建Web界面：

```bash
pip install gradio
python web_app.py
# 访问 http://localhost:7860
```

### 方式三：Docker部署

```bash
docker build -t paper-reader .
docker run -v ./papers:/app/papers -e DEEPSEEK_API_KEY=sk-xxx paper-reader
```

## 配置说明

在 `.env` 文件中可配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | **推荐** DeepSeek API密钥 | - |
| `MOONSHOT_API_KEY` | Moonshot API密钥 | - |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `OPENAI_BASE_URL` | 自定义API端点 | `https://api.deepseek.com/v1` |
| `MODEL_NAME` | 模型名称 | `deepseek-chat` |
| `CHUNK_SIZE` | 文本分块大小 | 4000 |
| `CHUNK_OVERLAP` | 分块重叠大小 | 200 |
| `OUTPUT_LANGUAGE` | 输出语言 | zh |

## 费用说明

| 提供商 | 费用 | 说明 |
|--------|------|------|
| **DeepSeek** | **免费额度** | 新用户注册赠送约 50 万 Token，超量后按量付费（价格极低） |
| Moonshot | 按量付费 | 需自行充值 |
| OpenAI | 按量付费 | 需海外信用卡，价格较高 |
| 本地模型 | **完全免费** | 需自行部署，适合有 GPU 的环境 |

> 💡 **建议**：先用 DeepSeek 免费额度体验，超量后再考虑其他方案或充值。

## 开发计划

- [ ] 支持更多文献格式（DOCX、EPUB等）
- [ ] 支持多文献对比分析
- [ ] 支持生成文献综述草稿
- [ ] 支持Zotero等文献管理工具集成
- [ ] 支持自动下载参考文献

## 许可证

MIT License

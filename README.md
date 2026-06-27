# AI文献阅读助手 (Paper Reader AI)

> 用于阅读长文献，并提取出有助于写作时能使用的部分

## 功能特点

- 支持PDF、TXT、Markdown等格式的文献上传
- 自动分块处理长文献，避免超出AI上下文限制
- 智能提取关键信息：研究问题、方法、核心结论、重要数据
- 生成写作素材卡片：可引用语句、论点支持、方法参考
- 支持批量处理多篇文献
- 提供结构化输出，便于直接用于论文写作

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env`，并填入你的API密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

支持的AI模型（配置其一即可）：
- **OpenAI**: `OPENAI_API_KEY`
- **Moonshot (Kimi)**: `MOONSHOT_API_KEY`
- **DeepSeek**: `DEEPSEEK_API_KEY`
- **本地模型**: 支持通过 `OPENAI_BASE_URL` 配置本地兼容OpenAI API的模型

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
# 文献分析：xxx

## 基本信息
- 标题：xxx
- 作者：xxx
- 摘要：xxx

## 核心观点
1. ...
2. ...

## 可引用语句（带页码）
> "..." (p.5)

## 研究方法参考
- 方法：xxx
- 适用场景：xxx

## 数据与证据
- 关键数据：xxx
- 数据来源：xxx

## 对写作的帮助
- 可用于支持论点：xxx
- 可对比的观点：xxx
```

## 项目结构

```
paper-reader-ai/
├── main.py                  # 主入口（CLI）
├── config.py                # 配置管理
├── requirements.txt         # 依赖
├── .env.example            # 环境变量示例
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

### 方式一：本地使用（最简单）

直接克隆仓库，安装依赖即可使用。

```bash
git clone https://github.com/xiaoming-good/paper-reader-ai.git
cd paper-reader-ai
pip install -r requirements.txt
python main.py --input your_paper.pdf
```

### 方式二：部署为Web服务（可选）

项目支持通过 `gradio` 快速搭建Web界面：

```bash
python web_app.py
# 访问 http://localhost:7860
```

### 方式三：Docker部署

```bash
docker build -t paper-reader .
docker run -v ./papers:/app/papers -e OPENAI_API_KEY=xxx paper-reader
```

## 配置说明

在 `.env` 文件中可配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `MOONSHOT_API_KEY` | Moonshot API密钥 | - |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - |
| `OPENAI_BASE_URL` | 自定义API端点 | https://api.openai.com/v1 |
| `MODEL_NAME` | 模型名称 | gpt-4o-mini |
| `CHUNK_SIZE` | 文本分块大小 | 4000 |
| `CHUNK_OVERLAP` | 分块重叠大小 | 200 |
| `OUTPUT_LANGUAGE` | 输出语言 | zh |

## 开发计划

- [ ] 支持更多文献格式（DOCX、EPUB等）
- [ ] 支持多文献对比分析
- [ ] 支持生成文献综述草稿
- [ ] 支持Zotero等文献管理工具集成
- [ ] 支持自动下载参考文献

## 许可证

MIT License

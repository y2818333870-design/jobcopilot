# 🚀 AI 求职副驾驶 (JobCopilot)

基于 AI 的简历分析与求职信生成工具，帮助求职者快速评估简历与岗位的匹配度，并生成定制求职信。

## ✨ 已实现功能

- 📄 **简历输入**：支持粘贴文本或上传 PDF 自动解析
- 🎯 **岗位 JD 输入**：粘贴目标岗位的职位描述
- ✨ **AI 匹配分析**：分析简历与 JD 的匹配度，给出评分、匹配点、差距、优化建议
- 📝 **求职信生成**：基于简历和 JD 生成定制中文求职信
- 📋 **历史记录**：自动保存分析记录，支持查看最近 5 条
- 🎯 **Demo 样例**：一键填入示例数据，快速体验功能

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/y2818333870-design/jobcopilot.git
cd jobcopilot
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key（可选）

**本地开发**：创建 `.env` 文件

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

**Streamlit Cloud 部署**：在 App Settings → Secrets 中配置

```toml
OPENAI_API_KEY="你的 API Key"
OPENAI_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
OPENAI_MODEL="MiMo-V2.5"
```

### 5. 启动

```bash
streamlit run app/main.py
```

浏览器会自动打开 http://localhost:8501

## 📁 项目结构

```
jobcopilot/
├── app/
│   ├── main.py              # Streamlit 主页面
│   ├── config.py            # 配置管理（读取 .env 或 st.secrets）
│   ├── core/
│   │   ├── analyzer.py      # 简历分析（调用 MIMO API）
│   │   ├── cover_letter.py  # 求职信生成（调用 MIMO API）
│   │   └── pdf_parser.py    # PDF 文本提取
│   ├── models/
│   │   └── schemas.py       # Pydantic 数据模型
│   └── storage/
│       └── database.py      # SQLite 数据库操作
├── data/
│   ├── uploads/             # 上传的简历文件
│   └── jobcopilot.db        # SQLite 数据库（自动生成）
├── prompts/                 # Prompt 模板（备用）
├── tests/
│   └── test_resume.pdf      # 测试用 PDF 文件
├── requirements.txt         # Python 依赖
├── pyproject.toml           # 项目配置
└── .env.example             # 环境变量模板
```

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | Python |
| 存储 | SQLite |
| AI | MIMO API（兼容 OpenAI 格式） |
| PDF 解析 | PyMuPDF |
| 数据模型 | Pydantic |

## 🌐 部署到 Streamlit Cloud

1. 推送代码到 GitHub
2. 打开 https://share.streamlit.io
3. 点击 **New app**
4. 选择仓库，Main file path 填 `app/main.py`
5. 点击 **Deploy**
6. 在 App Settings → Secrets 中配置 API Key

## 📝 功能说明

### 简历分析

- 输入简历和 JD 后，点击「✨ 开始分析」
- AI 会分析匹配度（0-100 分），并给出：
  - ✅ 匹配点：简历与岗位的匹配之处
  - ⚠️ 差距/缺口：需要改进的地方
  - 💡 优化建议：具体的改进建议

### 求职信生成

- 输入简历和 JD 后，点击「📝 生成求职信」
- AI 会生成一封 300-400 字的中文求职信
- 可直接复制使用

### 历史记录

- 每次分析会自动保存到本地 SQLite 数据库
- 页面底部显示最近 5 条分析记录
- 点击可展开查看详情

## ⚠️ 限制条件

| 限制 | 说明 |
|------|------|
| PDF 解析 | 仅支持文本型 PDF，不支持扫描件/图片 |
| 中文 PDF | PyMuPDF 对中文提取效果有限 |
| API 依赖 | 需要配置 MIMO API Key 才能使用 AI 功能 |
| 历史记录 | 仅保存最近记录，云端部署可能丢失 |

## 📄 License

MIT

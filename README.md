# 🚀 AI 求职副驾驶 (JobCopilot)

帮你优化简历、生成求职信的 AI 工具。

## ✨ 功能

- 📄 上传简历（PDF/文本）
- 🎯 粘贴目标岗位 JD
- ✨ AI 分析简历与岗位的匹配度
- 📝 一键生成定制求职信
- 📋 历史记录保存

## 🚀 快速开始

### 1. 克隆项目

```bash
cd /mnt/d/Aiwork/project/jobcopilot
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -e .
```

### 4. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 OpenAI API Key
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
│   ├── main.py            # Streamlit 主页面
│   ├── config.py          # 配置管理
│   ├── core/              # 业务逻辑（分析、生成）
│   ├── ai/                # AI 调用封装
│   ├── models/            # 数据模型
│   └── storage/           # 数据库操作
├── data/
│   ├── uploads/           # 上传的简历
│   └── jobcopilot.db      # SQLite 数据库（自动生成）
├── prompts/               # Prompt 模板
├── tests/                 # 测试
├── pyproject.toml         # 依赖配置
└── .env                   # 环境变量（需自行创建）
```

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | Python |
| 存储 | SQLite |
| AI | OpenAI API |
| PDF 解析 | PyMuPDF |

## 📝 开发计划

- [x] 项目骨架
- [ ] 简历解析 (PDF → 文本)
- [ ] AI 匹配分析
- [ ] 求职信生成
- [ ] 历史记录

## 📄 License

MIT

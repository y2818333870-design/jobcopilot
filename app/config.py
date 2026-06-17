"""
配置管理模块
支持两种配置方式：
1. 本地开发：从 .env 文件读取
2. Streamlit Cloud：从 st.secrets 读取
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 尝试加载 .env（本地开发）
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


def get_config(key: str, default: str = "") -> str:
    """
    读取配置，优先级：
    1. 环境变量
    2. st.secrets
    3. 默认值
    """
    # 先检查环境变量
    value = os.getenv(key)
    if value:
        return value

    # 再检查 st.secrets（延迟导入，避免模块级别报错）
    try:
        import streamlit as st
        # st.secrets 类似字典，但需要用 .get() 方法
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass

    return default


# ==================== AI 配置 ====================
OPENAI_API_KEY: str = get_config("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = get_config("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL: str = get_config("OPENAI_MODEL", "gpt-4o-mini")

# ==================== 路径配置 ====================
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "jobcopilot.db"
PROMPTS_DIR = BASE_DIR / "prompts"

# 确保目录存在
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

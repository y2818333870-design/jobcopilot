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


def _read_secrets(key: str):
    """从 st.secrets 读取配置"""
    try:
        import streamlit as st
        return st.secrets.get(key)
    except Exception:
        return None


def get_api_key() -> str:
    """获取 API Key"""
    return os.getenv("OPENAI_API_KEY") or _read_secrets("OPENAI_API_KEY") or ""


def get_base_url() -> str:
    """获取 API Base URL"""
    return os.getenv("OPENAI_BASE_URL") or _read_secrets("OPENAI_BASE_URL") or "https://api.openai.com/v1"


def get_model() -> str:
    """获取模型名称"""
    model = os.getenv("OPENAI_MODEL") or _read_secrets("OPENAI_MODEL") or "gpt-4o-mini"
    # MIMO API 可能需要小写模型名称
    return model.lower() if model.startswith("MiMo") else model


# ==================== 路径配置 ====================
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "jobcopilot.db"
PROMPTS_DIR = BASE_DIR / "prompts"

# 确保目录存在
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

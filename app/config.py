"""
配置管理模块
从 .env 文件读取配置，统一管理
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env
load_dotenv(BASE_DIR / ".env")

# ==================== AI 配置 ====================
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ==================== 路径配置 ====================
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "jobcopilot.db"
PROMPTS_DIR = BASE_DIR / "prompts"

# 确保目录存在
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

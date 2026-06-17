"""
数据库初始化模块
使用 SQLite，零配置
"""

import sqlite3
from app.config import DB_PATH, DATA_DIR


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    # 确保目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # 返回字典格式
    return conn


def init_db():
    """初始化数据库表"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 分析记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT NOT NULL,           -- 岗位名称
                jd_text TEXT NOT NULL,             -- 职位描述原文
                resume_text TEXT NOT NULL,         -- 简历内容
                match_score REAL,                  -- 匹配度评分 (0-100)
                suggestions TEXT,                  -- AI 优化建议 (JSON)
                cover_letter TEXT,                 -- 生成的求职信
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
    except Exception as e:
        # 云端环境可能无法写入，不影响主功能
        print(f"数据库初始化警告: {e}")


# 模块导入时自动初始化
init_db()

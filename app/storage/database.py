"""
数据库初始化模块
使用 SQLite，零配置
"""

import sqlite3
import json
from app.config import DB_PATH, DATA_DIR


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    try:
        conn = get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_text TEXT NOT NULL,
                jd_text TEXT NOT NULL,
                match_score REAL,
                summary TEXT,
                match_points TEXT,
                gaps TEXT,
                suggestions TEXT,
                cover_letter TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"数据库初始化警告: {e}")


def save_analysis(resume_text: str, jd_text: str, match_score: float, 
                  summary: str, match_points: list, gaps: list, 
                  suggestions: list, cover_letter: str = None):
    """保存分析记录"""
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO analyses (resume_text, jd_text, match_score, summary, 
                                  match_points, gaps, suggestions, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resume_text, jd_text, match_score, summary,
            json.dumps(match_points, ensure_ascii=False),
            json.dumps(gaps, ensure_ascii=False),
            json.dumps(suggestions, ensure_ascii=False),
            cover_letter
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存分析记录失败: {e}")
        return False


def get_recent_analyses(limit: int = 10) -> list:
    """获取最近的分析记录"""
    try:
        conn = get_connection()
        rows = conn.execute("""
            SELECT id, resume_text, jd_text, match_score, summary, 
                   match_points, gaps, suggestions, cover_letter, created_at
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            for field in ['match_points', 'gaps', 'suggestions']:
                if result[field]:
                    try:
                        result[field] = json.loads(result[field])
                    except:
                        result[field] = []
            results.append(result)
        return results
    except Exception as e:
        print(f"查询历史记录失败: {e}")
        return []


# 模块导入时自动初始化
init_db()

"""
数据库初始化模块
使用 SQLite，零配置
"""

import sqlite3
import json
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
                resume_text TEXT NOT NULL,         -- 简历内容
                jd_text TEXT NOT NULL,             -- 职位描述原文
                match_score REAL,                  -- 匹配度评分 (0-100)
                summary TEXT,                      -- 总体评价
                match_points TEXT,                 -- 匹配点 (JSON)
                gaps TEXT,                         -- 差距 (JSON)
                suggestions TEXT,                  -- 优化建议 (JSON)
                cover_letter TEXT,                 -- 生成的求职信
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
    except Exception as e:
        # 云端环境可能无法写入，不影响主功能
        print(f"数据库初始化警告: {e}")


def save_analysis(resume_text: str, jd_text: str, match_score: float, 
                  summary: str, match_points: list, gaps: list, 
                  suggestions: list, cover_letter: str = None):
    """保存分析记录"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analyses (resume_text, jd_text, match_score, summary, 
                                  match_points, gaps, suggestions, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resume_text,
            jd_text,
            match_score,
            summary,
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, resume_text, jd_text, match_score, summary, 
                   match_points, gaps, suggestions, cover_letter, created_at
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        results = []
        for row in rows:
            result = dict(row)
            # 解析 JSON 字段
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

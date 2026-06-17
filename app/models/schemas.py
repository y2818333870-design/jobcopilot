"""
数据模型定义
使用 Pydantic 做数据校验
"""

from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    """分析请求"""
    resume_text: str       # 简历内容
    jd_text: str           # 岗位 JD
    job_title: str = ""    # 岗位名称（可选）


class MatchPoint(BaseModel):
    """匹配点"""
    title: str             # 匹配点标题
    description: str       # 说明


class GapItem(BaseModel):
    """差距/缺口"""
    title: str             # 缺口标题
    description: str       # 说明
    severity: str = "medium"  # 严重程度: low/medium/high


class Suggestion(BaseModel):
    """优化建议"""
    category: str          # 分类：技能/经历/格式/关键词
    content: str           # 具体建议


class AnalysisResult(BaseModel):
    """分析结果"""
    match_score: int       # 匹配度评分 0-100
    summary: str           # 总体评价
    match_points: list[MatchPoint]   # 匹配点列表
    gaps: list[GapItem]              # 差距列表
    suggestions: list[Suggestion]    # 优化建议列表

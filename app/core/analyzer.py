"""
简历分析模块
接入 MIMO API 进行真实 AI 分析
"""

import json
import streamlit as st
from openai import OpenAI
from app.config import get_api_key, get_base_url, get_model
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResult,
    MatchPoint,
    GapItem,
    Suggestion,
)
from app.storage.database import save_analysis

# Prompt 模板
ANALYZE_PROMPT = """你是一位资深的求职顾问。请分析以下简历与目标岗位的匹配程度。

## 目标岗位 JD
{jd}

## 应聘者简历
{resume}

## 请以 JSON 格式输出以下内容：

{{
  "match_score": 0-100的整数评分,
  "summary": "一句话总体评价",
  "match_points": [
    {{"title": "匹配点标题", "description": "说明"}},
    ...
  ],
  "gaps": [
    {{"title": "缺口标题", "description": "说明", "severity": "high/medium/low"}},
    ...
  ],
  "suggestions": [
    {{"category": "技能/经历/格式/关键词", "content": "具体建议"}},
    ...
  ]
}}

要求：
1. match_points 最多 5 条
2. gaps 最多 5 条
3. suggestions 最多 5 条
4. 用中文回答
5. 只输出 JSON，不要其他内容
"""


def analyze_resume(request: AnalysisRequest) -> tuple[AnalysisResult, dict]:
    """
    分析简历与岗位的匹配度
    调用 MIMO API 进行真实分析
    
    返回: (分析结果, 调试信息)
    """
    api_key = get_api_key()
    base_url = get_base_url()
    model = get_model()
    
    debug_info = {
        "api_key_configured": bool(api_key),
        "base_url": base_url,
        "model": model,
        "api_called": False,
        "error": None,
        "is_mock": False,
    }

    # 如果没有配置 API Key，返回 Mock 数据
    if not api_key:
        debug_info["is_mock"] = True
        debug_info["error"] = "未配置 API Key"
        result = _mock_analyze(request)
        # 保存到数据库
        _save_to_db(request, result)
        return result, debug_info

    try:
        # 初始化 OpenAI 客户端（兼容 MIMO API）
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        # 构造 prompt
        prompt = ANALYZE_PROMPT.format(
            jd=request.jd_text,
            resume=request.resume_text,
        )

        # 调用 API
        debug_info["api_called"] = True
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是 MiMo，一个由小米开发的 AI 助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        # 解析响应
        content = response.choices[0].message.content
        result = _parse_response(content)
        # 保存到数据库
        _save_to_db(request, result)
        return result, debug_info

    except Exception as e:
        # API 调用失败，返回错误信息（不 fallback 到 Mock）
        debug_info["is_mock"] = False
        debug_info["error"] = str(e)
        print(f"API 调用失败: {e}")
        
        # 返回一个错误提示结果
        result = AnalysisResult(
            match_score=0,
            summary=f"❌ API 调用失败: {str(e)[:100]}...",
            match_points=[],
            gaps=[],
            suggestions=[],
        )
        return result, debug_info


def _save_to_db(request: AnalysisRequest, result: AnalysisResult):
    """保存分析结果到数据库"""
    try:
        save_analysis(
            resume_text=request.resume_text,
            jd_text=request.jd_text,
            match_score=result.match_score,
            summary=result.summary,
            match_points=[p.model_dump() for p in result.match_points],
            gaps=[g.model_dump() for g in result.gaps],
            suggestions=[s.model_dump() for s in result.suggestions],
        )
    except Exception as e:
        print(f"保存到数据库失败: {e}")


def _parse_response(content: str) -> AnalysisResult:
    """解析 AI 返回的 JSON"""
    try:
        # 尝试提取 JSON（可能被 markdown 包裹）
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        return AnalysisResult(
            match_score=data.get("match_score", 60),
            summary=data.get("summary", "分析完成"),
            match_points=[
                MatchPoint(**p) for p in data.get("match_points", [])
            ],
            gaps=[
                GapItem(**g) for g in data.get("gaps", [])
            ],
            suggestions=[
                Suggestion(**s) for s in data.get("suggestions", [])
            ],
        )
    except Exception as e:
        print(f"JSON 解析失败: {e}")
        print(f"原始内容: {content}")
        # 解析失败，返回默认结果
        return AnalysisResult(
            match_score=50,
            summary="AI 分析完成，但结果解析异常，请重试。",
            match_points=[],
            gaps=[],
            suggestions=[],
        )


def _mock_analyze(request: AnalysisRequest) -> AnalysisResult:
    """Mock 分析（无 API Key 时使用）"""
    resume_len = len(request.resume_text)
    mock_score = min(85, max(55, 60 + (resume_len // 100)))

    return AnalysisResult(
        match_score=mock_score,
        summary="[Mock 模式] 你的简历与目标岗位有一定匹配度，但仍有提升空间。建议针对 JD 中的关键技能进行简历优化。",
        match_points=[
            MatchPoint(title="教育背景匹配", description="你的学历符合岗位要求，专业方向相关。"),
            MatchPoint(title="基础技能覆盖", description="简历中提到了岗位所需的部分核心技术栈。"),
            MatchPoint(title="项目经验相关", description="有 1-2 个项目经历与目标岗位职责相关。"),
        ],
        gaps=[
            GapItem(title="缺少量化成果", description="简历中缺少用数据量化的成果描述，建议补充具体数字。", severity="high"),
            GapItem(title="关键词覆盖不足", description="JD 中的部分关键词在简历中未体现。", severity="medium"),
            GapItem(title="技能深度待加强", description="部分技能仅列出名称，缺少深度描述。", severity="low"),
        ],
        suggestions=[
            Suggestion(category="经历", content="用 STAR 法则重写项目经历：情境(Situation)、任务(Task)、行动(Action)、结果(Result)。"),
            Suggestion(category="关键词", content="在简历中自然融入 JD 里的关键词，如技术栈名称、业务术语等。"),
            Suggestion(category="格式", content="确保简历排版清晰，重点内容放在页面上半部分。"),
            Suggestion(category="技能", content="将技能分为「精通/熟练/了解」三个层次，突出与岗位匹配的核心技能。"),
        ],
    )

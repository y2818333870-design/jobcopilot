"""
简历分析模块
接入 MIMO API 进行真实 AI 分析
"""

import json
import re
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

ANALYZE_PROMPT = """你是一位资深的求职顾问。请分析以下简历与目标岗位的匹配程度。

## 目标岗位 JD
{jd}

## 应聘者简历
{resume}

## 请严格以 JSON 格式输出，不要添加任何其他文字：

{{
  "match_score": 75,
  "summary": "一句话总体评价",
  "match_points": [
    {{"title": "匹配点标题", "description": "说明"}}
  ],
  "gaps": [
    {{"title": "缺口标题", "description": "说明", "severity": "high"}}
  ],
  "suggestions": [
    {{"category": "技能", "content": "具体建议"}}
  ]
}}

注意：只输出 JSON，不要输出其他任何文字。"""


def analyze_resume(request: AnalysisRequest) -> tuple[AnalysisResult, dict]:
    """分析简历与岗位的匹配度"""
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

    if not api_key:
        debug_info["is_mock"] = True
        debug_info["error"] = "未配置 API Key"
        result = _mock_analyze(request)
        _save_to_db(request, result)
        return result, debug_info

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        prompt = ANALYZE_PROMPT.format(jd=request.jd_text, resume=request.resume_text)
        
        debug_info["api_called"] = True
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是 MiMo，一个由小米开发的 AI 助手。请严格只输出 JSON。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        content = response.choices[0].message.content
        print(f"API 返回内容: {content[:300]}...")
        
        result = _parse_response(content)
        _save_to_db(request, result)
        return result, debug_info

    except Exception as e:
        debug_info["is_mock"] = False
        debug_info["error"] = str(e)
        print(f"API 调用失败: {e}")
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
    """解析 AI 返回的 JSON（增强容错）"""
    try:
        # 1. 尝试直接解析
        try:
            data = json.loads(content.strip())
            return _build_result(data)
        except json.JSONDecodeError:
            pass
        
        # 2. 提取 markdown 包裹的 JSON
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{[^{}]*"match_score"[^{}]*\}',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    data = json.loads(json_str.strip())
                    return _build_result(data)
                except (json.JSONDecodeError, IndexError):
                    continue
        
        # 3. 尝试找到第一个 { 和最后一个 }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(content[start:end+1])
                return _build_result(data)
            except json.JSONDecodeError:
                pass
        
        # 4. 所有方法都失败，返回默认结果
        print(f"JSON 解析失败，原始内容: {content[:500]}...")
        return AnalysisResult(
            match_score=50,
            summary="AI 分析完成，但结果解析异常，请重试。",
            match_points=[],
            gaps=[],
            suggestions=[],
        )
        
    except Exception as e:
        print(f"解析响应失败: {e}")
        return AnalysisResult(
            match_score=50,
            summary="AI 分析完成，但结果解析异常，请重试。",
            match_points=[],
            gaps=[],
            suggestions=[],
        )


def _build_result(data: dict) -> AnalysisResult:
    """从字典构建 AnalysisResult"""
    return AnalysisResult(
        match_score=data.get("match_score", 60),
        summary=data.get("summary", "分析完成"),
        match_points=[MatchPoint(**p) for p in data.get("match_points", [])],
        gaps=[GapItem(**g) for g in data.get("gaps", [])],
        suggestions=[Suggestion(**s) for s in data.get("suggestions", [])],
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

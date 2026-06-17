"""
简历分析模块
当前使用 Mock 实现，后续替换为真实 AI 调用
"""

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResult,
    MatchPoint,
    GapItem,
    Suggestion,
)


def analyze_resume(request: AnalysisRequest) -> AnalysisResult:
    """
    分析简历与岗位的匹配度
    当前返回 Mock 数据，后续接入 AI
    """
    # 简单计算一个 mock 评分（基于文本长度）
    resume_len = len(request.resume_text)
    jd_len = len(request.jd_text)
    mock_score = min(85, max(55, 60 + (resume_len // 100)))

    return AnalysisResult(
        match_score=mock_score,
        summary="你的简历与目标岗位有一定匹配度，但仍有提升空间。建议针对 JD 中的关键技能进行简历优化。",
        match_points=[
            MatchPoint(
                title="教育背景匹配",
                description="你的学历符合岗位要求，专业方向相关。"
            ),
            MatchPoint(
                title="基础技能覆盖",
                description="简历中提到了岗位所需的部分核心技术栈。"
            ),
            MatchPoint(
                title="项目经验相关",
                description="有 1-2 个项目经历与目标岗位职责相关。"
            ),
        ],
        gaps=[
            GapItem(
                title="缺少量化成果",
                description="简历中缺少用数据量化的成果描述，建议补充具体数字。",
                severity="high"
            ),
            GapItem(
                title="关键词覆盖不足",
                description="JD 中的部分关键词在简历中未体现。",
                severity="medium"
            ),
            GapItem(
                title="技能深度待加强",
                description="部分技能仅列出名称，缺少深度描述。",
                severity="low"
            ),
        ],
        suggestions=[
            Suggestion(
                category="经历",
                content="用 STAR 法则重写项目经历：情境(Situation)、任务(Task)、行动(Action)、结果(Result)。"
            ),
            Suggestion(
                category="关键词",
                content="在简历中自然融入 JD 里的关键词，如技术栈名称、业务术语等。"
            ),
            Suggestion(
                category="格式",
                content="确保简历排版清晰，重点内容放在页面上半部分。"
            ),
            Suggestion(
                category="技能",
                content="将技能分为「精通/熟练/了解」三个层次，突出与岗位匹配的核心技能。"
            ),
        ],
    )

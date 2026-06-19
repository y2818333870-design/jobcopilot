"""
AI 求职副驾驶 - Streamlit 主页面
运行命令: streamlit run app/main.py
"""

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
# 原因：streamlit run app/main.py 时，工作目录会变成 app/，导致 import app 失败
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.config import get_api_key, get_model
from app.models.schemas import AnalysisRequest
from app.core.analyzer import analyze_resume
from app.core.cover_letter import generate_cover_letter

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="AI 求职副驾驶",
    page_icon="🚀",
    layout="wide",
)

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("🚀 AI 求职副驾驶")
    st.markdown("---")
    st.markdown("### 功能")
    st.markdown("- 📄 输入简历")
    st.markdown("- 🎯 粘贴岗位 JD")
    st.markdown("- ✨ AI 匹配分析")
    st.markdown("- 📝 生成求职信")
    st.markdown("---")

    # API 状态检查（运行时读取）
    api_key = get_api_key()
    model_name = get_model()

    if api_key:
        st.success("✅ API Key 已配置")
    else:
        st.warning("⚠️ 未配置 API Key（当前使用 Mock 模式）")
        st.caption("配置后将使用真实 AI 分析")

    st.caption(f"模型: {model_name}")

# ==================== 主页面 ====================
st.title("📄 AI 求职副驾驶")
st.markdown("**输入简历 + 粘贴 JD = 获取匹配分析和优化建议**")

# 两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 你的简历")
    resume_text = st.text_area(
        "粘贴简历内容",
        height=250,
        placeholder="在这里粘贴你的简历内容...\n\n示例：\n张三\n北京大学 计算机科学与技术 本科\n熟悉 Python、Java，有 2 段实习经历...",
        key="resume_input"
    )

with col2:
    st.subheader("🎯 目标岗位 JD")
    jd_text = st.text_area(
        "粘贴职位描述",
        height=250,
        placeholder="在这里粘贴目标岗位的职位描述...\n\n示例：\n岗位：后端开发工程师\n要求：\n1. 熟悉 Python/Java\n2. 了解数据库\n3. 良好的沟通能力...",
        key="jd_input"
    )

st.markdown("---")

# ==================== 操作按钮 ====================
col_btn1, col_btn2, col_space = st.columns([1, 1, 2])

with col_btn1:
    analyze_btn = st.button("✨ 开始分析", type="primary", use_container_width=True)

with col_btn2:
    letter_btn = st.button("📝 生成求职信", use_container_width=True)

# ==================== 分析结果展示 ====================
if analyze_btn:
    # 输入校验
    if not jd_text or not jd_text.strip():
        st.warning("⚠️ 请先粘贴目标岗位的 JD")
    elif not resume_text or not resume_text.strip():
        st.warning("⚠️ 请先粘贴简历内容")
    else:
        # 构造请求
        request = AnalysisRequest(
            resume_text=resume_text.strip(),
            jd_text=jd_text.strip(),
        )

        # 调用分析
        with st.spinner("正在分析中..."):
            result, debug_info = analyze_resume(request)

        # 显示调试信息
        if debug_info.get("is_mock"):
            st.warning("⚠️ **当前使用 Mock 模式**（非真实 AI 分析）")
            if debug_info.get("error"):
                st.error(f"错误原因: {debug_info['error']}")
        else:
            st.success("✅ **已调用 MIMO API 进行真实 AI 分析**")

        # 展示结果
        st.markdown("---")
        st.subheader("📊 分析结果")

        # 匹配度评分
        score = result.match_score
        if score >= 80:
            score_color = "🟢"
            score_label = "高度匹配"
        elif score >= 60:
            score_color = "🟡"
            score_label = "中等匹配"
        else:
            score_color = "🔴"
            score_label = "匹配度较低"

        col_score, col_summary = st.columns([1, 3])
        with col_score:
            st.metric("匹配度", f"{score_color} {score}分", score_label)
        with col_summary:
            st.info(f"**总体评价：** {result.summary}")

        # 三列展示：匹配点 / 差距 / 建议
        st.markdown("---")
        col_match, col_gap, col_suggest = st.columns(3)

        # 匹配点
        with col_match:
            st.markdown("### ✅ 匹配点")
            for i, point in enumerate(result.match_points, 1):
                st.markdown(f"**{i}. {point.title}**")
                st.caption(point.description)

        # 差距
        with col_gap:
            st.markdown("### ⚠️ 差距/缺口")
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            for gap in result.gaps:
                icon = severity_icon.get(gap.severity, "⚪")
                st.markdown(f"**{icon} {gap.title}**")
                st.caption(gap.description)

        # 优化建议
        with col_suggest:
            st.markdown("### 💡 优化建议")
            for i, sug in enumerate(result.suggestions, 1):
                st.markdown(f"**{i}. [{sug.category}]**")
                st.caption(sug.content)

# ==================== 求职信生成 ====================
if letter_btn:
    if not jd_text or not jd_text.strip():
        st.warning("⚠️ 请先粘贴目标岗位的 JD")
    elif not resume_text or not resume_text.strip():
        st.warning("⚠️ 请先粘贴简历内容")
    else:
        # 调用求职信生成
        with st.spinner("正在生成求职信..."):
            cover_letter, debug_info = generate_cover_letter(
                resume_text.strip(),
                jd_text.strip()
            )

        # 显示调试信息
        if debug_info.get("error"):
            st.warning(f"⚠️ {debug_info['error']}")
        elif debug_info.get("api_called"):
            st.success("✅ **已调用 MIMO API 生成求职信**")

        # 展示求职信
        st.markdown("---")
        st.subheader("📝 生成的求职信")
        st.markdown(cover_letter)

        # 复制按钮
        st.code(cover_letter, language=None)

# ==================== 页脚 ====================
st.markdown("---")
st.caption("JobCopilot v0.1.0 | AI 求职副驾驶")

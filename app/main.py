"""
AI 求职副驾驶 - Streamlit 主页面
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.config import get_api_key, get_model
from app.models.schemas import AnalysisRequest
from app.core.analyzer import analyze_resume
from app.core.cover_letter import generate_cover_letter
from app.core.pdf_parser import extract_text_from_pdf
from app.storage.database import get_recent_analyses

DEMO_RESUME = "张三\n北京大学 计算机科学与技术 本科\nGPA: 3.8/4.0\n\n技能：Python, Java, SQL, Git, Docker\n\n实习经历：\n1. 字节跳动 后端开发实习生 (2024.06-2024.09)\n   - 负责推荐系统后端开发，使用 Python + FastAPI\n   - 优化数据库查询，QPS 提升 30%\n\n2. 阿里云 开发实习生 (2023.12-2024.03)\n   - 参与微服务架构设计，使用 Java + Spring Boot\n   - 编写单元测试，代码覆盖率达到 85%"

DEMO_JD = "岗位：后端开发工程师\n公司：某互联网公司\n\n要求：\n1. 计算机相关专业本科及以上\n2. 熟悉 Python 或 Java\n3. 了解数据库\n4. 有实习经验优先"

st.set_page_config(page_title="AI 求职副驾驶", page_icon="🚀", layout="wide")

# 初始化
if "resume" not in st.session_state:
    st.session_state.resume = ""
if "jd" not in st.session_state:
    st.session_state.jd = ""

# 侧边栏
with st.sidebar:
    st.title("🚀 AI 求职副驾驶")
    st.markdown("---")
    if get_api_key():
        st.success("✅ API Key 已配置")
    else:
        st.warning("⚠️ Mock 模式（无 API Key）")
    st.caption(f"模型: {get_model()}")

st.title("📄 AI 求职副驾驶")

# Demo 按钮
c1, c2, _ = st.columns([1, 1, 2])
if c1.button("🎯 一键填入示例"):
    st.session_state.resume = DEMO_RESUME
    st.session_state.jd = DEMO_JD
    st.rerun()
if c2.button("🗑️ 清空"):
    st.session_state.resume = ""
    st.session_state.jd = ""
    st.rerun()

# 输入框（使用 key）
col1, col2 = st.columns(2)
with col1:
    st.text_area("📄 简历", height=200, key="resume")
with col2:
    st.text_area("🎯 JD", height=200, key="jd")

# 按钮
btn1, btn2, _ = st.columns([1, 1, 2])
analyze_clicked = btn1.button("✨ 开始分析", type="primary")
letter_clicked = btn2.button("📝 生成求职信")

# 分析
if analyze_clicked:
    resume = st.session_state.resume
    jd = st.session_state.jd
    if resume and resume.strip() and jd and jd.strip():
        result, _ = analyze_resume(AnalysisRequest(resume_text=resume.strip(), jd_text=jd.strip()))
        st.session_state.result = result
    else:
        st.warning("⚠️ 请填写简历和 JD")

# 求职信
if letter_clicked:
    resume = st.session_state.resume
    jd = st.session_state.jd
    if resume and resume.strip() and jd and jd.strip():
        letter, _ = generate_cover_letter(resume.strip(), jd.strip())
        st.session_state.letter = letter
    else:
        st.warning("⚠️ 请填写简历和 JD")

# 显示分析结果
if "result" in st.session_state and st.session_state.result:
    r = st.session_state.result
    st.markdown("---")
    st.subheader("📊 分析结果")
    score = r.match_score
    label = "🟢 高度匹配" if score >= 80 else ("🟡 中等匹配" if score >= 60 else "🔴 匹配度较低")
    st.metric("匹配度", f"{score}分")
    st.markdown(f"**{label}**")
    st.info(f"**总体评价：** {r.summary}")
    col_m, col_g, col_s = st.columns(3)
    with col_m:
        st.markdown("### ✅ 匹配点")
        for p in r.match_points:
            st.markdown(f"- **{p.title}**: {p.description}")
    with col_g:
        st.markdown("### ⚠️ 差距")
        for g in r.gaps:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(g.severity, "⚪")
            st.markdown(f"- {icon} **{g.title}**: {g.description}")
    with col_s:
        st.markdown("### 💡 建议")
        for s in r.suggestions:
            st.markdown(f"- [{s.category}] {s.content}")

# 显示求职信
if "letter" in st.session_state and st.session_state.letter:
    st.markdown("---")
    st.subheader("📝 求职信")
    st.markdown(st.session_state.letter)

# 历史记录
st.markdown("---")
st.subheader("📋 历史记录")
try:
    for r in get_recent_analyses(5):
        st.markdown(f"- **{r['match_score']}分** | {r['resume_text'][:50]}... | {r['created_at'][:16]}")
except Exception as e:
    st.error(f"加载历史记录失败: {e}")

st.caption("JobCopilot v0.1.0")

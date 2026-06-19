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
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "result_data" not in st.session_state:
    st.session_state.result_data = None

# 侧边栏
with st.sidebar:
    st.title("🚀 AI 求职副驾驶")
    st.markdown("---")
    api_key = get_api_key()
    if api_key:
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
    st.session_state.show_result = False
    st.rerun()
if c2.button("🗑️ 清空"):
    st.session_state.resume = ""
    st.session_state.jd = ""
    st.session_state.show_result = False
    st.rerun()

# PDF 上传
uploaded = st.file_uploader("上传 PDF 简历", type=["pdf"])
if uploaded:
    text = extract_text_from_pdf(uploaded)
    if text and len(text.strip()) >= 10:
        st.session_state.resume = text
        st.success(f"✅ PDF 解析成功 ({len(text)} 字)")
        st.rerun()
    else:
        st.warning("⚠️ PDF 解析失败")

# 输入框 - 使用 key 让 Streamlit 自动管理状态
col1, col2 = st.columns(2)
with col1:
    st.text_area("📄 简历", height=200, key="resume")
with col2:
    st.text_area("🎯 JD", height=200, key="jd")

# 按钮
btn1, btn2, _ = st.columns([1, 1, 2])

# 分析按钮回调
def do_analysis():
    resume = st.session_state.resume
    jd = st.session_state.jd
    if not resume or not resume.strip():
        st.session_state.result_data = {"error": "请填写简历"}
        return
    if not jd or not jd.strip():
        st.session_state.result_data = {"error": "请填写 JD"}
        return
    with st.spinner("🤖 AI 分析中..."):
        result, info = analyze_resume(
            AnalysisRequest(resume_text=resume.strip(), jd_text=jd.strip())
        )
    st.session_state.result_data = {
        "score": result.match_score,
        "summary": result.summary,
        "points": [(p.title, p.description) for p in result.match_points],
        "gaps": [(g.title, g.description, g.severity) for g in result.gaps],
        "sugs": [(s.category, s.content) for s in result.suggestions],
    }
    st.session_state.show_result = True

# 求职信按钮回调
def do_letter():
    resume = st.session_state.resume
    jd = st.session_state.jd
    if not resume or not resume.strip():
        st.session_state.result_data = {"error": "请填写简历"}
        return
    if not jd or not jd.strip():
        st.session_state.result_data = {"error": "请填写 JD"}
        return
    with st.spinner("✍️ 生成中..."):
        letter, info = generate_cover_letter(resume.strip(), jd.strip())
    st.session_state.result_data = {"letter": letter}
    st.session_state.show_result = True

btn1.button("✨ 开始分析", type="primary", on_click=do_analysis, use_container_width=True)
btn2.button("📝 生成求职信", on_click=do_letter, use_container_width=True)

# 显示结果
if st.session_state.show_result and st.session_state.result_data:
    data = st.session_state.result_data
    
    if "error" in data:
        st.warning(f"⚠️ {data['error']}")
    elif "letter" in data:
        st.markdown("---")
        st.subheader("📝 求职信")
        st.markdown(data["letter"])
        st.code(data["letter"], language=None)
    else:
        st.markdown("---")
        st.subheader("📊 分析结果")
        
        score = data["score"]
        label = "高度匹配" if score >= 80 else ("中等匹配" if score >= 60 else "匹配度较低")
        st.metric("匹配度", f"{score}分", label)
        st.info(f"**总体评价：** {data['summary']}")
        
        col_m, col_g, col_s = st.columns(3)
        with col_m:
            st.markdown("### ✅ 匹配点")
            for title, desc in data["points"]:
                st.markdown(f"- **{title}**: {desc}")
        with col_g:
            st.markdown("### ⚠️ 差距")
            for title, desc, sev in data["gaps"]:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")
                st.markdown(f"- {icon} **{title}**: {desc}")
        with col_s:
            st.markdown("### 💡 建议")
            for cat, content in data["sugs"]:
                st.markdown(f"- [{cat}] {content}")

# 历史记录
st.markdown("---")
st.subheader("📋 历史记录")
for r in get_recent_analyses(5):
    st.markdown(f"- **{r['match_score']}分** | {r['resume_text'][:50]}... | {r['created_at'][:16]}")

st.caption("JobCopilot v0.1.0")

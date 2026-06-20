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
from app.core.docx_parser import extract_text_from_docx
from app.storage.database import get_recent_analyses

# ==================== 常量 ====================
DEMO_RESUME = """张三
北京大学 计算机科学与技术 本科
GPA: 3.8/4.0

技能：Python, Java, SQL, Git, Docker

实习经历：
1. 字节跳动 后端开发实习生 (2024.06-2024.09)
   - 负责推荐系统后端开发，使用 Python + FastAPI
   - 优化数据库查询，QPS 提升 30%

2. 阿里云 开发实习生 (2023.12-2024.03)
   - 参与微服务架构设计，使用 Java + Spring Boot
   - 编写单元测试，代码覆盖率达到 85%"""

DEMO_JD = """岗位：后端开发工程师
公司：某互联网公司

要求：
1. 计算机相关专业本科及以上
2. 熟悉 Python 或 Java
3. 了解数据库
4. 有实习经验优先"""

# 最小字数限制
MIN_RESUME_LEN = 50
MIN_JD_LEN = 20

# ==================== 页面配置 ====================
st.set_page_config(page_title="AI 求职副驾驶", page_icon="🚀", layout="wide")

# ==================== 初始化 session_state ====================
if "resume" not in st.session_state:
    st.session_state.resume = ""
if "jd" not in st.session_state:
    st.session_state.jd = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "letter" not in st.session_state:
    st.session_state.letter = None

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("🚀 AI 求职副驾驶")
    st.markdown("---")
    if get_api_key():
        st.success("✅ API Key 已配置")
    else:
        st.warning("⚠️ Mock 模式（无 API Key）")
    st.caption(f"模型: {get_model()}")
    st.markdown("---")
    st.caption("v0.2.0 · 支持 PDF/DOCX 上传")

# ==================== 主页面 ====================
st.title("📄 AI 求职副驾驶")

# Demo 按钮
c1, c2, _ = st.columns([1, 1, 2])
if c1.button("🎯 一键填入示例"):
    st.session_state.resume = DEMO_RESUME
    st.session_state.jd = DEMO_JD
    st.session_state.result = None
    st.session_state.letter = None
    st.rerun()
if c2.button("🗑️ 清空"):
    st.session_state.resume = ""
    st.session_state.jd = ""
    st.session_state.result = None
    st.session_state.letter = None
    st.rerun()

# ==================== 文件上传（支持 PDF + DOCX） ====================
st.markdown("#### 📎 上传简历文件（可选）")
uploaded = st.file_uploader(
    "支持 PDF 和 Word (.docx) 格式",
    type=["pdf", "docx"],
    help="上传后自动提取文本，也可手动粘贴简历内容"
)

if uploaded:
    file_type = uploaded.name.split(".")[-1].lower()
    
    with st.spinner(f"正在解析 {uploaded.name}..."):
        if file_type == "pdf":
            text = extract_text_from_pdf(uploaded)
        elif file_type == "docx":
            text = extract_text_from_docx(uploaded)
        else:
            text = ""
            st.error("❌ 不支持的文件格式")
    
    # 检查解析结果
    if text and not text.startswith("❌") and len(text.strip()) >= MIN_RESUME_LEN:
        st.session_state.resume = text
        st.success(f"✅ PDF 解析成功，共提取 {len(text)} 个字符")
        st.rerun()
    elif text and text.startswith("❌"):
        st.error(text)
    else:
        st.warning(f"⚠️ 解析内容过少（{len(text.strip()) if text else 0} 字符），请手动粘贴简历")

# ==================== 输入框 ====================
col1, col2 = st.columns(2)
with col1:
    st.text_area("📄 简历", height=200, key="resume",
                 placeholder="粘贴简历内容，或上传文件自动填入...")
with col2:
    st.text_area("🎯 岗位 JD", height=200, key="jd",
                 placeholder="粘贴目标岗位的职位描述...")

# ==================== 输入验证函数 ====================
def validate_input(resume: str, jd: str) -> tuple[bool, str]:
    """验证输入是否有效"""
    if not resume or not resume.strip():
        return False, "⚠️ 请填写或上传简历"
    if not jd or not jd.strip():
        return False, "⚠️ 请填写岗位 JD"
    if len(resume.strip()) < MIN_RESUME_LEN:
        return False, f"⚠️ 简历内容过短（{len(resume.strip())} 字），至少需要 {MIN_RESUME_LEN} 字"
    if len(jd.strip()) < MIN_JD_LEN:
        return False, f"⚠️ JD 内容过短（{len(jd.strip())} 字），至少需要 {MIN_JD_LEN} 字"
    return True, ""

# ==================== 按钮 ====================
btn1, btn2, _ = st.columns([1, 1, 2])
analyze_clicked = btn1.button("✨ 开始分析", type="primary")
letter_clicked = btn2.button("📝 生成求职信")

# ==================== 分析逻辑 ====================
if analyze_clicked:
    resume = st.session_state.resume
    jd = st.session_state.jd
    valid, msg = validate_input(resume, jd)
    
    if not valid:
        st.warning(msg)
    else:
        with st.spinner("🔄 正在分析简历与岗位匹配度..."):
            try:
                result, debug_info = analyze_resume(
                    AnalysisRequest(resume_text=resume.strip(), jd_text=jd.strip())
                )
                st.session_state.result = result
            except Exception as e:
                st.error(f"❌ 分析失败: {e}")

# ==================== 求职信逻辑 ====================
if letter_clicked:
    resume = st.session_state.resume
    jd = st.session_state.jd
    valid, msg = validate_input(resume, jd)
    
    if not valid:
        st.warning(msg)
    else:
        with st.spinner("🔄 正在生成求职信..."):
            try:
                letter, debug_info = generate_cover_letter(resume.strip(), jd.strip())
                st.session_state.letter = letter
            except Exception as e:
                st.error(f"❌ 生成失败: {e}")

# ==================== 显示分析结果 ====================
if st.session_state.result:
    r = st.session_state.result
    st.markdown("---")
    st.subheader("📊 分析结果")
    
    # 匹配度分数
    score = r.match_score
    label = "🟢 高度匹配" if score >= 80 else ("🟡 中等匹配" if score >= 60 else "🔴 匹配度较低")
    st.metric("匹配度", f"{score}分")
    st.markdown(f"**{label}**")
    
    # 总体评价
    st.info(f"**总体评价：** {r.summary}")
    
    # 匹配点、差距、建议（三列）
    col_m, col_g, col_s = st.columns(3)
    
    with col_m:
        st.markdown("### ✅ 核心匹配点")
        if r.match_points:
            for p in r.match_points:
                st.markdown(f"- **{p.title}**: {p.description}")
        else:
            st.caption("暂无")
    
    with col_g:
        st.markdown("### ⚠️ 明显差距")
        if r.gaps:
            for g in r.gaps:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(g.severity, "⚪")
                st.markdown(f"- {icon} **{g.title}**: {g.description}")
        else:
            st.caption("暂无")
    
    with col_s:
        st.markdown("### 💡 优化建议")
        if r.suggestions:
            for s in r.suggestions:
                st.markdown(f"- [{s.category}] {s.content}")
        else:
            st.caption("暂无")

# ==================== 显示求职信 ====================
if st.session_state.letter:
    st.markdown("---")
    st.subheader("📝 求职信")
    st.markdown(st.session_state.letter)
    
    # 一键复制按钮
    st.code(st.session_state.letter, language=None)

# ==================== 历史记录 ====================
st.markdown("---")
st.subheader("📋 历史记录")
try:
    records = get_recent_analyses(5)
    if records:
        for r in records:
            score = r.get('match_score', 0)
            emoji = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
            resume_preview = r.get('resume_text', '')[:30]
            created = r.get('created_at', '')[:16]
            st.markdown(f"- {emoji} **{score}分** | {resume_preview}... | {created}")
    else:
        st.caption("暂无历史记录")
except Exception as e:
    st.error(f"加载历史记录失败: {e}")

st.caption("JobCopilot v0.2.0")

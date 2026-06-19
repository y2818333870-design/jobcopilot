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
from app.core.pdf_parser import extract_text_from_pdf
from app.storage.database import get_recent_analyses

# ==================== Demo 数据 ====================
DEMO_RESUME = """张三
北京大学 计算机科学与技术 本科
GPA: 3.8/4.0

技能：Python, Java, SQL, Git, Docker, FastAPI, Spring Boot

实习经历：
1. 字节跳动 后端开发实习生 (2024.06-2024.09)
   - 负责推荐系统后端开发，使用 Python + FastAPI
   - 优化数据库查询，QPS 提升 30%
   - 参与设计分布式缓存方案

2. 阿里云 开发实习生 (2023.12-2024.03)
   - 参与微服务架构设计，使用 Java + Spring Boot
   - 编写单元测试，代码覆盖率达到 85%

项目经验：
1. 在线商城系统
   - 技术栈：Python + Django + MySQL + Redis
   - 支持 1000+ 并发用户，日均订单 5000+
"""

DEMO_JD = """岗位：后端开发工程师
公司：某互联网公司

职责：
1. 负责公司核心业务系统的后端开发与维护
2. 参与系统架构设计和技术方案评审
3. 编写高质量代码，确保系统稳定性和可扩展性

要求：
1. 计算机相关专业本科及以上学历
2. 熟悉 Python 或 Java 编程语言
3. 了解 MySQL、Redis 等数据库技术
4. 有实习经验者优先
5. 良好的沟通能力和团队协作精神
6. 了解分布式系统、微服务架构者加分
"""

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
    st.markdown("- 📄 输入简历（支持 PDF 上传）")
    st.markdown("- 🎯 粘贴岗位 JD")
    st.markdown("- ✨ AI 匹配分析")
    st.markdown("- 📝 生成求职信")
    st.markdown("- 📋 历史记录")
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

# Demo 按钮
st.markdown("---")
col_demo1, col_demo2, col_demo3 = st.columns([1, 1, 2])
with col_demo1:
    demo_btn = st.button("🎯 一键填入示例", use_container_width=True, help="点击填入示例简历和 JD，快速体验功能")
with col_demo2:
    clear_btn = st.button("🗑️ 清空输入", use_container_width=True, help="清空所有输入内容")

# 处理 Demo 按钮
if demo_btn:
    st.session_state['resume_input'] = DEMO_RESUME
    st.session_state['jd_input'] = DEMO_JD
    st.rerun()

if clear_btn:
    st.session_state['resume_input'] = ""
    st.session_state['jd_input'] = ""
    st.rerun()

# 两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 你的简历")
    
    # PDF 上传区域
    uploaded_file = st.file_uploader(
        "上传 PDF 简历（可选）",
        type=["pdf"],
        help="上传 PDF 格式的简历，系统会自动提取文字内容"
    )
    
    # 如果上传了 PDF，提取文本
    if uploaded_file is not None:
        with st.spinner("正在解析 PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
        
        if extracted_text and not extracted_text.startswith("❌"):
            # 检查提取的文本是否为空或太短
            if len(extracted_text.strip()) < 10:
                st.warning("⚠️ PDF 解析成功，但提取的文本内容较少。可能是扫描件/图片 PDF，建议手动粘贴简历内容。")
            else:
                st.success(f"✅ PDF 解析成功，共提取 {len(extracted_text)} 个字符")
                # 将提取的文本存入 session state（使用 text_area 的 key）
                st.session_state['resume_input'] = extracted_text
                st.rerun()
        else:
            st.error(f"❌ PDF 解析失败: {extracted_text}")
            st.info("💡 提示：如果是扫描件/图片 PDF，请手动粘贴简历内容。")
    
    # 简历文本输入框
    resume_text = st.text_area(
        "粘贴简历内容（或上传 PDF 后自动填入）",
        height=250,
        placeholder="在这里粘贴你的简历内容...\n\n点击上方「🎯 一键填入示例」快速体验 →",
        key="resume_input"
    )

with col2:
    st.subheader("🎯 目标岗位 JD")
    jd_text = st.text_area(
        "粘贴职位描述",
        height=250,
        placeholder="在这里粘贴目标岗位的职位描述...\n\n点击上方「🎯 一键填入示例」快速体验 →",
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
        st.warning("⚠️ 请先粘贴目标岗位的 JD，或点击「🎯 一键填入示例」快速体验")
    elif not resume_text or not resume_text.strip():
        st.warning("⚠️ 请先粘贴简历内容或上传 PDF，或点击「🎯 一键填入示例」快速体验")
    else:
        # 构造请求
        request = AnalysisRequest(
            resume_text=resume_text.strip(),
            jd_text=jd_text.strip(),
        )

        # 调用分析
        with st.spinner("🤖 AI 正在分析简历与岗位的匹配度..."):
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
            if result.match_points:
                for i, point in enumerate(result.match_points, 1):
                    st.markdown(f"**{i}. {point.title}**")
                    st.caption(point.description)
            else:
                st.caption("暂无匹配点")

        # 差距
        with col_gap:
            st.markdown("### ⚠️ 差距/缺口")
            if result.gaps:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                for gap in result.gaps:
                    icon = severity_icon.get(gap.severity, "⚪")
                    st.markdown(f"**{icon} {gap.title}**")
                    st.caption(gap.description)
            else:
                st.caption("暂无差距")

        # 优化建议
        with col_suggest:
            st.markdown("### 💡 优化建议")
            if result.suggestions:
                for i, sug in enumerate(result.suggestions, 1):
                    st.markdown(f"**{i}. [{sug.category}]**")
                    st.caption(sug.content)
            else:
                st.caption("暂无建议")

# ==================== 求职信生成 ====================
if letter_btn:
    if not jd_text or not jd_text.strip():
        st.warning("⚠️ 请先粘贴目标岗位的 JD，或点击「🎯 一键填入示例」快速体验")
    elif not resume_text or not resume_text.strip():
        st.warning("⚠️ 请先粘贴简历内容或上传 PDF，或点击「🎯 一键填入示例」快速体验")
    else:
        # 调用求职信生成
        with st.spinner("✍️ AI 正在生成求职信..."):
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

# ==================== 历史记录 ====================
st.markdown("---")
st.subheader("📋 分析历史记录")

# 获取最近的分析记录
recent_analyses = get_recent_analyses(limit=5)

if recent_analyses:
    for i, record in enumerate(recent_analyses, 1):
        with st.expander(f"📊 记录 {i} - 匹配度: {record['match_score']}分 - {record['created_at'][:16]}"):
            col_info, col_score = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"**简历摘要**: {record['resume_text'][:100]}...")
                st.markdown(f"**JD 摘要**: {record['jd_text'][:100]}...")
            
            with col_score:
                score = record['match_score']
                if score >= 80:
                    st.success(f"🟢 {score}分")
                elif score >= 60:
                    st.warning(f"🟡 {score}分")
                else:
                    st.error(f"🔴 {score}分")
            
            st.markdown(f"**总体评价**: {record['summary']}")
            
            # 显示匹配点
            if record.get('match_points'):
                st.markdown("**匹配点**:")
                for point in record['match_points']:
                    st.markdown(f"- {point['title']}: {point['description']}")
            
            # 显示建议
            if record.get('suggestions'):
                st.markdown("**优化建议**:")
                for sug in record['suggestions']:
                    st.markdown(f"- [{sug['category']}] {sug['content']}")
else:
    st.info("📝 暂无分析记录，点击「🎯 一键填入示例」后开始你的第一次分析吧！")

# ==================== 页脚 ====================
st.markdown("---")
st.caption("JobCopilot v0.1.0 | AI 求职副驾驶 | Powered by MiMo")

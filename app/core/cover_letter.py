"""
求职信生成模块
接入 MIMO API 生成定制求职信
"""

from openai import OpenAI
from app.config import get_api_key, get_base_url, get_model

# Prompt 模板
COVER_LETTER_PROMPT = """你是一位专业的求职信撰写专家。请根据以下信息生成一封专业的求职信。

## 目标岗位 JD
{jd}

## 应聘者简历
{resume}

## 要求：
1. 开头表明申请意向，提及公司和岗位名称
2. 中间段落突出与岗位最匹配的 2-3 个核心能力
3. 结尾表达诚意和期待
4. 语言专业但不失亲和力
5. 控制在 300-400 字
6. 使用中文

请直接输出求职信正文，不要添加额外说明。
"""


def generate_cover_letter(resume_text: str, jd_text: str) -> tuple[str, dict]:
    """
    生成求职信
    
    返回: (求职信内容, 调试信息)
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
    }

    # 如果没有配置 API Key，返回提示
    if not api_key:
        debug_info["error"] = "未配置 API Key"
        return "⚠️ 未配置 API Key，无法生成求职信。请在 Streamlit Cloud 的 Secrets 中配置 OPENAI_API_KEY。", debug_info

    try:
        # 初始化 OpenAI 客户端（兼容 MIMO API）
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        # 构造 prompt
        prompt = COVER_LETTER_PROMPT.format(
            jd=jd_text,
            resume=resume_text,
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
            max_tokens=1000,
        )

        # 返回求职信内容
        content = response.choices[0].message.content
        return content, debug_info

    except Exception as e:
        # API 调用失败
        debug_info["error"] = str(e)
        print(f"求职信生成失败: {e}")
        return f"❌ 求职信生成失败: {str(e)[:100]}...", debug_info

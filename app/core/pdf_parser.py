"""
PDF 简历解析模块
使用 PyMuPDF 提取 PDF 文本
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_file) -> str:
    """
    从 PDF 文件提取文本
    
    参数:
        pdf_file: Streamlit 上传的文件对象或文件路径
    
    返回:
        提取的文本内容
    """
    try:
        # 读取 PDF 文件
        if hasattr(pdf_file, 'read'):
            # Streamlit 上传的文件对象
            pdf_bytes = pdf_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            # 文件路径
            doc = fitz.open(pdf_file)
        
        text_parts = []
        
        # 遍历每一页提取文本
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
        
        doc.close()
        
        # 合并所有文本
        full_text = "\n".join(text_parts)
        
        # 简单清理：移除多余空行
        lines = full_text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return "\n".join(cleaned_lines)
    
    except Exception as e:
        print(f"PDF 解析失败: {e}")
        return f"❌ PDF 解析失败: {str(e)}"

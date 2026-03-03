import os
import docx2txt
from pypdf import PdfReader

def read_document(file_path):
    """
    自适应读取不同格式的文档并提取文本
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        elif ext in ['.docx', '.doc']:
            text = docx2txt.process(file_path)
            
        elif ext in ['.txt', '.md', '.py', '.cpp']:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        else:
            return f"[错误] 不支持的文件格式: {ext}"
            
        return text.strip()
    
    except Exception as e:
        return f"[解析文档失败]: {str(e)}"

def split_text(text, chunk_size=1000):
    """
    如果文档太长，可以切分成块（后续 RAG 进阶使用）
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

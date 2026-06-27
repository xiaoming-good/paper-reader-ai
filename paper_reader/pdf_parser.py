import re
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """PDF文献解析器"""
    
    def __init__(self):
        self.metadata = {}
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析PDF文件，提取文本和元数据
        
        Returns:
            dict: 包含 text, metadata, pages, toc 等信息的字典
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        result = {
            "file_path": str(path.absolute()),
            "file_name": path.name,
            "text": "",
            "metadata": {},
            "pages": [],
            "page_count": 0,
            "toc": []
        }
        
        # 使用 PyPDF2 提取元数据
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                result["metadata"] = dict(reader.metadata) if reader.metadata else {}
                result["page_count"] = len(reader.pages)
                
                # 尝试提取目录
                if "/Outlines" in reader.trailer["/Root"]:
                    outlines = reader.outline
                    result["toc"] = self._extract_toc(outlines)
        except Exception as e:
            logger.warning(f"PyPDF2 元数据提取失败: {e}")
        
        # 使用 pdfplumber 提取文本（更精确）
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        full_text.append(f"\n--- Page {i+1} ---\n{page_text}")
                
                result["text"] = "\n".join(full_text)
                result["pages"] = full_text
        except Exception as e:
            logger.error(f"pdfplumber 文本提取失败: {e}")
            # 降级使用 PyPDF2
            result["text"] = self._fallback_extract(file_path)
        
        # 提取标题（通常是第一页的前几行）
        result["title"] = self._extract_title(result["text"])
        
        # 提取摘要
        result["abstract"] = self._extract_abstract(result["text"])
        
        return result
    
    def _extract_toc(self, outlines) -> List[Dict]:
        """提取目录结构"""
        toc = []
        for item in outlines:
            if isinstance(item, list):
                toc.extend(self._extract_toc(item))
            elif hasattr(item, 'title'):
                toc.append({
                    "title": item.title,
                    "page": getattr(item, 'page', None)
                })
        return toc
    
    def _fallback_extract(self, file_path: str) -> str:
        """降级提取方案"""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                texts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        texts.append(text)
                return "\n".join(texts)
        except Exception as e:
            logger.error(f"降级提取也失败: {e}")
            return ""
    
    def _extract_title(self, text: str) -> str:
        """从文本中提取标题"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "未知标题"
        
        # 标题通常是第一页的前几行非空行，且比较短
        for line in lines[:20]:
            if 10 < len(line) < 200 and not line.startswith('---'):
                # 排除常见的非标题行
                if not any(keyword in line.lower() for keyword in 
                          ['abstract', 'introduction', 'keywords', 'doi', 'http', 'email']):
                    return line
        return lines[0] if lines else "未知标题"
    
    def _extract_abstract(self, text: str) -> str:
        """提取摘要部分"""
        # 常见的摘要标记模式
        patterns = [
            r'(?i)abstract[\s]*[:\n](.*?)(?=\n\s*(?:keywords|introduction|1\.|I\.))',
            r'(?i)摘要[\s]*[:\n](.*?)(?=\n\s*(?:关键词|引言|1\.|一、))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # 清理多余空白
                abstract = ' '.join(abstract.split())
                return abstract[:2000]  # 限制长度
        
        return ""
    
    def extract_references(self, text: str) -> List[str]:
        """提取参考文献部分"""
        # 匹配参考文献部分
        ref_patterns = [
            r'(?i)references[\s]*\n(.*?)(?=\n\s*(?:appendix|acknowledgment|figure|table)|$)',
            r'(?i)参考文献[\s]*\n(.*?)(?=\n\s*(?:附录|致谢|图|表)|$)',
        ]
        
        references = []
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                ref_text = match.group(1)
                # 按行分割，提取每条引用
                lines = ref_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 20:
                        references.append(line)
                break
        
        return references


class TextParser:
    """通用文本解析器（支持 TXT, MD 等）"""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "file_path": str(path.absolute()),
            "file_name": path.name,
            "text": text,
            "metadata": {},
            "pages": [text],
            "page_count": text.count('\n\n') + 1,
            "toc": [],
            "title": path.stem,
            "abstract": ""
        }


class DocumentParser:
    """文档解析工厂"""
    
    @staticmethod
    def parse(file_path: str) -> Dict[str, Any]:
        """根据文件类型自动选择解析器"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return PDFParser().parse(file_path)
        elif suffix in ['.txt', '.md', '.markdown']:
            return TextParser().parse(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

import re
from typing import List, Dict, Any, Tuple
from config import config

class TextProcessor:
    """文本处理与分块"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        # 删除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 删除页眉页脚标记
        text = re.sub(r'---\s*Page\s*\d+\s*---', '\n', text)
        # 删除孤立的数字（通常是页码）
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        return text.strip()
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        将长文本分割成多个块
        
        策略：
        1. 优先按段落分割
        2. 如果段落太长，按句子分割
        3. 保持上下文连贯性
        """
        # 先按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 如果单个段落就超过 chunk_size，需要进一步拆分
            if para_length > self.chunk_size:
                # 先保存当前 chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    # 保留重叠部分
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = len(overlap_text)
                
                # 拆分长段落为句子
                sentences = self._split_to_sentences(para)
                for sent in sentences:
                    if current_length + len(sent) > self.chunk_size and current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        overlap_text = self._get_overlap(current_chunk)
                        current_chunk = [overlap_text] if overlap_text else []
                        current_length = len(overlap_text)
                    
                    current_chunk.append(sent)
                    current_length += len(sent)
            
            elif current_length + para_length > self.chunk_size:
                # 保存当前 chunk，开始新 chunk
                chunks.append('\n\n'.join(current_chunk))
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = [overlap_text, para] if overlap_text else [para]
                current_length = sum(len(p) for p in current_chunk)
            
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # 保存最后一个 chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_to_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 匹配句子结尾（考虑缩写等特殊情况）
        sentence_pattern = r'(?<=[.!?。！？])\s+(?=[A-Z\u4e00-\u9fff])'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, chunks: List[str]) -> str:
        """获取重叠文本，保持上下文连贯"""
        if not chunks:
            return ""
        
        overlap_text = "\n\n".join(chunks[-2:])  # 保留最后两段
        if len(overlap_text) > self.chunk_overlap:
            # 如果重叠太多，截断
            overlap_text = overlap_text[-self.chunk_overlap:]
        return overlap_text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """提取文献的主要章节"""
        sections = {}
        
        # 常见章节模式（英文和中文）
        section_patterns = [
            (r'(?i)(?:^|\n)\s*1\.\s*Introduction\s*\n', 'introduction'),
            (r'(?i)(?:^|\n)\s*(?:2\.\s*|)Related\s+Work|Background\s*\n', 'background'),
            (r'(?i)(?:^|\n)\s*(?:\d+\.\s*|)Methodology|Methods|Method\s*\n', 'methodology'),
            (r'(?i)(?:^|\n)\s*(?:\d+\.\s*|)Experiments?|Evaluation|Results?\s*\n', 'experiments'),
            (r'(?i)(?:^|\n)\s*(?:\d+\.\s*|)Conclusion|Discussion\s*\n', 'conclusion'),
            (r'(?i)(?:^|\n)\s*摘要\s*\n', 'abstract'),
            (r'(?i)(?:^|\n)\s*引言|绪论\s*\n', 'introduction'),
            (r'(?i)(?:^|\n)\s*方法|方法ology|实验方法\s*\n', 'methodology'),
            (r'(?i)(?:^|\n)\s*实验|结果|实验结果\s*\n', 'experiments'),
            (r'(?i)(?:^|\n)\s*结论|讨论|总结\s*\n', 'conclusion'),
        ]
        
        # 找到所有章节的位置
        positions = []
        for pattern, name in section_patterns:
            for match in re.finditer(pattern, text):
                positions.append((match.start(), name, match.group()))
        
        # 按位置排序
        positions.sort(key=lambda x: x[0])
        
        # 提取各章节内容
        for i, (pos, name, _) in enumerate(positions):
            start = pos
            end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
            content = text[start:end].strip()
            if name not in sections or len(content) > len(sections.get(name, '')):
                sections[name] = content
        
        return sections
    
    def identify_key_paragraphs(self, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """识别关键段落（基于关键词密度）"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # 关键指标词
        key_indicators = [
            'result', 'finding', 'conclude', 'show', 'demonstrate', 'prove',
            'significant', 'improve', 'achieve', 'outperform', 'novel',
            'contribution', 'key', 'main', 'important', 'essential',
            '结果', '发现', '结论', '表明', '证明', '显著', '提高', '优于',
            '贡献', '关键', '主要', '重要'
        ]
        
        scored_paragraphs = []
        for para in paragraphs:
            if len(para) < 50 or len(para) > 1000:
                continue
            
            score = 0
            para_lower = para.lower()
            for indicator in key_indicators:
                if indicator.lower() in para_lower:
                    score += 1
            
            # 包含数据的段落加分
            if re.search(r'\d+\.?\d*\s*%', para) or re.search(r'\d+\.?\d*\s*(?:times|x|fold)', para):
                score += 2
            
            if score > 0:
                scored_paragraphs.append({
                    'text': para,
                    'score': score,
                    'length': len(para)
                })
        
        # 按分数排序，取前N个
        scored_paragraphs.sort(key=lambda x: x['score'], reverse=True)
        return scored_paragraphs[:top_n]

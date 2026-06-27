"""数据模型定义"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PaperInfo(BaseModel):
    """文献基本信息"""
    file_path: str
    file_name: str
    title: str = ""
    abstract: str = ""
    metadata: Dict[str, Any] = {}
    page_count: int = 0
    toc: List[Dict[str, Any]] = []

class ChunkAnalysis(BaseModel):
    """分块分析结果"""
    chunk_index: int
    key_points: List[str] = []
    quotable_sentences: List[str] = []
    methodology_notes: str = ""
    data_evidence: str = ""
    writing_use: str = ""

class PaperAnalysisResult(BaseModel):
    """文献分析完整结果"""
    paper_info: PaperInfo
    chunk_analyses: List[ChunkAnalysis] = []
    synthesized_report: str = ""
    writing_materials: str = ""
    sections: Dict[str, str] = {}

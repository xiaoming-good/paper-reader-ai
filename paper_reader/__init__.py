from .pdf_parser import DocumentParser, PDFParser, TextParser
from .text_processor import TextProcessor
from .ai_analyzer import AIAnalyzer
from .writing_helper import WritingHelper
from .models import PaperInfo, PaperAnalysisResult, ChunkAnalysis
from typing import Union, List, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging

logger = logging.getLogger(__name__)
console = Console()

class PaperReader:
    """文献阅读器主类"""
    
    def __init__(self, config=None):
        self.config = config
        self.parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.ai_analyzer = AIAnalyzer(config)
        self.writing_helper = WritingHelper()
        
    def analyze(self, file_path: str, mode: str = "detailed", output_file: str = None) -> PaperAnalysisResult:
        """
        分析单篇文献
        
        Args:
            file_path: 文献文件路径
            mode: 分析模式 (brief/detailed/comprehensive)
            output_file: 输出文件路径
        
        Returns:
            PaperAnalysisResult: 分析结果
        """
        console.print(f"\n[bold blue]📖 开始分析文献: {Path(file_path).name}[/bold blue]\n")
        
        # 1. 解析文档
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("📄 正在解析文档...", total=None)
            doc_info = self.parser.parse(file_path)
            progress.update(task, description="✅ 文档解析完成")
        
        console.print(f"[green]✓[/green] 标题: {doc_info.get('title', '未知')}")
        console.print(f"[green]✓[/green] 页数: {doc_info.get('page_count', 0)}")
        console.print(f"[green]✓[/green] 文本长度: {len(doc_info.get('text', ''))} 字符\n")
        
        # 2. 文本处理
        text = self.text_processor.clean_text(doc_info['text'])
        
        # 3. 根据模式选择分析策略
        if mode == "brief" or len(text) < 10000:
            result = self._analyze_short(text, doc_info)
        elif mode == "comprehensive":
            result = self._analyze_comprehensive(text, doc_info)
        else:
            result = self._analyze_detailed(text, doc_info)
        
        # 4. 生成最终输出
        final_output = self._generate_final_output(result, doc_info)
        result.writing_materials = final_output
        
        # 5. 保存结果
        if output_file:
            self._save_output(final_output, output_file)
            console.print(f"\n[bold green]✅ 结果已保存到: {output_file}[/bold green]")
        
        return result
    
    def _analyze_short(self, text: str, doc_info: Dict[str, Any]) -> PaperAnalysisResult:
        """短篇文献分析（直接全文分析）"""
        console.print("[yellow]🔍 使用直接分析模式（文献较短）[/yellow]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🤖 AI正在分析全文...", total=None)
            analysis = self.ai_analyzer.extract_writing_materials(text, doc_info)
            progress.update(task, description="✅ AI分析完成")
        
        result = PaperAnalysisResult(
            paper_info=PaperInfo(**{k: v for k, v in doc_info.items() if k in PaperInfo.model_fields}),
            writing_materials=analysis.get('writing_materials', '')
        )
        return result
    
    def _analyze_detailed(self, text: str, doc_info: Dict[str, Any]) -> PaperAnalysisResult:
        """详细分析（分块处理）"""
        console.print("[yellow]🔍 使用分块分析模式（文献较长）[/yellow]\n")
        
        # 分块
        chunks = self.text_processor.split_into_chunks(text)
        console.print(f"[blue]ℹ[/blue] 文档已分为 {len(chunks)} 个片段进行分析\n")
        
        # 分析每个块
        chunk_results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🤖 AI正在分析各个片段...", total=len(chunks))
            
            for i, chunk in enumerate(chunks):
                progress.update(task, advance=1, description=f"🤖 正在分析第 {i+1}/{len(chunks)} 个片段...")
                analysis = self.ai_analyzer.analyze_chunk(chunk, i, len(chunks))
                chunk_results.append(ChunkAnalysis(
                    chunk_index=i,
                    **analysis
                ))
            
            progress.update(task, description="✅ 所有片段分析完成")
        
        # 综合分析
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔄 正在综合所有分析结果...", total=None)
            
            # 转换为字典列表
            chunk_dicts = [{
                'key_points': c.key_points,
                'quotable_sentences': c.quotable_sentences,
                'methodology_notes': c.methodology_notes,
                'data_evidence': c.data_evidence,
                'writing_use': c.writing_use
            } for c in chunk_results]
            
            synthesized = self.ai_analyzer.synthesize_analysis(chunk_dicts, doc_info)
            progress.update(task, description="✅ 综合分析完成")
        
        result = PaperAnalysisResult(
            paper_info=PaperInfo(**{k: v for k, v in doc_info.items() if k in PaperInfo.model_fields}),
            chunk_analyses=chunk_results,
            synthesized_report=synthesized
        )
        return result
    
    def _analyze_comprehensive(self, text: str, doc_info: Dict[str, Any]) -> PaperAnalysisResult:
        """全面分析（包含章节识别和深度分析）"""
        # 先进行详细分析
        result = self._analyze_detailed(text, doc_info)
        
        # 额外提取章节信息
        sections = self.text_processor.extract_sections(text)
        result.sections = sections
        
        return result
    
    def _generate_final_output(self, result: PaperAnalysisResult, doc_info: Dict[str, Any]) -> str:
        """生成最终输出"""
        # 如果有综合分析报告，使用它
        if result.synthesized_report:
            output = f"""# 📄 文献深度分析报告

> **文献**: {doc_info.get('title', '未知')}
> **文件**: {doc_info.get('file_name', '')}

---

{result.synthesized_report}

---

## 📚 原始素材整理

"""
            # 添加分块分析的关键信息
            if result.chunk_analyses:
                output += "### 所有核心观点\n\n"
                all_points = []
                for chunk in result.chunk_analyses:
                    all_points.extend(chunk.key_points)
                
                # 去重
                seen = set()
                unique_points = []
                for p in all_points:
                    if p not in seen:
                        seen.add(p)
                        unique_points.append(p)
                
                for i, point in enumerate(unique_points[:20], 1):
                    output += f"{i}. {point}\n\n"
                
                # 所有可引用语句
                output += "\n### 所有可引用语句\n\n"
                all_quotes = []
                for chunk in result.chunk_analyses:
                    all_quotes.extend(chunk.quotable_sentences)
                
                seen = set()
                unique_quotes = []
                for q in all_quotes:
                    if q not in seen:
                        seen.add(q)
                        unique_quotes.append(q)
                
                for i, quote in enumerate(unique_quotes[:20], 1):
                    output += f"> {i}. \"{quote}\"\n\n"
            
            return output
        else:
            # 使用写作素材格式化
            return self.writing_helper.organize_materials(
                {"writing_materials": result.writing_materials},
                doc_info
            )
    
    def _save_output(self, content: str, output_file: str):
        """保存输出到文件"""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def analyze_batch(self, input_dir: str, output_dir: str, mode: str = "detailed"):
        """批量分析文献"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 查找所有支持的文件
        files = []
        for ext in ['*.pdf', '*.txt', '*.md']:
            files.extend(input_path.glob(ext))
        
        console.print(f"\n[bold blue]📂 找到 {len(files)} 篇文献，开始批量分析...[/bold blue]\n")
        
        for i, file in enumerate(files, 1):
            console.print(f"[cyan]▶ [{i}/{len(files)}] 分析: {file.name}[/cyan]")
            output_file = output_path / f"{file.stem}_analysis.md"
            try:
                self.analyze(str(file), mode=mode, output_file=str(output_file))
            except Exception as e:
                console.print(f"[red]✗ 分析失败: {e}[/red]")
                continue
        
        console.print(f"\n[bold green]✅ 批量分析完成！结果保存在: {output_dir}[/bold green]")

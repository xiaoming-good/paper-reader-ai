from typing import List, Dict, Any, Optional
import re

class WritingHelper:
    """写作辅助工具 - 整理提取的素材，生成可直接使用的写作内容"""
    
    def __init__(self, output_language: str = "zh"):
        self.output_language = output_language
    
    def organize_materials(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> str:
        """将分析结果整理为写作素材卡片"""
        
        title = doc_info.get('title', '未知文献')
        
        output = f"""# 📄 写作素材卡片：{title}

> **来源**: {doc_info.get('file_name', 'unknown')}
> **分析日期**: 自动生成
> **用途**: 学术写作引用参考

---

"""
        
        # 1. 文献概览
        output += "## 📋 文献概览\n\n"
        if doc_info.get('abstract'):
            output += f"**摘要**: {doc_info['abstract'][:300]}...\n\n"
        
        if 'writing_materials' in analysis_result:
            output += self._format_writing_materials(analysis_result['writing_materials'])
        
        # 如果有结构化分析结果
        if 'key_points' in analysis_result:
            output += "\n## 🔑 核心观点\n\n"
            for i, point in enumerate(analysis_result.get('key_points', [])[:10], 1):
                output += f"{i}. {point}\n\n"
        
        if 'quotable_sentences' in analysis_result:
            output += "\n## 💬 可引用语句\n\n"
            for i, quote in enumerate(analysis_result.get('quotable_sentences', [])[:15], 1):
                output += f"> {i}. \"{quote}\"\n\n"
        
        if 'methodology_notes' in analysis_result and analysis_result['methodology_notes']:
            output += "\n## 🔬 方法参考\n\n"
            output += f"{analysis_result['methodology_notes']}\n\n"
        
        if 'data_evidence' in analysis_result and analysis_result['data_evidence']:
            output += "\n## 📊 数据与证据\n\n"
            output += f"{analysis_result['data_evidence']}\n\n"
        
        # 写作建议
        output += "\n## ✍️ 写作应用建议\n\n"
        output += self._generate_writing_suggestions(analysis_result, doc_info)
        
        return output
    
    def _format_writing_materials(self, materials_text: str) -> str:
        """格式化AI生成的写作素材"""
        # 清理并格式化AI输出
        formatted = materials_text.strip()
        
        # 确保标题使用正确的Markdown格式
        formatted = re.sub(r'^(#{1,6})\s*', r'## ', formatted, flags=re.MULTILINE)
        
        return formatted
    
    def _generate_writing_suggestions(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> str:
        """生成写作建议"""
        suggestions = []
        
        if analysis_result.get('key_points'):
            suggestions.append("- **文献综述**: 可将本文的核心观点纳入文献综述的 [相关主题] 部分")
        
        if analysis_result.get('quotable_sentences'):
            suggestions.append("- **直接引用**: 文中标注的可引用句子可用于支撑你的论点")
        
        if analysis_result.get('methodology_notes'):
            suggestions.append("- **方法借鉴**: 参考本文的研究方法设计，特别适用于 [类似场景]")
        
        if analysis_result.get('data_evidence'):
            suggestions.append("- **数据支撑**: 使用本文的实验数据作为你论点的实证支撑")
        
        suggestions.append("- **对比分析**: 可将本文结论与 [你的研究发现/其他文献] 进行对比")
        suggestions.append("- **批判引用**: 注意本文的局限性，可用于展示你对该领域的深入理解")
        
        return '\n'.join(suggestions) + '\n'
    
    def generate_citation(self, doc_info: Dict[str, Any], style: str = "apa") -> str:
        """生成标准引用格式"""
        # 从文件名或元数据提取信息
        title = doc_info.get('title', doc_info.get('file_name', 'Unknown'))
        
        if style == "apa":
            return f"{title} (n.d.). Retrieved from {doc_info.get('file_name', '')}"
        elif style == "mla":
            return f'"{title}." {doc_info.get("file_name", "")}'
        elif style == "gb":
            return f"[{title}[J/OL]. {doc_info.get('file_name', '')}.]"
        else:
            return title
    
    def create_argument_map(self, analysis_result: Dict[str, Any]) -> str:
        """创建论点映射 - 展示文献如何支撑不同论点"""
        output = "## 🗺️ 论点映射\n\n"
        output += "以下展示本文献可如何支撑你的不同论点：\n\n"
        
        key_points = analysis_result.get('key_points', [])
        
        argument_mappings = {
            "研究背景/问题重要性": [p for p in key_points if any(w in p for w in ['problem', 'issue', 'challenge', 'gap', '问题', '挑战', '空白'])],
            "方法创新": [p for p in key_points if any(w in p for w in ['method', 'approach', 'novel', 'methodology', '方法', '创新'])],
            "理论贡献": [p for p in key_points if any(w in p for w in ['theory', 'framework', 'model', '理论', '框架', '模型'])],
            "实证发现": [p for p in key_points if any(w in p for w in ['result', 'finding', 'evidence', '结果', '发现', '证据'])],
            "实践意义": [p for p in key_points if any(w in p for w in ['practice', 'application', 'implication', '实践', '应用', '意义'])],
        }
        
        for argument_type, points in argument_mappings.items():
            if points:
                output += f"### {argument_type}\n"
                for p in points[:3]:
                    output += f"- ✅ {p}\n"
                output += "\n"
        
        return output
    
    def generate_summary_for_different_sections(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> Dict[str, str]:
        """为论文不同章节生成可用的总结段落"""
        
        sections = {}
        
        # 引言部分可用内容
        sections["introduction"] = self._generate_introduction_use(analysis_result, doc_info)
        
        # 文献综述部分可用内容
        sections["literature_review"] = self._generate_lr_use(analysis_result, doc_info)
        
        # 方法部分可用内容
        sections["methodology"] = self._generate_method_use(analysis_result, doc_info)
        
        # 讨论部分可用内容
        sections["discussion"] = self._generate_discussion_use(analysis_result, doc_info)
        
        return sections
    
    def _generate_introduction_use(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> str:
        """生成引言部分可用的内容"""
        output = "### 引言部分可用\n\n"
        output += "**研究背景引用**：\n"
        
        abstract = doc_info.get('abstract', '')
        if abstract:
            output += f"> {abstract[:200]}...\n\n"
        
        key_points = analysis_result.get('key_points', [])
        if key_points:
            output += "**问题重要性支撑**：\n"
            for p in key_points[:2]:
                if any(w in p.lower() for w in ['problem', 'issue', 'gap', 'challenge', '问题', '挑战']):
                    output += f"- {p}\n"
        
        return output
    
    def _generate_lr_use(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> str:
        """生成文献综述部分可用的内容"""
        output = "### 文献综述部分可用\n\n"
        
        key_points = analysis_result.get('key_points', [])
        if key_points:
            output += "**可对比/综述的观点**：\n"
            for p in key_points[:5]:
                output += f"- {p}\n"
        
        quotes = analysis_result.get('quotable_sentences', [])
        if quotes:
            output += "\n**可直接引用的综述语句**：\n"
            for q in quotes[:3]:
                output += f"> \"{q}\"\n\n"
        
        return output
    
    def _generate_method_use(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> str:
        """生成方法部分可用的内容"""
        output = "### 方法部分可用\n\n"
        
        methods = analysis_result.get('methodology_notes', '')
        if methods:
            output += f"**方法参考**：\n{methods}\n\n"
        
        output += "**建议的借鉴方式**：\n"
        output += "- 可参考其实验设计思路\n"
        output += "- 可对比其数据处理方法\n"
        output += "- 可借鉴其评估指标选择\n\n"
        
        return output
    
    def _generate_discussion_use(self, analysis_result: Dict[str, Any], doc_info: Dict[str, Any]) -> str:
        """生成讨论部分可用的内容"""
        output = "### 讨论部分可用\n\n"
        
        output += "**对比讨论素材**：\n"
        output += "- 可与本文结果进行比较\n"
        output += "- 可讨论方法上的差异\n"
        output += "- 可分析结论的异同\n\n"
        
        data = analysis_result.get('data_evidence', '')
        if data:
            output += f"**对比数据**：\n{data}\n\n"
        
        return output

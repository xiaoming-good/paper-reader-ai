from typing import List, Dict, Any, Optional
import json
import re
from openai import OpenAI
from config import Config

class AIAnalyzer:
    """AI分析引擎 - 使用大语言模型分析文献"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.model_config = self.config.get_model_config()
        self.client = OpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )
        self.model = self.model_config["model"]
    
    def _call_llm(self, prompt: str, system_prompt: str = None, max_tokens: int = None) -> str:
        """调用大语言模型"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.config.MAX_TOKENS,
                temperature=0.3  # 较低的temperature，保持输出稳定
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM调用失败: {e}")
    
    def analyze_chunk(self, chunk: str, chunk_index: int, total_chunks: int) -> Dict[str, Any]:
        """分析单个文本块"""
        system_prompt = """你是一位专业的学术文献分析助手。你的任务是仔细阅读提供的文献片段，
提取对学术写作有用的关键信息。请以JSON格式输出，确保输出格式严格正确。"""
        
        prompt = f"""请分析以下文献片段（第{chunk_index+1}/{total_chunks}部分）：

```
{chunk[:3000]}
```

请提取以下信息并以JSON格式返回（只返回JSON，不要其他内容）：
{{
    "key_points": ["核心观点1", "核心观点2"],  // 该片段中的核心论点
    "quotable_sentences": ["可引用句子1", "可引用句子2"],  // 可直接用于写作的引用句
    "methodology_notes": "方法相关描述",  // 研究方法相关的内容
    "data_evidence": "数据与证据",  // 重要的数据、实验结果
    "writing_use": "对写作的帮助"  // 这部分内容对我的写作有什么帮助
}}

如果没有某类信息，使用空字符串或空数组。"""
        
        response = self._call_llm(prompt, system_prompt, max_tokens=2000)
        
        # 解析JSON响应
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回结构化文本
            return self._parse_text_response(response)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """将文本响应解析为结构化数据"""
        result = {
            "key_points": [],
            "quotable_sentences": [],
            "methodology_notes": "",
            "data_evidence": "",
            "writing_use": ""
        }
        
        # 尝试提取关键信息
        lines = text.split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            if '核心观点' in line or 'key point' in line.lower():
                current_key = 'key_points'
            elif '引用' in line or 'quotable' in line.lower():
                current_key = 'quotable_sentences'
            elif '方法' in line or 'method' in line.lower():
                current_key = 'methodology_notes'
            elif '数据' in line or 'evidence' in line.lower():
                current_key = 'data_evidence'
            elif '写作' in line or 'writing' in line.lower() or 'help' in line.lower():
                current_key = 'writing_use'
            elif line and current_key:
                if current_key in ['key_points', 'quotable_sentences']:
                    result[current_key].append(line.lstrip('- ').strip('"'))
                else:
                    result[current_key] += line + ' '
        
        return result
    
    def synthesize_analysis(self, chunk_results: List[Dict], doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """综合所有分析结果，生成最终报告"""
        system_prompt = """你是一位资深的学术写作顾问。请基于文献分段分析结果，
生成一份结构化的文献分析总结，帮助用户将其融入到自己的写作中。"""
        
        # 合并所有分块结果
        all_key_points = []
        all_quotable = []
        all_methods = []
        all_data = []
        all_writing_use = []
        
        for r in chunk_results:
            all_key_points.extend(r.get('key_points', []))
            all_quotable.extend(r.get('quotable_sentences', []))
            if r.get('methodology_notes'):
                all_methods.append(r['methodology_notes'])
            if r.get('data_evidence'):
                all_data.append(r['data_evidence'])
            if r.get('writing_use'):
                all_writing_use.append(r['writing_use'])
        
        # 去重
        all_key_points = list(dict.fromkeys(all_key_points))
        all_quotable = list(dict.fromkeys(all_quotable))
        
        # 构建综合提示
        prompt = f"""基于以下文献分段分析结果，请生成一份完整的写作辅助报告。

文献标题：{doc_info.get('title', '未知')}
摘要：{doc_info.get('abstract', '无')[:500]}

各段核心观点：
{chr(10).join(f'- {p}' for p in all_key_points[:20])}

可引用语句：
{chr(10).join(f'- {q}' for q in all_quotable[:15])}

方法相关：
{chr(10).join(f'- {m}' for m in all_methods[:5])}

数据证据：
{chr(10).join(f'- {d}' for d in all_data[:5])}

请按以下结构输出完整的分析报告（使用Markdown格式）：

## 1. 文献概览
- 研究主题/问题
- 核心贡献

## 2. 核心论点总结（适合用于文献综述）
- 分点列出，每个论点带简要说明

## 3. 可引用素材（按主题分类）
- 直接可用于引用的句子（带建议的引用位置说明）

## 4. 研究方法参考
- 使用了什么方法
- 适合借鉴到我研究中的方法

## 5. 数据与证据
- 关键实验结果和数据
- 可用于支撑我论点的证据

## 6. 写作应用建议
- 在我的写作中，可以如何使用这篇文献
- 可以与哪些观点形成对比/支撑
- 潜在的批评角度
"""
        
        return self._call_llm(prompt, system_prompt, max_tokens=4000)
    
    def extract_writing_materials(self, full_text: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """直接提取写作素材（适用于较短的文献）"""
        system_prompt = """你是一位专业的学术写作助手。请从文献中提取所有对写作有用的素材，
包括可引用语句、核心观点、方法参考、数据证据等。"""
        
        # 截断文本以避免超出限制
        text_to_analyze = full_text[:15000]  # 限制长度
        
        prompt = f"""请仔细分析以下文献，提取对学术写作有用的所有素材：

文献标题：{doc_info.get('title', '未知')}

```
{text_to_analyze}
```

请提取以下信息并以结构化格式输出：

**一、核心观点与论点**
（按重要性排序，列出5-10个核心论点，每个附带简要说明其在原文中的支撑）

**二、可直接引用的句子**
（列出8-15个引用价值高的原句，标注"直接引用"或"改写引用"建议）

**三、研究方法参考**
（详细描述方法：1.方法名称 2.具体步骤 3.适用场景 4.可借鉴点）

**四、关键数据与实验结果**
（列出所有具体数据、指标、对比结果，标注页码位置）

**五、写作应用指南**
1. 这篇文献最适合支撑我的哪个论点？
2. 这篇文献可以与哪些研究方向形成对比？
3. 引用这篇文献时需要注意什么？
4. 这篇文献的局限性是什么？（可用于批判性分析）
"""
        
        response = self._call_llm(prompt, system_prompt, max_tokens=4000)
        return {"writing_materials": response}

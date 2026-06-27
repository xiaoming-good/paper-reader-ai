#!/usr/bin/env python3
"""
Web界面版 - 通过浏览器使用文献阅读助手

启动方式:
    python web_app.py

访问 http://localhost:7860
"""

import gradio as gr
import tempfile
from pathlib import Path
from paper_reader import PaperReader
from config import config

# 全局阅读器实例
reader = None

def get_reader():
    """获取或初始化阅读器"""
    global reader
    if reader is None:
        reader = PaperReader(config)
    return reader


def analyze_paper(file, mode, language):
    """分析文献（Gradio回调）"""
    if file is None:
        return "请先上传文献文件（PDF、TXT或MD）"
    
    if not config.api_key:
        return """⚠️ 未配置AI API密钥！

请按照以下步骤配置：
1. 在项目目录创建 .env 文件
2. 填入你的API Key：
   OPENAI_API_KEY=sk-xxxxxxxx
   或
   MOONSHOT_API_KEY=sk-xxxxxxxx
   或
   DEEPSEEK_API_KEY=sk-xxxxxxxx"""
    
    try:
        # 保存上传的文件
        if hasattr(file, 'name'):
            file_path = file.name
        else:
            file_path = file
        
        # 分析
        result = get_reader().analyze(
            file_path,
            mode=mode.lower()
        )
        
        return result.writing_materials
    
    except Exception as e:
        return f"分析出错: {str(e)}\n\n请检查：\n1. 文件是否有效\n2. API密钥是否正确\n3. 网络连接是否正常"


def create_interface():
    """创建Gradio界面"""
    
    with gr.Blocks(title="AI文献阅读助手", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 📖 AI文献阅读助手
        
        > 上传文献，AI自动提取对写作有用的核心内容
        
        ---
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 上传文献")
                file_input = gr.File(
                    label="选择文献（PDF、TXT、MD）",
                    file_types=[".pdf", ".txt", ".md"]
                )
                
                mode_dropdown = gr.Dropdown(
                    choices=["Brief（快速概览）", "Detailed（详细分析）", "Comprehensive（全面分析）"],
                    value="Detailed（详细分析）",
                    label="分析模式"
                )
                
                language_dropdown = gr.Dropdown(
                    choices=["中文", "English"],
                    value="中文",
                    label="输出语言"
                )
                
                analyze_btn = gr.Button("🚀 开始分析", variant="primary")
                
                gr.Markdown("""
                ---
                
                ### 使用提示
                
                1. **Brief**: 快速获取文献概览（适合筛选阶段）
                2. **Detailed**: 详细分析，提取核心观点和可引用内容
                3. **Comprehensive**: 最全面分析，包含章节识别和深度解读
                
                分析结果包含：
                - ✓ 核心观点总结
                - ✓ 可直接引用的句子
                - ✓ 研究方法参考
                - ✓ 数据与证据整理
                - ✓ 写作应用建议
                """)
            
            with gr.Column(scale=2):
                output_text = gr.Markdown(
                    label="分析结果",
                    value="请先上传文献并点击「开始分析」"
                )
        
        analyze_btn.click(
            fn=analyze_paper,
            inputs=[file_input, mode_dropdown, language_dropdown],
            outputs=output_text
        )
        
        gr.Markdown("""
        ---
        
        <center>
        
        💡 <b>提示</b>：首次使用请配置API Key，在项目目录创建 .env 文件
        
        🔗 <a href="https://github.com/xiaoming-good/paper-reader-ai" target="_blank">GitHub 项目地址</a>
        
        </center>
        """)
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

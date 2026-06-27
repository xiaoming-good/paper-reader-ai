#!/usr/bin/env python3
"""
AI文献阅读助手 - 主入口
用于阅读长文献，并提取出有助于写作时能使用的部分

使用方法:
    python main.py --input paper.pdf --output result.md
    python main.py --input ./papers/ --output ./results/ --mode comprehensive
"""

import argparse
import sys
from pathlib import Path
from paper_reader import PaperReader
from config import config
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_banner():
    """打印启动横幅"""
    banner = Text()
    banner.append("╔═══════════════════════════════════════╗\n", style="bold blue")
    banner.append("║      📖 AI文献阅读助手 v1.0           ║\n", style="bold blue")
    banner.append("║   提取文献精华，助力学术写作          ║\n", style="blue")
    banner.append("╚═══════════════════════════════════════╝", style="bold blue")
    console.print(banner)
    console.print()


def check_config():
    """检查配置是否有效"""
    if not config.api_key:
        console.print(Panel(
            "[red]⚠️ 未配置AI API密钥！[/red]\n\n"
            "请按照以下步骤配置：\n"
            "1. 复制 .env.example 为 .env\n"
            "2. 在 .env 文件中填入你的 API Key\n\n"
            "支持的API：\n"
            "- OpenAI (OPENAI_API_KEY)\n"
            "- Moonshot/Kimi (MOONSHOT_API_KEY)\n"
            "- DeepSeek (DEEPSEEK_API_KEY)",
            title="配置错误",
            border_style="red"
        ))
        return False
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI文献阅读助手 - 提取文献中有助于写作的部分",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单篇文献分析
  python main.py --input paper.pdf --output result.md

  # 详细分析模式
  python main.py --input paper.pdf --mode detailed --output result.md

  # 批量分析
  python main.py --input ./my_papers/ --output ./analysis_results/

  # 简短分析（快速概览）
  python main.py --input paper.pdf --mode brief
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入文件或文件夹路径（支持PDF、TXT、MD）"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="analysis_result.md",
        help="输出文件或文件夹路径（默认: analysis_result.md）"
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["brief", "detailed", "comprehensive"],
        default="detailed",
        help="分析模式：brief(快速概览)/detailed(详细分析)/comprehensive(全面分析)"
    )
    
    parser.add_argument(
        "--language", "-l",
        choices=["zh", "en"],
        default="zh",
        help="输出语言（默认: zh）"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式（默认: markdown）"
    )
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 检查配置
    if not check_config():
        sys.exit(1)
    
    # 显示配置信息
    console.print(Panel(
        f"[green]模型[/green]: {config.MODEL_NAME}\n"
        f"[green]分析模式[/green]: {args.mode}\n"
        f"[green]输出语言[/green]: {args.language}\n"
        f"[green]输出格式[/green]: {args.format}",
        title="当前配置",
        border_style="green"
    ))
    console.print()
    
    # 初始化阅读器
    reader = PaperReader(config)
    
    # 判断输入是文件还是文件夹
    input_path = Path(args.input)
    
    if not input_path.exists():
        console.print(f"[red]✗ 错误: 路径不存在: {args.input}[/red]")
        sys.exit(1)
    
    try:
        if input_path.is_file():
            # 单文件分析
            if not input_path.suffix.lower() in ['.pdf', '.txt', '.md', '.markdown']:
                console.print(f"[red]✗ 不支持的文件格式: {input_path.suffix}[/red]")
                console.print("[yellow]支持的格式: PDF, TXT, MD[/yellow]")
                sys.exit(1)
            
            result = reader.analyze(
                str(input_path),
                mode=args.mode,
                output_file=args.output
            )
            
            # 打印完成信息
            console.print(Panel(
                f"[bold green]✅ 分析完成！[/bold green]\n\n"
                f"[green]📄 输出文件[/green]: {args.output}\n"
                f"[green]📊 文本片段数[/green]: {len(result.chunk_analyses)}\n"
                f"[green]📝 报告长度[/green]: {len(result.writing_materials)} 字符",
                title="完成",
                border_style="green"
            ))
            
        elif input_path.is_dir():
            # 批量分析
            output_path = Path(args.output)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            
            reader.analyze_batch(
                str(input_path),
                str(output_path),
                mode=args.mode
            )
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ 用户中断[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]✗ 分析失败: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

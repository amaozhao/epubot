import asyncio
import os
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from epubot.config.logger import logger
from epubot.config.settings import settings
from epubot.services.coordinator import Coordinator

# 创建 Typer 应用
app = typer.Typer(
    name="epubot",
    help="EPUB 自动翻译工具",
    no_args_is_help=True,
    add_completion=False,
)


def validate_input_file(file_path: str) -> Path:
    """验证输入文件是否存在且可读"""
    path = Path(file_path)
    if not path.exists():
        typer.echo(f"错误: 输入文件 '{file_path}' 不存在。", err=True)
        raise typer.Exit(1)
    if not os.access(path, os.R_OK):
        typer.echo(f"错误: 无法读取文件 '{file_path}'。", err=True)
        raise typer.Exit(1)
    return path


# 为参数创建类型别名，提高可读性
InputEpubPath = Annotated[
    str,
    typer.Argument(
        ...,
        help="需要翻译的原始 EPUB 文件路径",
        callback=validate_input_file,
        show_default=False,
    ),
]

TargetLang = Annotated[
    str,
    typer.Option(
        "--target-lang",
        "-t",
        help="目标语言代码 (例如: zh, fr, es)",
        show_default=True,
    ),
]

OutputFile = Annotated[
    Optional[str],
    typer.Option(
        "--output-file",
        "-o",
        help="翻译完成的 EPUB 文件保存路径 (如果不指定，将自动生成)",
        show_default=False,
    ),
]

OutputDir = Annotated[
    str,
    typer.Option(
        "--output-dir",
        "-d",
        help=f"翻译完成的 EPUB 文件保存目录 (默认为: {settings.OUTPUT_DIR}，仅在不指定 --output-file 时使用)",
        show_default=True,
    ),
]


async def _translate_async(
    input_epub: Path,
    target_lang: str,
    output_file: Optional[str],
    output_dir: str,
):
    """异步执行翻译任务"""
    logger.info(
        "开始翻译",
        input_epub=str(input_epub),
        target_lang=target_lang,
        output_file=output_file,
        output_dir=output_dir,
    )

    # 创建输出目录（如果不存在）
    if output_file is None and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    coordinator = Coordinator(str(input_epub))
    await coordinator.process()


@app.command()
def translate(
    input_epub: InputEpubPath,
    target_lang: TargetLang = "zh",
    output_file: OutputFile = None,
    output_dir: OutputDir = settings.OUTPUT_DIR,
):
    """翻译 EPUB 文件到指定语言"""
    # 在同步函数中运行异步代码
    asyncio.run(_translate_async(input_epub, target_lang, output_file, output_dir))


# 添加版本信息
@app.callback()
def version_callback(
    version: bool = typer.Option(None, "--version", "-v", is_eager=True)
):
    """显示版本信息"""
    if version:
        from importlib.metadata import version

        typer.echo(f"epubot v{version('epubot')}")
        raise typer.Exit()


def run():
    """应用程序入口点，用于 setup.py 中的入口点配置"""
    app()


if __name__ == "__main__":
    # 使用 asyncio 运行 Typer 应用
    app()

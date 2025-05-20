import argparse
import asyncio
import os
import sys

from epubot.config.logger import logger

# 导入配置和日志设置
from epubot.config.settings import settings

# 导入协调者 Agent
from epubot.services.coordinator import Coordinator


async def main():
    """
    应用程序的主入口点。
    解析命令行参数，设置日志，启动 EPUB 翻译工作流。
    """
    # 设置参数解析器
    parser = argparse.ArgumentParser(description="EPUB 自动翻译应用程序")

    # 添加输入 EPUB 文件路径参数，这是必须的参数
    parser.add_argument("input_epub", type=str, help="需要翻译的原始 EPUB 文件路径")

    # 添加目标语言代码参数，这是必须的参数
    parser.add_argument(
        "--target_lang",
        type=str,
        default='zh',
        help="目标语言代码 (例如: zh, fr, es)"
    )

    # 添加可选的输出文件路径参数
    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="翻译完成的 EPUB 文件保存路径 (如果不指定，将自动生成)",
    )

    # 添加可选的输出目录参数，使用 settings 中的默认值
    parser.add_argument(
        "--output_dir",
        type=str,
        default=settings.OUTPUT_DIR,
        help=f"翻译完成的 EPUB 文件保存目录 (默认为: {settings.OUTPUT_DIR}，仅在不指定 --output_file 时使用)",
    )

    # 解析命令行参数
    args = parser.parse_args()

    logger.info(
        "应用程序启动",
        input_epub=args.input_epub,
        target_lang=args.target_lang,
        output_file=args.output_file,
        output_dir=args.output_dir,
    )

    # 检查输入文件是否存在
    if not os.path.exists(args.input_epub):
        logger.error("输入的 EPUB 文件不存在", file_path=args.input_epub)
        print(f"错误: 输入文件 '{args.input_epub}' 不存在。")
        sys.exit(1)

    coordinator = Coordinator(args.input_epub)
    await coordinator.process()


# 使用 asyncio 运行主函数
if __name__ == "__main__":
    # 确保日志在 asyncio 事件循环启动前配置好
    asyncio.run(main())

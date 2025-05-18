import ebooklib

from epubot.services.epub import EpubBuilder, EpubParser
from epubot.services.html import HTMLBuilder, HTMLReplacer, HTMLSplitter
from epubot.services.translator import Translator


class Coordinator:
    """
    协调者类，负责协调 EPUB 翻译的各个步骤。
    """

    def __init__(
        self, input_epub: str, target_lang: str = "zh", output_file: str = None
    ) -> None:
        self.input_epub = input_epub
        self.target_lang = target_lang
        self.output_file = output_file or f"{input_epub}-{target_lang}.epub"
        self.epub_parser = EpubParser(input_epub)
        self.html_splitter = HTMLSplitter()
        self.html_builder = HTMLBuilder()
        self.translator = Translator()

    async def translate(self, book) -> None:
        parser = "html.parser"
        for item in book.items:
            if item.item_type == ebooklib.ITEM_DOCUMENT:
                html_replacer = HTMLReplacer(parser)
                content = html_replacer.replace(item.content)
                chunks = self.html_splitter.split(content)
                translated_chunks = []
                for chunk in chunks:
                    chunk.translated = await self.translator.translate(chunk.content)
                    translated_chunks.append(chunk)
                item.translated = html_replacer.restore(
                    self.html_builder.build(translated_chunks)
                )
                print(chunks[-1].content)
                print(chunks[-1].translated)

    async def process(self) -> None:
        """
        运行 EPUB 翻译工作流。
        """
        # 解析 EPUB 文件
        book = self.epub_parser.parse()

        # 翻译
        await self.translate(book)

        # 构建新的 EPUB 文件
        epub_builder = EpubBuilder(book, self.output_file)
        epub_builder.build()
        print(f"翻译完成，输出文件: {self.output_file}")

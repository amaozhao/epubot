from typing import Union
from tqdm import tqdm
from ebooklib import epub
import json

from epubot.services.epub import EpubBuilder, EpubParser
from epubot.services.html import HTMLBuilder, HTMLReplacer, HTMLSplitter
from epubot.services.translator import Translator
from epubot.services.resume import Resume


class Coordinator:
    def __init__(
        self, 
        input_epub: str, 
        target_lang: str = "zh", 
        output_file: Union[str, None] = None,
        enable_resume: bool = True
    ) -> None:
        self.input_epub = input_epub
        self.target_lang = target_lang
        self.output_file = output_file or f"{input_epub}-{target_lang}.epub"
        self.epub_parser = EpubParser(input_epub)
        self.html_splitter = HTMLSplitter()
        self.html_builder = HTMLBuilder()
        self.translator = Translator()
        
        # 断点续传相关
        self.enable_resume = enable_resume
        self.resume = Resume() if enable_resume else None
        self.processed_files = set()
        
        if enable_resume and self.resume:
            self.processed_files = self.resume.get_processed_files(input_epub)
    
    def _update_toc(self, original_toc, translated_toc):
        """
        递归地将翻译后的标题替换回原始的 Link 对象结构中。
        要求 original_toc 和 translated_toc 具有完全相同的嵌套和顺序。
        """
        if isinstance(original_toc, (epub.Link, epub.Section)):
            # 如果是 Link 对象，直接更新其 title 属性
            # original_toc 是 Link 对象本身，所以可以直接修改
            original_toc.title = translated_toc
            return original_toc # 返回修改后的 Link 对象（虽然是原地修改，返回方便理解）
        elif isinstance(original_toc, (list, tuple)) and isinstance(translated_toc, list):
            # 如果都是列表，遍历并递归处理每个元素
            for i in range(len(original_toc)):
                # 确保两个结构的长度匹配，否则会有 IndexError
                if i < len(translated_toc):
                    self._update_toc(original_toc[i], translated_toc[i])
            return original_toc # 返回修改后的列表
        else:
            return original_toc

    async def translate_toc(self, book):
        toc_content = self.epub_parser.parse_toc(toc=book.toc)
        translated = await self.translator.translate(json.dumps(toc_content))
        translated = translated.strip()
        translated = json.loads(translated)
        self._update_toc(book.toc, translated)

    async def translate(self, book) -> None:
        """翻译 EPUB 内容"""
        await self.translate_toc(book=book.book)
        # 获取所有可翻译项
        translatable_items = [item for item in book.items if item.is_translatable]
        
        # 创建进度条
        with tqdm(translatable_items, desc="翻译进度", unit="文件") as pbar:
            for item in pbar:
                # 如果启用了断点续传且已处理过，则跳过
                if self.enable_resume and item.file_name in self.processed_files:
                    pbar.set_postfix_str(f"跳过已处理: {item.file_name}")
                    continue
                
                pbar.set_postfix_str(f"正在处理: {item.file_name}")

                parser = 'html.parser'
                if 'nav.xhtml' in item.file_name:
                    parser = 'lxml'
                html_replacer = HTMLReplacer(parser)
                content = html_replacer.replace(item.content)
                chunks = self.html_splitter.split(content)
                translated_chunks = []
                
                # 分块翻译
                for chunk in chunks:
                    chunk.translated = await self.translator.translate(chunk.content)
                    translated_chunks.append(chunk)
                
                item.translated = html_replacer.restore(
                    self.html_builder.build(translated_chunks)
                )
                
                # 标记为已处理
                if self.enable_resume and self.resume:
                    self.resume.mark_file_processed(
                        self.input_epub, 
                        item.file_name
                    )
                    self.processed_files.add(item.file_name)

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

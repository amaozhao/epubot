from typing import List

import ebooklib
from ebooklib import epub

from epubot.schemas.epub import EpubBook, EpubItem, Metadata


class EpubParser:
    path: str

    def __init__(self, path: str):
        self.path = path
        self.book = None

    def _generate_metadata(self, raw_metadata: dict) -> Metadata:
        """
        Converts the raw ebooklib metadata structure into our detailed Metadata schema.
        This is a blocking operation, intended to be run via run_blocking_io.
        Args:
            raw_metadata: The raw metadata dictionary from ebooklib.epub.EpubBook.metadata.
        Returns:
            A populated Metadata schema object.
        """
        metadata = Metadata()
        for ns_uri, ns_data in raw_metadata.items():
            metadata.namespaces[ns_uri] = {}
            for name, values in ns_data.items():
                # Ensure attributes are converted to serializable dictionaries
                metadata.namespaces[ns_uri][name] = [(v[0], dict(v[1])) for v in values]
        return metadata

    def _generate_items(self, book: epub.EpubBook) -> List[EpubItem]:
        items = book.get_items()
        epub_items: List[EpubItem] = []
        for item in items:
            content = item.get_content()
            if item.get_type() in (
                ebooklib.ITEM_DOCUMENT,
                ebooklib.ITEM_NAVIGATION,
            ):
                content = content.decode("utf-8")
            item = EpubItem(
                id=item.id,
                file_name=item.file_name,
                media_type=item.media_type,
                is_linear=item.is_linear,
                manifest=item.manifest,
                content=content,
                item_type=item.get_type(),
            )
            epub_items.append(item)
        return epub_items

    def _generate_version(self, book: epub.EpubBook) -> str:
        version = getattr(book, "EPUB_VERSION", "3.0")
        if callable(version) and not isinstance(version, str):
            version = "3.0"
        return str(version)

    def parse(self):
        book = epub.read_epub(self.path)
        metadata = self._generate_metadata(book.metadata)
        items = self._generate_items(book)
        self.book = EpubBook(
            metadata=metadata,
            items=items,  # Store all resources
            version=self._generate_version(book),
            book=book,
        )
        return self.book

    def parse_toc(self, toc):
        """
        递归地将嵌套结构中的 Link/Section 对象替换为其 title 属性，
        同时保留原始的嵌套（list/tuple）结构。
        """
        if isinstance(toc, (epub.Link, epub.Section)):
            # 如果是 Link/Section 对象，返回其 title
            return toc.title
        elif isinstance(toc, (list, tuple)):
            # 如果是列表，遍历每个元素并递归处理，然后构建新的列表
            return [self.parse_toc(item) for item in toc]
        else:
            # 如果是其他类型（例如字符串、数字等），原样返回
            return toc


if __name__ == "__main__":
    parser = EpubParser("/Users/amaozhao/workspace/epubot/Think-Like-Commoner-2nd.epub")
    parser.parse()

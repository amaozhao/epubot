from typing import List

import ebooklib
from ebooklib import epub

from epubot.schemas.epub import EpubBook, EpubItem


class EpubBuilder:

    def __init__(self, epubook: EpubBook, output: str) -> None:
        self.origin_book = epubook.book
        self.items: List[EpubItem] = epubook.items
        self.book = epub.EpubBook()
        self.output = output

    def build(self) -> None:
        self.book.metadata = self.origin_book.metadata
        self.book.set_language("zh")
        self.book.toc = self.origin_book.toc
        self.book.spine = self.origin_book.spine

        for item in self.items:
            if item.item_type == ebooklib.ITEM_DOCUMENT:
                c = epub.EpubItem(
                    uid=item.id,
                    file_name=item.file_name,
                    media_type=item.media_type,
                    content=item.translated if item.translated else item.content,
                )
            elif item.item_type == ebooklib.ITEM_IMAGE:
                c = epub.EpubImage(
                    uid=item.id,
                    file_name=item.file_name,
                    media_type=item.media_type,
                    content=item.content,
                )
            elif item.item_type == ebooklib.ITEM_NAVIGATION:
                c = epub.EpubNav(
                    uid=item.id,
                    file_name=item.file_name,
                    media_type=item.media_type,
                )
            else:
                c = epub.EpubItem(
                    uid=item.id,
                    file_name=item.file_name,
                    media_type=item.media_type,
                    content=item.content,
                )
            self.book.add_item(c)
        epub.write_epub(
            self.output,
            self.book,
            {"pretty_print": True},
        )


if __name__ == "__main__":
    from epubot.services.epub.parser import EpubParser

    parser = EpubParser("/Users/amaozhao/workspace/epubot/Think-Like-Commoner-2nd.epub")
    parser.parse()
    builder = EpubBuilder(
        parser.book, "/Users/amaozhao/workspace/epubot/Think-Like-Commoner-2nd-zh.epub"
    )
    builder.build()

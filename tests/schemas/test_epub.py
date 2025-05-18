from unittest.mock import MagicMock

from epubot.schemas.epub import EpubInfo, EpubResource, Metadata, Structure


def test_epubresource_creation():
    """Test successful creation of an EpubResource object."""
    epub_resource = EpubResource(
        id="item_1",
        href="OEBPS/text/chapter1.xhtml",
        media_type="application/xhtml+xml",
        item_type=1,  # 假设 1 代表 EbookLib.ITEM_DOCUMENT
        content="<html><body>Chapter 1</body></html>",
    )
    assert epub_resource.id == "item_1"
    assert epub_resource.href == "OEBPS/text/chapter1.xhtml"
    assert epub_resource.media_type == "application/xhtml+xml"
    assert epub_resource.content == "<html><body>Chapter 1</body></html>"
    assert epub_resource.is_translatable == True  # 检查辅助属性


def test_epubinfo_creation():
    """Test successful creation of an EpubInfo object."""
    mock_book_obj = MagicMock()  # Mock the EbookLib.EpubBook object

    # 创建元数据
    metadata = Metadata()
    metadata.namespaces = {
        "http://purl.org/dc/elements/1.1/": {
            "title": [("Test Book", {})],
            "language": [("en", {})],
        }
    }

    # 创建资源
    epub_resource1 = EpubResource(
        id="item_1",
        href="chap1.xhtml",
        media_type="application/xhtml+xml",
        item_type=1,
        content="content1",
    )
    epub_resource2 = EpubResource(
        id="item_2",
        href="chap2.xhtml",
        media_type="application/xhtml+xml",
        item_type=1,
        content="content2",
    )

    # 创建结构
    structure = Structure(
        spines=["chap1.xhtml", "chap2.xhtml"],
        tocs=["chap1.xhtml", "chap2.xhtml"],
    )

    # 创建 EpubInfo
    epub_info = EpubInfo(
        metadata=metadata,
        resources=[epub_resource1, epub_resource2],
        structure=structure,
        version="3.0",
        book_obj=mock_book_obj,
    )

    # 断言
    assert (
        epub_info.metadata.namespaces["http://purl.org/dc/elements/1.1/"]["title"][0][0]
        == "Test Book"
    )
    assert (
        epub_info.metadata.namespaces["http://purl.org/dc/elements/1.1/"]["language"][
            0
        ][0]
        == "en"
    )
    assert len(epub_info.resources) == 2
    assert epub_info.resources[0].id == "item_1"
    assert epub_info.structure.spines == ["chap1.xhtml", "chap2.xhtml"]
    assert epub_info.version == "3.0"
    assert epub_info.book_obj == mock_book_obj


# Test with empty content_files list
def test_epubinfo_empty_resources():
    """Test EpubInfo creation with an empty resources list."""
    mock_book_obj = MagicMock()

    # 创建元数据
    metadata = Metadata()
    metadata.namespaces = {
        "http://purl.org/dc/elements/1.1/": {"title": [("Empty Book", {})]}
    }

    epub_info = EpubInfo(
        metadata=metadata, resources=[], book_obj=mock_book_obj  # 空资源列表
    )

    assert (
        epub_info.metadata.namespaces["http://purl.org/dc/elements/1.1/"]["title"][0][0]
        == "Empty Book"
    )
    assert len(epub_info.resources) == 0
    assert epub_info.book_obj == mock_book_obj


# Test EpubInfo with minimal metadata
def test_epubinfo_minimal_metadata():
    """Test EpubInfo creation with minimal metadata."""
    mock_book_obj = MagicMock()

    # 创建最小元数据
    metadata = Metadata()  # 空的元数据

    epub_info = EpubInfo(metadata=metadata, resources=[], book_obj=mock_book_obj)

    # 断言元数据的 namespaces 是空字典
    assert epub_info.metadata.namespaces == {}
    assert len(epub_info.resources) == 0
    assert epub_info.book_obj == mock_book_obj

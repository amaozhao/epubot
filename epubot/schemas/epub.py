from typing import Any, Dict, List, Optional, Tuple, Union

import ebooklib
from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Represents the detailed metadata structure from EbookLib."""

    namespaces: Dict[str, Dict[str, List[Tuple[str, Dict[str, str]]]]] = Field(
        default_factory=dict
    )


class EpubItem(BaseModel):
    id: str
    file_name: str
    media_type: str
    content: Union[bytes, str]
    translated: Optional[str] = None
    is_linear: bool
    manifest: bool
    item_type: int
    is_translatable: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        if self.item_type in (ebooklib.ITEM_DOCUMENT, ebooklib.ITEM_NAVIGATION):
            self.is_translatable = True


class EpubBook(BaseModel):
    items: List[EpubItem] = Field(default_factory=list)  # All resource items
    version: str = "3.0"  # EPUB version
    book: Any

    class Config:
        arbitrary_types_allowed = True  # Allow EbookLib.EpubBook type

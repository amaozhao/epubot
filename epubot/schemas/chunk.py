from typing import Optional

from pydantic import BaseModel


class Chunk(BaseModel):
    id: str
    file_id: str
    content: str
    translated: Optional[str] = None
    tokens: Optional[int] = None
    retry_count: int = 0
    # review_status: Optional[str] = None
    # review_issues: Optional[List[str]] = None
    # suggested_correction: Optional[str] = None

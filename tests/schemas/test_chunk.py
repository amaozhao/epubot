# tests/schemas/test_chunk.py

from epubot.schemas.chunk import Chunk


def test_chunk_creation():
    """Test successful creation of a Chunk object."""
    chunk = Chunk(
        chunk_id="test-chunk-1",
        file_id="file-1",
        origin="This is the original text.",
        tokens=10,
    )
    assert chunk.chunk_id == "test-chunk-1"
    assert chunk.file_id == "file-1"
    assert chunk.origin == "This is the original text."
    assert chunk.translated is None
    assert chunk.tokens == 10
    assert chunk.retry_count == 0
    assert chunk.review_status is None
    assert chunk.review_issues is None
    assert chunk.suggested_correction is None


def test_chunk_with_translated_text():
    """Test Chunk creation with translated text."""
    chunk = Chunk(
        chunk_id="test-chunk-2",
        file_id="file-2",
        origin="Original text.",
        translated="Translated text.",
        tokens=5,
    )
    assert chunk.translated == "Translated text."


def test_chunk_with_review_status():
    """Test Chunk creation with review status and issues."""
    chunk = Chunk(
        chunk_id="test-chunk-3",
        file_id="file-3",
        origin="Another original.",
        translated="Another translated.",
        review_status="FAIL_RETRY",
        review_issues=["Fluency low"],
        suggested_correction="Suggested fix.",
    )
    assert chunk.review_status == "FAIL_RETRY"
    assert chunk.review_issues == ["Fluency low"]
    assert chunk.suggested_correction == "Suggested fix."


def test_chunk_default_values():
    """Test default values for optional fields."""
    chunk = Chunk(chunk_id="test-chunk-4", file_id="file-4", origin="Simple text.")
    assert chunk.translated is None
    assert chunk.tokens is None
    assert chunk.retry_count == 0
    assert chunk.review_status is None
    assert chunk.review_issues is None
    assert chunk.suggested_correction is None


# Example of testing Pydantic validation (optional but good practice)
# def test_chunk_invalid_data():
#     """Test that invalid data raises validation error."""
#     with pytest.raises(ValueError): # Or Pydantic ValidationError
#         Chunk(chunk_id=123, file_id="file-5", origin="Invalid ID") # chunk_id should be string

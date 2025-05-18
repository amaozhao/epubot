# tests/schemas/test_review.py

from epubot.schemas.review import ReviewResult


def test_reviewresult_creation_pass():
    """Test successful creation of a ReviewResult object with PASS status."""
    review_result = ReviewResult(status="PASS", issues=[])
    assert review_result.status == "PASS"
    assert review_result.issues == []
    assert review_result.suggested_correction is None


def test_reviewresult_creation_fail_retry():
    """Test ReviewResult creation with FAIL_RETRY status and issues."""
    review_result = ReviewResult(
        status="FAIL_RETRY",
        issues=["Fluency too low", "Term not preserved"],
        suggested_correction="Here is a suggested fix.",
    )
    assert review_result.status == "FAIL_RETRY"
    assert review_result.issues == ["Fluency too low", "Term not preserved"]
    assert review_result.suggested_correction == "Here is a suggested fix."


def test_reviewresult_creation_fail_manual():
    """Test ReviewResult creation with FAIL_MANUAL status and issues."""
    review_result = ReviewResult(
        status="FAIL_MANUAL", issues=["Placeholder integrity compromised"]
    )
    assert review_result.status == "FAIL_MANUAL"
    assert review_result.issues == ["Placeholder integrity compromised"]
    assert (
        review_result.suggested_correction is None
    )  # Manual failures might not have suggestions


# Test with invalid status (optional Pydantic validation test)
# def test_reviewresult_invalid_status():
#     """Test that invalid status raises validation error."""
#     with pytest.raises(ValueError): # Or Pydantic ValidationError
#         ReviewResult(status="INVALID_STATUS", issues=[])

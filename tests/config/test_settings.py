# tests/config/test_settings.py

import os

import pytest

from epubot.config.settings import Settings


# Define a fixture to manage environment variables for testing
@pytest.fixture(scope="function")
def clear_env_vars():
    """Clears relevant environment variables before each test."""
    original_env = os.environ.copy()
    keys_to_clear = [
        "DEEPSEEK_API_KEY",
        "MISTRAL_API_KEY",
        "AGENT_LLM_MODEL_FOR_DECISION",
        "TRANSLATION_LLM_MODEL",
        "REVIEW_LLM_MODEL",
        "MAX_TRANSLATION_RETRIES",
        "REVIEW_FLUENCY_THRESHOLD",
        "SPECIFIC_TERMS_TO_PRESERVE",
        "OUTPUT_DIR",
        "LOG_LEVEL",
        "LOG_FILE",
        "LOG_JSON_OUTPUT",
    ]
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]
    yield
    # Restore original environment variables after the test
    os.environ.clear()
    os.environ.update(original_env)


# Use the fixture in tests that modify environment variables
def test_settings_default_values(clear_env_vars):
    """Test that settings load with default values when no env vars are set."""
    # Re-instantiate Settings after clearing env vars to ensure defaults are loaded
    default_settings = Settings()

    assert default_settings.deepseek_api_key is not None
    assert default_settings.mistral_api_key is not None
    assert default_settings.agent_llm_model_for_decision == "deepseek/deepseek-coder"
    assert default_settings.translation_llm_model == "mistral/mistral-large-latest"
    assert default_settings.review_llm_model == "deepseek/deepseek-coder"
    assert default_settings.max_translation_retries == 3
    assert default_settings.review_fluency_threshold == 0.75
    assert default_settings.specific_terms_to_preserve == [
        "Agno Agent",
        "EPUB",
        "HTML",
        "NCX",
        "Python",
        "DeepSeek",
        "Mistral",
    ]
    assert default_settings.output_dir == "translated_epubs"
    assert default_settings.log_level == "INFO"
    assert default_settings.log_file == "app.log"
    assert default_settings.log_json_output is False


def test_settings_load_from_env_vars(clear_env_vars):
    """Test that settings load correctly from environment variables."""
    os.environ["DEEPSEEK_API_KEY"] = "env_deepseek_key"
    os.environ["MISTRAL_API_KEY"] = "env_mistral_key"
    os.environ["TRANSLATION_LLM_MODEL"] = "test/model"
    os.environ["MAX_TRANSLATION_RETRIES"] = "5"
    os.environ["REVIEW_FLUENCY_THRESHOLD"] = "0.9"
    os.environ["SPECIFIC_TERMS_TO_PRESERVE"] = '["TermA", "TermB", "TermC"]'
    os.environ["OUTPUT_DIR"] = "output/test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_JSON_OUTPUT"] = "True"  # Pydantic handles boolean conversion

    # Re-instantiate Settings to load from env vars
    env_settings = Settings()

    assert env_settings.deepseek_api_key == "env_deepseek_key"
    assert env_settings.mistral_api_key == "env_mistral_key"
    assert env_settings.translation_llm_model == "test/model"
    assert env_settings.max_translation_retries == 5
    assert env_settings.review_fluency_threshold == 0.9
    assert env_settings.specific_terms_to_preserve == ["TermA", "TermB", "TermC"]
    assert env_settings.output_dir == "output/test"
    assert env_settings.log_level == "DEBUG"
    assert env_settings.log_json_output is True


# Note: Testing .env file loading requires creating a temporary .env file,
# which adds complexity. For this example, we focus on default and env var loading.
# A real test suite might include a fixture to create/clean up a temporary .env file.

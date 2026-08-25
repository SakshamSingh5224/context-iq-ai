import pytest
from unittest.mock import patch, MagicMock

from services.copilot import (
    generate_intervention_strategy,
    CopilotError,
)

def test_generate_intervention_strategy_success(monkeypatch):
    # Set a fake API key for the test
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key")

    # Create a fake response that mimics what Gemini would return
    fake_response = MagicMock()
    fake_response.text = "1. Secure the perimeter.\n2. Halt external work.\n3. Deploy backup systems."

    # Intercept the call to the Gemini model
    with patch("services.copilot.genai.GenerativeModel") as mock_model_class:
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = fake_response
        mock_model_class.return_value = mock_model_instance

        result = generate_intervention_strategy(
            operation_title="Inspect cold-storage unit 4",
            risk_level="HIGH",
            weather_summary={"temperature_2m": 35.0, "precipitation": 10.0}
        )

        assert "Secure the perimeter." in result
        mock_model_class.assert_called_once_with("gemini-1.5-flash")
        mock_model_instance.generate_content.assert_called_once()

def test_missing_api_key_raises_error(monkeypatch):
    # Ensure the environment variable is temporarily removed
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(CopilotError, match="GEMINI_API_KEY environment variable is missing"):
        generate_intervention_strategy(
            operation_title="Test Operation",
            risk_level="LOW",
            weather_summary={}
        )

import os
import pytest
from unittest.mock import patch, MagicMock
from services.copilot import generate_intervention_strategy, CopilotError

@patch.dict(os.environ, {"GROQ_API_KEY": "fake_test_key"})
@patch("services.copilot.Groq")
def test_generate_intervention_strategy_success(mock_groq_class):
    # Setup mock Groq client
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Mock the chat completions return object
    mock_message = MagicMock()
    mock_message.message.content = "1. Test step 1\n2. Test step 2\n3. Test step 3"
    mock_completion = MagicMock()
    mock_completion.choices = [mock_message]
    mock_client.chat.completions.create.return_value = mock_completion
    
    # Call strategy generator
    strategy = generate_intervention_strategy(
        operation_title="Data Center Transformer Maintenance",
        risk_level="medium",
        weather_summary={"temp": 28.2}
    )
    
    assert "Test step 1" in strategy
    mock_client.chat.completions.create.assert_called_once()

@patch.dict(os.environ, {}, clear=True)
def test_missing_api_key():
    with pytest.raises(CopilotError, match="GROQ_API_KEY environment variable is missing."):
        generate_intervention_strategy("Test Op", "HIGH", {})

@patch.dict(os.environ, {"GROQ_API_KEY": "fake_test_key"})
@patch("services.copilot.Groq")
def test_groq_api_failure(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("Model down")
    
    with pytest.raises(CopilotError, match="Groq API request failed: Model down"):
        generate_intervention_strategy("Test Op", "HIGH", {})

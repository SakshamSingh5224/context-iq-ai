"""
Gemini AI Copilot service for ContextIQ.
Generates actionable insights based on deterministic risk scores and external data.
"""

import os
import google.generativeai as genai

class CopilotError(RuntimeError):
    """Raised when the AI copilot fails to generate a response."""

def generate_intervention_strategy(
    operation_title: str,
    risk_level: str,
    weather_summary: dict
) -> str:
    """
    Calls Gemini to recommend an intervention strategy based on the operation's context.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise CopilotError("GEMINI_API_KEY environment variable is missing.")

    genai.configure(api_key=api_key)
    
    prompt = (
        f"You are an AI Copilot for an operational risk platform.\n"
        f"Operation: {operation_title}\n"
        f"Assessed Risk Level: {risk_level}\n"
        f"Current Weather Context: {weather_summary}\n\n"
        f"Provide a brief, 3-step intervention strategy to mitigate potential risks. Keep it concise."
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        raise CopilotError(f"Generative AI request failed: {exc}") from exc

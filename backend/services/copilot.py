"""
AI Copilot service for ContextIQ.
Generates actionable insights based on deterministic risk scores and external data using Groq.
"""

import os
from groq import Groq

class CopilotError(RuntimeError):
    """Raised when the AI copilot fails to generate a response."""

def generate_intervention_strategy(
    operation_title: str,
    risk_level: str,
    weather_summary: dict
) -> str:
    """
    Calls Llama 3 via Groq to recommend an intervention strategy based on the context.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise CopilotError("GROQ_API_KEY environment variable is missing.")

    prompt = (
        f"You are an AI Copilot for an operational risk platform.\n"
        f"Operation: {operation_title}\n"
        f"Assessed Risk Level: {risk_level}\n"
        f"Current Weather Context: {weather_summary}\n\n"
        f"Provide a brief, 3-step intervention strategy to mitigate potential risks. Keep it concise."
    )

    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-20b",
        )
        return chat_completion.choices[0].message.content
    except Exception as exc:
        raise CopilotError(f"Groq API request failed: {exc}") from exc

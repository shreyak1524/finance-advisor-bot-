"""
AI service.

Wraps calls to an external AI provider (OpenAI or Gemini) using an API key
from the environment. If no key is configured, or the API call fails for
any reason (network error, invalid key, quota, etc.), functions in this
module return None so the caller can fall back to the rule-based
recommendation_service instead. The rest of the app never has to know
which path was used.
"""

import json
import requests
from flask import current_app


def is_ai_configured():
    """True only if both a provider and an API key are set."""
    provider = current_app.config.get("AI_PROVIDER", "")
    api_key = current_app.config.get("AI_API_KEY", "")
    return bool(provider) and bool(api_key)


def _build_context_prompt(context, question):
    """Turn the user's financial context dict into a compact text prompt."""
    return (
        "You are a friendly personal finance assistant helping an individual "
        "understand their own budget. Use the financial data below to answer "
        "the user's question with specific, practical, and encouraging advice. "
        "Keep the answer under 150 words and do not give professional legal or "
        "investment advice.\n\n"
        f"Monthly income: ₹{context.get('income', 0):,.0f}\n"
        f"Total expenses: ₹{context.get('expenses', 0):,.0f}\n"
        f"Savings: ₹{context.get('savings', 0):,.0f}\n"
        f"Savings rate: {context.get('savings_rate', 0)}%\n"
        f"Category-wise expenses: {json.dumps(context.get('category_breakdown', {}))}\n"
        f"Budget status: {json.dumps(context.get('budget_status', []))}\n"
        f"Financial goals: {json.dumps(context.get('goals', []))}\n\n"
        f"User question: {question}"
    )


def _call_openai(prompt, api_key):
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.6,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # Any failure (network, auth, parsing) -> signal caller to use fallback
        return None


def _call_gemini(prompt, api_key):
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={api_key}"
        )
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None


def get_ai_response(context, question):
    """
    Try to get a response from the configured AI provider.
    Returns the AI's text response, or None if unavailable/failed
    (caller should fall back to recommendation_service in that case).
    """
    if not is_ai_configured():
        return None

    provider = current_app.config.get("AI_PROVIDER", "")
    api_key = current_app.config.get("AI_API_KEY", "")
    prompt = _build_context_prompt(context, question)

    if provider == "openai":
        return _call_openai(prompt, api_key)
    if provider == "gemini":
        return _call_gemini(prompt, api_key)
    return None

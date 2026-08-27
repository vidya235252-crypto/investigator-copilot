import os
import requests
from dotenv import load_dotenv
from ai import prompts, fallback

load_dotenv()

def generate_summary(case: dict) -> str:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return fallback.generate_fallback_summary(case)

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 400,
                "system": prompts.SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": prompts.build_user_prompt(case)}
                ],
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]
    except Exception:
        return fallback.generate_fallback_summary(case)
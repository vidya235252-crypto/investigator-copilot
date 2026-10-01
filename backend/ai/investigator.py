import logging
import requests
from ai import prompts, fallback

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b-instruct"


def generate_summary(case: dict) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": prompts.SYSTEM_PROMPT},
                    {"role": "user", "content": prompts.build_user_prompt(case)},
                ],
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=120,
        )

        if not response.ok:
            raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")

        data = response.json()

        if "message" not in data or "content" not in data["message"]:
            raise RuntimeError(f"Unexpected Ollama response: {data}")

        return data["message"]["content"]

    except Exception:
        logger.exception("Ollama failed for %s, using fallback", case.get("case_id"))
        return fallback.generate_fallback_summary(case)
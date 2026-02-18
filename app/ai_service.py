import os
from dotenv import load_dotenv
from openai import OpenAI

from app.budget import check_and_add

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
MAX_TOTAL_TOKENS_PER_REQUEST = int(os.getenv("MAX_TOTAL_TOKENS_PER_REQUEST", "1200"))

def generate_reply(message: str, api_key: str):
    message = (message or "").strip()
    if not message:
        raise RuntimeError("Empty message")

    api_key = (api_key or "").strip()
    if not api_key:
        raise RuntimeError("Missing X-API-Key header (OpenAI API key)")

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful business assistant."},
                {"role": "user", "content": message},
            ],
            temperature=0.4,
            max_tokens=300,
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI error: {str(e)}")

    total = response.usage.total_tokens

    if total > MAX_TOTAL_TOKENS_PER_REQUEST:
        raise RuntimeError(f"Per-request token limit exceeded ({total} > {MAX_TOTAL_TOKENS_PER_REQUEST})")

    used_today, daily_budget = check_and_add(total)

    return {
        "reply": response.choices[0].message.content,
        "model": MODEL_NAME,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": total,
        "daily_tokens_used": used_today,
        "daily_token_budget": daily_budget,
    }

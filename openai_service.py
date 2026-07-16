import json
from typing import Optional

from openai import AsyncOpenAI

from config import GROQ_API_KEY, GROQ_MODEL

# Groq предоставляет OpenAI-совместимый API — используем тот же клиент,
# просто меняем base_url и ключ.
client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


async def check_word_exists(word: str) -> dict:
    """
    Просит ИИ проверить, существует ли слово в русском языке.

    Возвращает словарь {"valid": bool, "reason": str}.
    """
    prompt = (
        f'Слово: "{word}".\n'
        "Проверь, является ли это существующим словом русского языка "
        "(существительное, в начальной форме — именительный падеж, "
        "единственное число, не имя собственное, не аббревиатура, без опечаток). "
        "Ответь СТРОГО в формате JSON без markdown и без пояснений вне JSON: "
        '{"valid": true или false, "reason": "короткое объяснение на русском"}'
    )
    try:
        resp = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = json.loads(resp.choices[0].message.content)
        return {"valid": bool(data.get("valid")), "reason": data.get("reason", "")}
    except Exception as e:
        return {"valid": False, "reason": f"ошибка проверки: {e}"}


async def generate_next_word(letter: str, used_words: list[str]) -> Optional[str]:
    """
    Просит ИИ придумать существующее русское слово, начинающееся на
    заданную букву и не встречавшееся ранее в used_words.
    """
    used_str = ", ".join(used_words[-30:]) if used_words else "нет"
    prompt = (
        f'Придумай ОДНО существующее слово русского языка '
        f'(существительное, именительный падеж, единственное число, '
        f'не имя собственное), которое начинается на букву "{letter}".\n'
        f"Слово не должно совпадать с уже использованными: {used_str}.\n"
        'Ответь СТРОГО в формате JSON без markdown: {"word": "слово"}'
    )
    try:
        resp = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        data = json.loads(resp.choices[0].message.content)
        word = (data.get("word") or "").strip().lower()
        return word or None
    except Exception:
        return None

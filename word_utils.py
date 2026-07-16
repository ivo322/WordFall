import re
from typing import Optional

CYRILLIC_RE = re.compile(r'^[а-яё]+$', re.IGNORECASE)

# Буквы, на которые не бывает (почти) слов в начальной форме —
# для них берём букву ПЕРЕД ними
EXCLUDED_LETTERS = {'ь', 'ы', 'ъ'}


def is_cyrillic_word(word: str) -> bool:
    """Проверяет, что слово состоит только из русских букв."""
    return bool(CYRILLIC_RE.fullmatch(word.strip()))


def get_chain_letter(word: str) -> Optional[str]:
    """
    Определяет букву, на которую должно начинаться следующее слово в цепочке.

    Берём последнюю букву слова. Если это ь, ы или ъ — отступаем на букву
    левее (и повторяем проверку), так как слов на эти буквы почти нет.

    Возвращает None, если подходящую букву найти не удалось
    (например, слово целиком состоит из таких букв).
    """
    w = word.strip().lower()
    idx = len(w) - 1
    while idx >= 0 and w[idx] in EXCLUDED_LETTERS:
        idx -= 1
    if idx < 0:
        return None
    return w[idx]

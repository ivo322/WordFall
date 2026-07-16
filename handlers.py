from typing import Optional

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import game_keyboard, menu_keyboard
from openai_service import check_word_exists, generate_next_word
from states import GameStates
from word_utils import get_chain_letter, is_cyrillic_word

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(

        "Нажми «Играть», чтобы начать.",
        reply_markup=menu_keyboard(),
    )


@router.callback_query(F.data == "play")
async def cb_play(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(GameStates.waiting_first_word)
    await state.update_data(used_words=[])
    await call.message.edit_text("Напишите слово для начала")
    await call.answer()


@router.callback_query(F.data == "restart")
async def cb_restart(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(GameStates.waiting_first_word)
    await state.update_data(used_words=[])
    await call.message.edit_text("Начинаем заново! Напишите слово для начала")
    await call.answer()


@router.callback_query(F.data == "report_error")
async def cb_report_error(call: CallbackQuery, state: FSMContext):
    # Здесь можно дополнительно логировать last_ai_word в файл/БД для анализа ошибок ИИ
    await call.answer("Спасибо, ошибка зафиксирована!", show_alert=True)


async def _validate_user_word(
    message: Message, state: FSMContext, expected_letter: Optional[str]
) -> Optional[str]:
    """
    Полная проверка слова игрока. При ошибке сама отправляет сообщение
    с описанием проблемы и возвращает None. При успехе возвращает букву,
    на которую должно начинаться слово ИИ.
    """
    word = message.text.strip().lower()

    # 1. Только русский алфавит
    if not is_cyrillic_word(word):
        await message.answer("Слово должно состоять только из русских букв. Попробуйте ещё раз:")
        return None

    # 2. Слово должно начинаться на нужную букву (если это не первый ход)
    if expected_letter and word[0] != expected_letter:
        await message.answer(
            f'Слово должно начинаться на букву "{expected_letter}".:'
        )
        return None

    # 3. Слово не должно повторяться
    data = await state.get_data()
    used_words = data.get("used_words", [])
    if word in used_words:
        await message.answer("Это слово уже было использовано.")
        return None

    # 4. Проверка существования слова через ИИ
    result = await check_word_exists(word)
    if not result["valid"]:
        await message.answer(
            f"ИИ считает, что такого слова нет"
        )
        return None

    used_words.append(word)
    await state.update_data(used_words=used_words)

    # 5. Буква для следующего слова (с учётом ь/ы/ъ)
    return get_chain_letter(word)


async def _ai_turn(message: Message, state: FSMContext, chain_letter: Optional[str]):
    """Ход ИИ: генерирует слово на нужную букву и отправляет игроку."""
    data = await state.get_data()
    used_words = data.get("used_words", [])

    if chain_letter is None:
        await message.answer(
            "Win",
            reply_markup=game_keyboard(),
        )
        await state.set_state(None)
        return

    ai_word = await generate_next_word(chain_letter, used_words)
    if not ai_word or not is_cyrillic_word(ai_word) or ai_word[0] != chain_letter:
        await message.answer(
            "ИИ не смог придумать слово.",
            reply_markup=game_keyboard(),
        )
        await state.set_state(None)
        return

    used_words.append(ai_word)
    next_letter = get_chain_letter(ai_word)
    await state.update_data(used_words=used_words, last_ai_word=ai_word, expected_letter=next_letter)

    if next_letter is None:
        await message.answer(
            f'Моё слово: "{ai_word}"\nНа эту букву продолжить не получится. Я выиграл!',
            reply_markup=game_keyboard(),
        )
        await state.set_state(None)
        return

    await state.set_state(GameStates.waiting_user_word)
    await message.answer(
        f'Моё слово: "{ai_word}"\nВаше слово на букву "{next_letter}":',
        reply_markup=game_keyboard(),
    )


@router.message(GameStates.waiting_first_word)
async def handle_first_word(message: Message, state: FSMContext):
    chain_letter = await _validate_user_word(message, state, expected_letter=None)
    if chain_letter is None:
        return
    await _ai_turn(message, state, chain_letter)


@router.message(GameStates.waiting_user_word)
async def handle_user_word(message: Message, state: FSMContext):
    data = await state.get_data()
    expected_letter = data.get("expected_letter")
    chain_letter = await _validate_user_word(message, state, expected_letter=expected_letter)
    if chain_letter is None:
        return
    await _ai_turn(message, state, chain_letter)

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Играть", callback_data="play")
    return kb.as_markup()


def game_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Ошибка ИИ", callback_data="report_error")
    kb.button(text="Играть заново", callback_data="restart")
    kb.adjust(2)
    return kb.as_markup()

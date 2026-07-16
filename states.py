from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    waiting_first_word = State()   # ждём первое слово от игрока
    waiting_user_word = State()    # ждём слово-продолжение от игрока

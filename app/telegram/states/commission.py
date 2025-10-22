from aiogram.fsm.state import StatesGroup, State


class CommissionAddFSM(StatesGroup):
    ask_title = State()
    ask_description = State()

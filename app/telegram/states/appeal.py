from aiogram.fsm.state import StatesGroup, State


class AppealFSM(StatesGroup):
    choose_commission = State()
    ask_contact = State()
    ask_text = State()
    ask_file = State()
    done = State()

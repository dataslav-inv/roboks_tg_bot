from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    parent_name = State()
    child_name = State()
    child_age = State()
    course = State()
    phone = State()
    preferred_time = State()
    confirm = State()
from aiogram.fsm.state import State, StatesGroup

class AdminSettings(StatesGroup):
    waiting_for_text = State()
    waiting_for_late_btns = State()
    waiting_for_group_name = State()
    waiting_for_educator_id = State()

class AdminGallery(StatesGroup):
    waiting_for_media = State()

class AdminBroadcast(StatesGroup):
    waiting_for_message = State()

class UserFeedback(StatesGroup):
    waiting_for_feedback = State()

class UserVacancy(StatesGroup):
    waiting_for_resume = State()

class AdminCameraEdit(StatesGroup):
    waiting_for_url = State()

class AdminFAQEdit(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()

class UserRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

class UserEducatorContact(StatesGroup):
    waiting_for_group = State()
    waiting_for_child_name = State()
    waiting_for_parent_role = State()
    waiting_for_message = State()

class UserPoll(StatesGroup):
    waiting_for_feedback = State()


class UserAttendance(StatesGroup):
    waiting_for_reason = State()
    waiting_for_late_time = State()








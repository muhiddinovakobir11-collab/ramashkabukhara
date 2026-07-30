from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from keyboards.reply_keyboards import contact_keyboard, cancel_keyboard
from keyboards.inline_keyboards import main_inline_menu
from config import ADMIN_ID

router = Router()

# Ro'yxatdan o'tish holatlari
class Registration(StatesGroup):
    child_name = State()
    child_age = State()
    parent_phone = State()

@router.callback_query(F.data == "register")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Ro'yxatdan o'tish uchun quyidagi ma'lumotlarni kiriting.\n\n"
        "Farzandingizning ism va familiyasini kiriting:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(Registration.child_name)
    await callback.answer()

@router.message(F.text == "⬅️ Bekor qilish")
async def cancel_registration(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ro'yxatdan o'tish bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Bosh menyu:", reply_markup=main_inline_menu(message.from_user.id))

@router.message(Registration.child_name)
async def process_child_name(message: Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer(
        "Farzandingiz necha yoshda? (Masalan: 4)",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(Registration.child_age)

@router.message(Registration.child_age)
async def process_child_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, yoshni raqamlarda kiriting:")
        return

    await state.update_data(child_age=message.text)
    await message.answer(
        "Bog'lanishimiz uchun telefon raqamingizni yuboring:",
        reply_markup=contact_keyboard()
    )
    await state.set_state(Registration.parent_phone)

@router.message(Registration.parent_phone)
async def process_parent_phone(message: Message, state: FSMContext):
    # Raqamni tekshirish
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    data = await state.get_data()
    child_name = data.get('child_name')
    child_age = data.get('child_age')

    # Foydalanuvchiga tasdiq
    await message.answer(
        "✅ Arizangiz muvaffaqiyatli qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("Bosh menyu:", reply_markup=main_inline_menu())

    # Adminga yuborish
    if ADMIN_ID:
        admin_text = (
            f"🆕 **Yangi ariza kelib tushdi!**\n\n"
            f"👤 Farzand ismi: {child_name}\n"
            f"🎂 Yoshi: {child_age}\n"
            f"📞 Ota-ona raqami: {phone}\n"
            f"💬 Telegram profil: @{message.from_user.username if message.from_user.username else 'yoq'}"
        )
        try:
            await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
        except Exception as e:
            pass # Admin id noto'g'ri bo'lsa yoki botni block qilgan bo'lsa
            
    await state.clear()

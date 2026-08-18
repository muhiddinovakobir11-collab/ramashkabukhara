from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputMediaVideo, ReplyKeyboardRemove
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from states import UserFeedback, UserVacancy, UserRegistration
from keyboards.inline_keyboards import (back_keyboard, location_keyboard, payment_groups_menu, 
                                        main_inline_menu, user_cameras_menu, user_food_days_menu, 
                                        user_faqs_menu, user_faq_back_menu)
from keyboards.reply_keyboards import contact_keyboard
from config import ADMIN_ID, START_VIDEO_ID
import re
from datetime import datetime, timedelta

def parse_time_to_delta(time_str: str):
    time_str = time_str.lower()
    minutes = 0
    m_min = re.search(r'(\d+)\s*(minut|daqiqa|m)', time_str)
    if m_min:
        minutes += int(m_min.group(1))
    m_hour = re.search(r'(\d+)\s*(soat|s)', time_str)
    if m_hour:
        minutes += int(m_hour.group(1)) * 60
    if minutes > 0:
        return timedelta(minutes=minutes)
    return None
import database
import datetime
import asyncio

router = Router()

@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.reply(f"Sizning Telegram ID raqamingiz:\n\n<code>{message.from_user.id}</code>\n\nShu raqamni ustiga bosing, nusxa olinadi.", parse_mode="HTML")


async def edit_message_safe(message: Message, text: str, reply_markup):
    try:
        if message.video:
            await message.edit_caption(caption=text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        pass

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    user = message.from_user
    user_id = user.id
    is_new = await database.add_user(user.id, user.username, user.full_name)
    
    # Adminga faqat BOSHQA yangi odamlar kirganda xabar berish
    if is_new and ADMIN_ID and str(user.id) != str(ADMIN_ID):
        try:
            await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🆕 <b>Yangi foydalanuvchi!</b>\n"
                     f"Ismi: {user.full_name}\n"
                     f"Username: @{user.username if user.username else 'yoq'}\n"
                     f"ID: <code>{user.id}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass

    # Check user auth status
    db_user = await database.get_user(user_id)
    status = db_user.get("status", "pending") if db_user else "pending"
    
    if str(user_id) != str(ADMIN_ID) and status != "approved":
        if status == "rejected":
            await message.answer("❌ <b>Sizning arizangiz ma'muriyat tomonidan rad etilgan.</b>\n\nQaytadan ariza yuborish uchun Ism va Familiyangizni kiriting:", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("👋 <b>Xush kelibsiz!</b>\n\nBotdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\nIltimos, <b>Ism va Familiyangizni</b> kiriting:", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserRegistration.waiting_for_name)
        return

    # Eski reply klaviaturani o'chirish uchun xabarni yuboramiz va UNI O'CHIRMAYMIZ
    await message.answer("👋 Xush kelibsiz! Barcha kerakli bo'limlar quyidagi tugmalarda joylashgan:", reply_markup=ReplyKeyboardRemove())

    # Video va Matn jo'natish
    caption_text = (
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        f"Xususiy bog'chamizning rasmiy botiga xush kelibsiz.\n\n"
        f"Botdan foydalanishingiz mumkin 😊"
    )

    if START_VIDEO_ID:
        try:
            await message.answer_video(
                video=START_VIDEO_ID, 
                caption=caption_text, 
                reply_markup=main_inline_menu(message.from_user.id)
            )
        except Exception:
            await message.answer(caption_text, reply_markup=main_inline_menu(message.from_user.id))
    else:
        # Agar video_id berilmagan bo'lsa, faqat matn yuboriladi
        await message.answer(caption_text, reply_markup=main_inline_menu(message.from_user.id))

@router.callback_query(F.data == "cameras")
async def cameras_menu(callback: CallbackQuery):
    cameras = await database.get_active_cameras()
    if not cameras:
        default_text = (
            "🎥 <b>Onlayn Kuzatuv Kameralari</b>\n\n"
            "Farzandingiz xavfsizligi va uning kun davomida nimalar bilan mashg'ul ekanligi siz uchun muhimligini bilamiz!\n\n"
            "Ayni paytda kameralar admin tomonidan yoqilmagan. Login va parolni bog'cha ma'muriyatidan shaxsan olishingiz mumkin."
        )
        await send_section_media(callback, "text_cameras", default_text, back_keyboard())
    else:
        text = "🎥 <b>Onlayn Kameralar</b>\n\nQuyidagi kameralardan birini tanlab ustiga bosing:"
        await edit_message_safe(callback.message, text, user_cameras_menu(cameras))
    await callback.answer()

@router.callback_query(F.data == "psychologist")
async def psychologist_menu(callback: CallbackQuery):
    default_text = (
        "🧠 <b>Psixolog Maslahati</b>\n\n"
        "Bolaning bog'chaga ilk bor kelishida uning psixologik holatini to'g'ri baholash muhim.\n\n"
        "Bizning malakali psixologimiz har bir bola bilan individual shug'ullanib, ulardagi iqtidorlarni ro'yobga chiqarish va jamiyatga moslashishiga yordam beradi. \n\n"
        "<i>(Psixolog qabuli uchun ma'muriyatga uchrashing)</i>"
    )
    await send_section_media(callback, "text_psychologist", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "birthdays")
async def birthdays_menu(callback: CallbackQuery):
    default_text = (
        "🎂 <b>Tug'ilgan kunlar!</b>\n\n"
        "Ushbu oyda bog'chamizda quvonchli kunlar ko'p! Quyidagi bolajonlarimizni tug'ilgan kunlari bilan tabriklaymiz: 🎉\n\n"
        "1. Ali (Katta guruh) - 5-Sentyabr\n"
        "2. Ziyoda (O'rta guruh) - 12-Sentyabr\n\n"
        "<i>(Sizning ham farzandingiz shu ro'yxatdan joy oladi!)</i>"
    )
    await send_section_media(callback, "text_birthdays", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "events")
async def events_menu(callback: CallbackQuery):
    default_text = (
        "🎈 <b>Bayramlar va Tadbirlar</b>\n\n"
        "Kelayotgan bayramlar uchun maxsus ertaliklarga tayyorgarlik ko'rilmoqda!\n\n"
        "Tez orada ushbu sahifada bayram dasturlari, bolalar uchun ssenariylar va kiyimlar bo'yicha ma'lumotlar e'lon qilinadi."
    )
    await send_section_media(callback, "text_events", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "achievements")
async def achievements_menu(callback: CallbackQuery):
    default_text = (
        "🏆 <b>Yutuqlarimiz va Litsenziya</b>\n\n"
        "Bizning bog'chamiz O'zbekiston Respublikasi Maktabgacha ta'lim vazirligi tomonidan berilgan rasmiy <b>Litsenziyaga</b> ega (№123456).\n\n"
        "Shuningdek, tarbiyachilarimiz turli ko'rik tanlovlarda qatnashib, oliy o'rinlarni egallab kelmoqdalar. Biz bilan farzandingiz ishonchli qo'llarda!"
    )
    await send_section_media(callback, "text_achievements", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "dress_code")
async def dress_code_menu(callback: CallbackQuery):
    default_text = (
        "👗 <b>Bog'cha Formasi va Kiyim-kechak</b>\n\n"
        "Farzandingiz bog'chada o'zini qulay his qilishi uchun quyidagilarga e'tibor bering:\n\n"
        "• Ichkarida kiyish uchun qulay shippak yoki poyabzal.\n"
        "• Ob-havoga mos, terlatmaydigan paxtali kiyimlar.\n"
        "• Zaxira uchun bitta to'liq kiyim (shkafda turishi uchun)."
    )
    await send_section_media(callback, "text_dress_code", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "registration")
async def registration_menu(callback: CallbackQuery):
    default_text = "👶 Farzandni yozdirish bo'limi tez kunda ishga tushadi!"
    await send_section_media(callback, "text_registration", default_text, back_keyboard())
    await callback.answer()

async def send_section_media_message(message: Message, key: str, default_text: str, markup):
    data = await database.get_setting_media(key, default_text)
    text = data["text"]
    
    try:
        if data["type"] == "photo":
            await message.answer_photo(photo=data["media_id"], caption=text, parse_mode="HTML", reply_markup=markup)
        elif data["type"] == "video":
            await message.answer_video(video=data["media_id"], caption=text, parse_mode="HTML", reply_markup=markup)
        else:
            if START_VIDEO_ID:
                await message.answer_video(video=START_VIDEO_ID, caption=text, parse_mode="HTML", reply_markup=markup)
            else:
                await message.answer(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await message.answer(text, parse_mode="HTML", reply_markup=markup)

@router.message(F.video)
async def get_video_id(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        video_id = message.video.file_id
        await message.reply(f"🎥 <b>Ushbu videoning maxsus ID kodi:</b>\n\n<code>{video_id}</code>\n\nBu kodni nusxalab oling va Render.com da START_VIDEO_ID qilib saqlang.", parse_mode="HTML")

async def send_section_media(callback: CallbackQuery, key: str, default_text: str, markup):
    data = await database.get_setting_media(key, default_text)
    text = data["text"]
    
    try:
        if data["type"] == "photo":
            media = InputMediaPhoto(media=data["media_id"], caption=text, parse_mode="HTML")
            await callback.message.edit_media(media=media, reply_markup=markup)
        elif data["type"] == "video":
            media = InputMediaVideo(media=data["media_id"], caption=text, parse_mode="HTML")
            await callback.message.edit_media(media=media, reply_markup=markup)
        else:
            if START_VIDEO_ID:
                media = InputMediaVideo(media=START_VIDEO_ID, caption=text, parse_mode="HTML")
                await callback.message.edit_media(media=media, reply_markup=markup)
            else:
                await edit_message_safe(callback.message, text, markup)
    except Exception:
        try:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=markup)
        except Exception:
            pass

@router.callback_query(F.data == "services")
async def services_menu(callback: CallbackQuery):
    default_text = (
        "<tg-emoji emoji-id=\"5368324170671202286\">📝</tg-emoji> <b>Xizmatlar va narxlar:</b>\n\n"
        "Barcha xizmatlarimiz sizning farzandingiz uchun eng yaxshi sharoitlarni taqdim etishga qaratilgan.\n\n"
        "<tg-emoji emoji-id=\"5368324170671202286\">👶</tg-emoji> Kichik guruh (2-3 yosh): 1,500,000 so'm/oy\n"
        "<tg-emoji emoji-id=\"5368324170671202286\">🧒</tg-emoji> O'rta guruh (4-5 yosh): 1,500,000 so'm/oy\n"
        "<tg-emoji emoji-id=\"5368324170671202286\">👦</tg-emoji> Katta guruh (6-7 yosh): 1,600,000 so'm/oy\n\n"
        "<tg-emoji emoji-id=\"5368324170671202286\">💡</tg-emoji> <i>Narxlar ichiga 4 mahal ovqat, ingliz tili va mental arifmetika darslari kiritilgan.</i>"
    )
    await send_section_media(callback, "text_services", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "location")
async def location_menu(callback: CallbackQuery):
    default_text = (
        "<tg-emoji emoji-id=\"5368324170671202286\">📍</tg-emoji> <b>Bizning manzilimiz:</b>\n\n"
        "Buxoro shahar, Mustaqillik ko'chasi 1-uy.\n"
        "Mo'ljal: Buxoro markaziy bog'i oldida.\n\n"
        "<tg-emoji emoji-id=\"5368324170671202286\">📞</tg-emoji> <b>Murojaat uchun telefonlar:</b>\n"
        "+998 90 123 45 67\n"
        "+998 93 765 43 21\n\n"
        "✉️ <b>Telegram administrator:</b> @akoshprod"
    )
    await send_section_media(callback, "text_location", default_text, location_keyboard())
    await callback.answer()

@router.callback_query(F.data == "schedule")
async def schedule_menu(callback: CallbackQuery):
    default_text = (
        "<tg-emoji emoji-id=\"5368324170671202286\">🕒</tg-emoji> <b>Kun tartibi:</b>\n\n"
        "08:00 - 08:30 : Bolalarni qabul qilish\n"
        "08:30 - 09:00 : Ertalabki badantarbiya\n"
        "09:00 - 09:30 : Nonushta\n"
        "09:30 - 11:00 : Ta'limiy mashg'ulotlar (Ingliz tili, Logika)\n"
        "11:00 - 12:00 : Ochiq havoda sayr va o'yinlar\n"
        "12:00 - 13:00 : Tushlik\n"
        "13:00 - 15:00 : Kunduzgi uyqu\n"
        "15:00 - 15:30 : Uyqudan uyg'onish, badantarbiya\n"
        "15:30 - 16:00 : Ikkinchi tushlik (Poldnik)\n"
        "16:00 - 17:30 : To'garaklar va erkin o'yinlar\n"
        "17:30 - 18:30 : Ota-onalarga kuzatish"
    )
    await send_section_media(callback, "text_schedule", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "teachers")
async def teachers_menu(callback: CallbackQuery):
    default_text = (
        "👩‍🏫 <b>Tarbiyachilarimiz:</b>\n\n"
        "Bizning bog'chada o'z kasbining ustasi bo'lgan, tajribali va bolajonlarni chin dildan sevadigan tarbiyachilar ishlaydi.\n\n"
        "Ular har bir bolaga individual yondashib, ularning qobiliyatlarini ro'yobga chiqarishga yordam berishadi. Bizning jamoamiz farzandingizning ikkinchi oilasiga aylanadi!"
    )
    await send_section_media(callback, "text_teachers", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "faq")
async def faq_menu(callback: CallbackQuery):
    faqs = await database.get_all_faqs()
    if not faqs:
        await edit_message_safe(callback.message, "Hozircha savollar yo'q.", back_keyboard())
    else:
        text = "❓ <b>Ko'p so'raladigan savollar:</b>\n\nSizni qaysi savol qiziqtiradi? Quyidagilardan birini tanlang:"
        await edit_message_safe(callback.message, text, user_faqs_menu(faqs))
    await callback.answer()

@router.callback_query(F.data.startswith("user_faq_"))
async def show_faq_answer(callback: CallbackQuery):
    faq_id = int(callback.data.split("_")[2])
    faq = await database.get_faq(faq_id)
    if faq:
        text = f"❓ <b>Savol:</b> {faq['question']}\n\n💬 <b>Javob:</b> {faq['answer']}"
        await edit_message_safe(callback.message, text, user_faq_back_menu())
    await callback.answer()

@router.callback_query(F.data == "active_students")
async def active_students_menu(callback: CallbackQuery):
    default_text = (
        "🌟 <b>Faol o'quvchilarimiz va yutuqlarimiz</b>\n\n"
        "Bu yerda bog'chamizning eng intiluvchan, faol va turli tanlovlarda g'olib bo'lgan jajji bolajonlarining rasm va videolari joylab boriladi!\n\n"
        "Tez kunda biz o'z faxrlarimizni shu bo'limda namoyish etamiz! 🏅"
    )
    await send_section_media(callback, "text_active_students", default_text, back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "food_menu")
async def food_menu_default(callback: CallbackQuery):
    # Bugungi kunni aniqlaymiz (1=Dushanba, 7=Yakshanba)
    weekday = datetime.datetime.now().weekday() + 1
    # Agar shanba yoki yakshanba bo'lsa, dushanbani ko'rsatamiz
    current_day = min(weekday, 5)
    await show_food_day(callback, current_day)
    await callback.answer()

@router.callback_query(F.data.startswith("user_food_"))
async def food_menu_day(callback: CallbackQuery):
    day_num = int(callback.data.split("_")[2])
    await show_food_day(callback, day_num)
    await callback.answer()

async def show_food_day(callback: CallbackQuery, day_num: int):
    days = {1: "Dushanba", 2: "Seshanba", 3: "Chorshanba", 4: "Payshanba", 5: "Juma"}
    day_name = days.get(day_num, "Dushanba")
    
    default_text = f"🍲 <b>{day_name} kungi taomnoma:</b>\n\nTez kunda admin tomonidan kiritiladi."
    
    # maxsus send_section_media orqali
    markup = user_food_days_menu(day_num)
    await send_section_media(callback, f"text_food_{day_num}", default_text, markup)

@router.callback_query(F.data == "payment")
async def payment_menu(callback: CallbackQuery):
    default_text = (
        "💳 <b>To'lov qilish:</b>\n\n"
        "Iltimos, farzandingiz qaysi guruhda o'qishini tanlang va bot orqali avtomatik to'lovni amalga oshiring."
    )
    await send_section_media(callback, "text_payment", default_text, payment_groups_menu())
    await callback.answer()

@router.callback_query(F.data == "feedback")
async def feedback_prompt(callback: CallbackQuery, state: FSMContext):
    default_text = (
        "💬 <b>Fikr, shikoyat va takliflar qutisi</b>\n\n"
        "Sizda bog'chamiz faoliyati haqida qanday fikr yoki shikoyatlar bor?\n"
        "Marhamat, shu yerda yozib qoldiring. Bu xat to'g'ridan-to'g'ri Adminga yetib boradi.\n\n"
        "<i>(Bekor qilish uchun 'Orqaga' tugmasini bosing)</i>"
    )
    await state.set_state(UserFeedback.waiting_for_feedback)
    await send_section_media(callback, "text_feedback", default_text, back_keyboard())
    await callback.answer()

@router.message(UserFeedback.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    user = message.from_user
    username = f"@{user.username}" if user.username else "yo'q"
    
    text = (
        f"📬 <b>Yangi Fikr/Shikoyat!</b>\n\n"
        f"Kimdan: {user.full_name}\n"
        f"Username: {username}\n\n"
        f"<b>Xabar:</b>"
    )
    
    if ADMIN_ID:
        try:
            await message.bot.send_message(ADMIN_ID, text, parse_mode="HTML")
            await message.copy_to(ADMIN_ID)
        except Exception:
            pass
            
    await message.reply("✅ Xabaringiz Adminga yuborildi! Fikringiz biz uchun muhim.", reply_markup=main_inline_menu(message.from_user.id))
    await state.clear()

@router.callback_query(F.data == "vacancies")
async def vacancies_prompt(callback: CallbackQuery, state: FSMContext):
    default_text = (
        "💼 <b>Ish o'rinlari (Vakansiyalar)</b>\n\n"
        "Bizning jamoamizga qo'shilmoqchimisiz?\n"
        "Iltimos, o'zingiz haqingizdagi ma'lumotni (rezyume, qaysi yo'nalish bo'yicha ishlamoqchisiz va telefon raqamingizni) yoki tanishtiruv videongizni shu yerga yuboring."
    )
    await state.set_state(UserVacancy.waiting_for_resume)
    await send_section_media(callback, "text_vacancies", default_text, back_keyboard())
    await callback.answer()

@router.message(UserVacancy.waiting_for_resume)
async def process_vacancy(message: Message, state: FSMContext):
    user = message.from_user
    username = f"@{user.username}" if user.username else "yo'q"
    
    text = (
        f"💼 <b>Yangi Vakansiya (Rezyume)!</b>\n\n"
        f"Kimdan: {user.full_name}\n"
        f"Username: {username}\n\n"
        f"<b>Ma'lumot:</b>"
    )
    
    if ADMIN_ID:
        try:
            await message.bot.send_message(ADMIN_ID, text, parse_mode="HTML")
            await message.copy_to(ADMIN_ID)
        except Exception:
            pass
            
    await message.reply("✅ Ma'lumotlaringiz Adminga yuborildi! Tez orada siz bilan bog'lanishadi.", reply_markup=main_inline_menu(message.from_user.id))
    await state.clear()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        f"Assalomu alaykum, {callback.from_user.first_name}!\n"
        f"Xususiy bog'chamizning rasmiy botiga xush kelibsiz.\n\n"
        f"Botdan foydalanishingiz mumkin 😊"
    )
    markup = main_inline_menu(callback.from_user.id)
    try:
        if START_VIDEO_ID and (callback.message.video or callback.message.photo):
            media = InputMediaVideo(media=START_VIDEO_ID, caption=text, parse_mode="HTML")
            await callback.message.edit_media(media=media, reply_markup=markup)
        elif callback.message.video or callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=markup)
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        if "is not modified" in str(e).lower():
            pass
        else:
            await callback.answer(f"Xato: {str(e)[:150]}", show_alert=True)
            return
            
    await callback.answer()

# ================= AUTHENTICATION HANDLERS =================
@router.message(UserRegistration.waiting_for_name, F.text)
async def auth_name_received(message: Message, state: FSMContext):
    await state.update_data(reg_name=message.text)
    await message.answer(
        "Rahmat! Endi <b>Telefon raqamingizni</b> yuboring:",
        parse_mode="HTML",
        reply_markup=contact_keyboard()
    )
    await state.set_state(UserRegistration.waiting_for_phone)

@router.message(UserRegistration.waiting_for_phone, F.contact | F.text)
async def auth_phone_received(message: Message, state: FSMContext):
    data = await state.get_data()
    full_name = data.get("reg_name")
    
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
        
    user_id = message.from_user.id
    
    await database.update_user_info(user_id, full_name, phone)
    await database.update_user_auth_status(user_id, "waiting")
    
    await message.answer(
        "⏳ <b>Arizangiz ma'muriyatga yuborildi.</b>\n\nIltimos, tasdiqlashlarini kuting. Tasdiqlangach sizga xabar beramiz.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    
    # Adminga yuborish
    if ADMIN_ID:
        from keyboards.inline_keyboards import admin_approval_keyboard
        text = (
            f"👤 <b>Yangi foydalanuvchi ruxsat so'rayapti!</b>\n\n"
            f"<b>Ism-familiya:</b> {full_name}\n"
            f"<b>Telefon:</b> {phone}\n"
            f"<b>ID:</b> <code>{user_id}</code>"
        )
        try:
            await message.bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=admin_approval_keyboard(user_id))
        except Exception as e:
            print(f"Adminga yuborishda xatolik: {e}")
            
# ================= OTHER HANDLERS =================
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=main_inline_menu(callback.from_user.id))
    await callback.answer()

@router.message(F.text, StateFilter(None))
async def unknown_message(message: Message):
    # Har qanday tushunarsiz matn yozilganda shu xabar chiqadi
    await message.reply("Botimizga xush kelibsiz! 😊\n\nIltimos, botdan to'liq foydalanish uchun /start komandasini bosing.")


@router.callback_query(F.data == "attendance")
async def attendance_menu(callback: CallbackQuery):
    default_text = "🌡 <b>Davomat va ogohlantirish</b>\n\nAgar farzandingiz bugun bog'chaga kela olmasa yoki kechiksa, quyidagi tugmalar orqali bizni ogohlantirishingiz mumkin."
    from keyboards.inline_keyboards import attendance_action_keyboard
    await send_section_media(callback, "text_attendance", default_text, attendance_action_keyboard())
    await callback.answer()

async def remind_reason(user_id: int, state: FSMContext, bot: Bot):
    for _ in range(15): # 45 minutgacha eslatadi
        await asyncio.sleep(180) # 3 minut
        current_state = await state.get_state()
        if current_state not in ["UserAttendance:waiting_for_reason", "UserAttendance:waiting_for_late_time"]:
            break
        try:
            if current_state == "UserAttendance:waiting_for_reason":
                await bot.send_message(user_id, "❗️ Hurmatli ota-ona, iltimos farzandingiz kela olmasligi sababini yozib yuboring:")
            else:
                await bot.send_message(user_id, "❗️ Hurmatli ota-ona, iltimos farzandingiz qancha vaqt kechikishini yozib yuboring:")
        except Exception:
            break

@router.callback_query(F.data == "att_absent")
async def attendance_absent_action(callback: CallbackQuery, state: FSMContext):
    from states import UserAttendance
    await state.update_data(att_status="🤒 Kasal / Kela olmaydi")
    await state.set_state(UserAttendance.waiting_for_reason)
    
    await callback.message.answer("Iltimos, farzandingiz nima sababdan <b>kela olmasligini</b> qisqacha yozib yuboring (Masalan: 'Toblari qochdi', 'Qishloqqa ketdik'):", parse_mode="HTML")
    await callback.answer()
    asyncio.create_task(remind_reason(callback.from_user.id, state, callback.bot))

@router.callback_query(F.data == "att_late")
async def attendance_late_menu(callback: CallbackQuery):
    from keyboards.inline_keyboards import attendance_late_keyboard
    kb = await attendance_late_keyboard()
    await callback.message.answer("⏳ Farzandingiz qancha vaqt kechikadi?", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.in_(["late_10", "late_15", "late_20", "late_60"]))
async def attendance_late_quick(callback: CallbackQuery):
    time_map = {
        "late_10": await database.get_setting("late_btn_1", "10 minut"),
        "late_15": await database.get_setting("late_btn_2", "15 minut"),
        "late_20": await database.get_setting("late_btn_3", "20 minut"),
        "late_60": await database.get_setting("late_btn_4", "1 soat")
    }
    time_str = time_map[callback.data]
    
    user_name = callback.from_user.full_name
    username = f"@{callback.from_user.username}" if callback.from_user.username else "yo'q"
    
    delta = parse_time_to_delta(time_str)
    
    debug_text = f"\n\nDEBUG: delta={repr(delta)}, time_str={repr(time_str)}"
    base_admin_text = f"🚨 <b>Davomat xabari!</b>\n\n👤 Ota-ona: {user_name} ({username})\nHolat: <b>⏰ Kech qoladi</b>\n\n⏱ Qancha vaqtga: <b>{time_str}</b>" + debug_text
    base_user_text = f"✅ Xo'p rahmat, farzandingizni kutamiz!\n\nHolat: <b>⏰ Kechikish ({time_str})</b>" + debug_text
    
    if ADMIN_ID:
        try:
            admin_msg = await callback.bot.send_message(
                chat_id=ADMIN_ID,
                text=base_admin_text + (f"\n\n🔄 <b>Qolgan vaqt: {int(delta.total_seconds()//60):02d}:{int(delta.total_seconds()%60):02d}</b>" if delta else ""),
                parse_mode="HTML"
            )
            if delta:
                end_time = datetime.now() + delta
                await database.add_timer(ADMIN_ID, admin_msg.message_id, end_time.isoformat(), base_admin_text)
        except Exception:
            pass
            
    user_msg = await callback.message.answer(
        base_user_text + (f"\n\n🔄 <b>Qolgan vaqt: {int(delta.total_seconds()//60):02d}:{int(delta.total_seconds()%60):02d}</b>" if delta else ""), 
        reply_markup=ReplyKeyboardRemove()
    )
    if delta:
        end_time = datetime.now() + delta
        await database.add_timer(callback.message.chat.id, user_msg.message_id, end_time.isoformat(), base_user_text)
        
    await callback.answer()

@router.callback_query(F.data == "late_manual")
async def attendance_late_manual(callback: CallbackQuery, state: FSMContext):
    from states import UserAttendance
    await state.update_data(att_status="⏰ Kech qoladi")
    await state.set_state(UserAttendance.waiting_for_late_time)
    
    await callback.message.answer("Iltimos, farzandingiz soat nechada kelishini yozib yuboring (Masalan: 'Soat 10:30 da boradi' yoki 'Abetdan keyin'):")
    await callback.answer()
    asyncio.create_task(remind_reason(callback.from_user.id, state, callback.bot))

@router.message(StateFilter("UserAttendance:waiting_for_reason", "UserAttendance:waiting_for_late_time"))
async def process_attendance_text(message: Message, state: FSMContext):
    data = await state.get_data()
    status = data.get("att_status", "Noma'lum")
    reason = message.text
    
    current_state = await state.get_state()
    field_name = "⏱ Vaqti" if current_state == "UserAttendance:waiting_for_late_time" else "💬 Sababi"
    
    user_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "yo'q"
    
    delta = None
    if current_state == "UserAttendance:waiting_for_late_time":
        delta = parse_time_to_delta(reason)
        
    base_admin_text = f"🚨 <b>Davomat xabari!</b>\n\n👤 Ota-ona: {user_name} ({username})\nHolat: <b>{status}</b>\n\n{field_name}: <b>{reason}</b>"
    base_user_text = f"✅ Xo'p rahmat, farzandingizni kutamiz!\n\nHolat: <b>{status} ({reason})</b>"
    
    if ADMIN_ID:
        try:
            admin_msg = await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=base_admin_text + (f"\n\n🔄 <b>Qolgan vaqt: {int(delta.total_seconds()//60):02d}:{int(delta.total_seconds()%60):02d}</b>" if delta else ""),
                parse_mode="HTML"
            )
            if delta:
                end_time = datetime.now() + delta
                await database.add_timer(ADMIN_ID, admin_msg.message_id, end_time.isoformat(), base_admin_text)
        except Exception:
            pass
            
    user_msg = await message.reply(
        base_user_text + (f"\n\n🔄 <b>Qolgan vaqt: {int(delta.total_seconds()//60):02d}:{int(delta.total_seconds()%60):02d}</b>" if delta else ""), 
        reply_markup=ReplyKeyboardRemove()
    )
    if delta:
        end_time = datetime.now() + delta
        await database.add_timer(message.chat.id, user_msg.message_id, end_time.isoformat(), base_user_text)
        
    await state.clear()

@router.callback_query(F.data == "educator_contact")
async def educator_contact_menu(callback: CallbackQuery):
    default_text = "💬 <b>Tarbiyachi bilan aloqa</b>\n\nTarbiyachilarga to'g'ridan-to'g'ri xabar, iltimos yoki savolingizni yo'llashingiz mumkin."
    from keyboards.inline_keyboards import educator_contact_keyboard
    await send_section_media(callback, "text_educator_contact", default_text, educator_contact_keyboard())
    await callback.answer()

@router.callback_query(F.data == "contact_educator_start")
async def start_educator_contact(callback: CallbackQuery, state: FSMContext):
    from states import UserEducatorContact
    groups = await database.get_all_educators()
    
    if not groups:
        await callback.message.answer("📝 Iltimos, farzandingizning ism-familiyasini yozib yuboring (Masalan: <i>Ali Valiyev</i>):", parse_mode="HTML")
        await state.set_state(UserEducatorContact.waiting_for_child_name)
    else:
        from keyboards.inline_keyboards import user_groups_keyboard
        await callback.message.answer("Farzandingiz qaysi guruhga qatnaydi? Iltimos, tanlang:", reply_markup=user_groups_keyboard(groups))
        await state.set_state(UserEducatorContact.waiting_for_group)
    await callback.answer()

@router.callback_query(StateFilter("UserEducatorContact:waiting_for_group"), F.data.startswith("sel_group_"))
async def process_group_selection(callback: CallbackQuery, state: FSMContext):
    from states import UserEducatorContact
    group_id = int(callback.data.replace("sel_group_", ""))
    
    group_data = await database.get_educator(group_id)
    if group_data:
        await state.update_data(target_group_name=group_data['group_name'], target_educator_id=group_data['educator_id'])
    
    await callback.message.answer("📝 Iltimos, farzandingizning ism-familiyasini yozib yuboring (Masalan: <i>Ali Valiyev</i>):", parse_mode="HTML")
    await state.set_state(UserEducatorContact.waiting_for_child_name)
    await callback.answer()

@router.message(StateFilter("UserEducatorContact:waiting_for_child_name"), F.text)
async def process_child_name(message: Message, state: FSMContext):
    from states import UserEducatorContact
    await state.update_data(child_name=message.text)
    
    from keyboards.inline_keyboards import parent_role_keyboard
    await message.answer("Siz kimsiz?", reply_markup=parent_role_keyboard())
    await state.set_state(UserEducatorContact.waiting_for_parent_role)

@router.callback_query(StateFilter("UserEducatorContact:waiting_for_parent_role"), F.data.startswith("role_"))
async def process_parent_role(callback: CallbackQuery, state: FSMContext):
    from states import UserEducatorContact
    
    roles = {
        "role_otasi": "Otasi",
        "role_onasi": "Onasi",
        "role_boshqa": "Boshqa qarindoshi"
    }
    role = roles.get(callback.data, "Noma'lum")
    await state.update_data(parent_role=role)
    
    await callback.message.answer("💬 Endi tarbiyachiga aytmoqchi bo'lgan xabaringizni yozib yuboring:")
    await state.set_state(UserEducatorContact.waiting_for_message)
    await callback.answer()

@router.message(StateFilter("UserEducatorContact:waiting_for_message"))
async def process_educator_message(message: Message, state: FSMContext):
    data = await state.get_data()
    child_name = data.get("child_name", "Noma'lum")
    parent_role = data.get("parent_role", "Noma'lum")
    target_group = data.get("target_group_name", "Noma'lum guruh")
    target_ed_id = data.get("target_educator_id")
    
    user_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "yo'q"
    
    msg_text = message.text or message.caption or ""
    
    text_to_send = (
        f"📩 <b>Sizga yangi xabar keldi!</b>\n\n"
        f"🏫 <b>Guruh:</b> {target_group}\n"
        f"👦 <b>Farzandi:</b> {child_name}\n"
        f"👤 <b>Yuboruvchi:</b> {parent_role} — {user_name} ({username})\n"
    )
    if msg_text:
        text_to_send += f"💬 <b>Xabar:</b>\n{msg_text}"
        
    # Tarbiyachiga yuborish
    sent_to_educator = False
    if target_ed_id:
        try:
            if message.content_type == "text":
                await message.bot.send_message(chat_id=target_ed_id, text=text_to_send, parse_mode="HTML")
            else:
                await message.bot.copy_message(chat_id=target_ed_id, from_chat_id=message.chat.id, message_id=message.message_id, caption=text_to_send, parse_mode="HTML")
            sent_to_educator = True
        except Exception as e:
            pass
            
    # Adminga nusxa yuborish
    if ADMIN_ID:
        try:
            admin_status = "✅ Tarbiyachiga ham yetkazildi" if sent_to_educator else "❌ Tarbiyachiga yetkazilmadi (ID xato yoki botga kirmagan)"
            if not target_ed_id:
                admin_status = "ℹ️ Tarbiyachi ID si kiritilmagan"
                
            admin_text = f"👮‍♂️ <b>Admin uchun hisobot:</b>\n{admin_status}\n\n" + text_to_send
            
            if message.content_type == "text":
                await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
            else:
                await message.bot.copy_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id, caption=admin_text, parse_mode="HTML")
        except Exception:
            pass
            
    if sent_to_educator:
        await message.reply("✅ Xabaringiz muvaffaqiyatli tarbiyachiga yetkazildi!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.reply("✅ Xabaringiz qabul qilindi va adminga yetkazildi!", reply_markup=ReplyKeyboardRemove())
        
    await state.clear()

@router.callback_query(F.data == "polls")
async def polls_menu(callback: CallbackQuery):
    default_text = "📊 <b>Ota-onalar bahosi</b>\n\nBizning xizmatlarimiz, taomlar va tarbiyachilarimiz haqida o'z bahoingizni va fikringizni qoldiring!"
    from keyboards.inline_keyboards import polls_action_keyboard
    await send_section_media(callback, "text_polls", default_text, polls_action_keyboard())
    await callback.answer()

@router.callback_query(F.data == "polls_start")
async def start_polls(callback: CallbackQuery, state: FSMContext):
    from states import UserPoll
    await callback.message.answer("📋 Iltimos, bog'chamiz xizmatlariga 1 dan 5 gacha baho bering va takliflaringizni yozib yuboring (Masalan: 5 yulduz. Hamma narsa zo'r!):")
    await state.set_state(UserPoll.waiting_for_feedback)
    await callback.answer()

@router.message(StateFilter("UserPoll:waiting_for_feedback"))
async def process_poll_feedback(message: Message, state: FSMContext):
    user_name = message.from_user.full_name
    
    if ADMIN_ID:
        try:
            await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📊 <b>Yangi so'rovnoma javobi!</b>\n\n👤 Ota-ona: {user_name}\n\n📝 Javob:\n{message.text}",
                parse_mode="HTML"
            )
        except Exception:
            pass
            
    await message.reply("✅ Fikringiz uchun katta rahmat! Bu biz uchun juda muhim.", reply_markup=ReplyKeyboardRemove())
    await state.clear()





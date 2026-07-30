from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputMediaVideo, ReplyKeyboardRemove
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from states import UserFeedback, UserVacancy, UserRegistration
from keyboards.inline_keyboards import (back_keyboard, location_keyboard, payment_groups_menu, 
                                        main_inline_menu, user_cameras_menu, user_food_days_menu, 
                                        user_faqs_menu, user_faq_back_menu)
from keyboards.reply_keyboards import contact_keyboard
from config import ADMIN_ID, START_VIDEO_ID
import database
import datetime

router = Router()

async def edit_message_safe(message: Message, text: str, reply_markup):
    try:
        if message.video:
            await message.edit_caption(caption=text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        pass

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    is_new = database.add_user(user.id, user.username, user.full_name)
    
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
    db_user = database.get_user(user_id)
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
    cameras = database.get_active_cameras()
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
    data = database.get_setting_media(key, default_text)
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
    data = database.get_setting_media(key, default_text)
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
    faqs = database.get_all_faqs()
    if not faqs:
        await edit_message_safe(callback.message, "Hozircha savollar yo'q.", back_keyboard())
    else:
        text = "❓ <b>Ko'p so'raladigan savollar:</b>\n\nSizni qaysi savol qiziqtiradi? Quyidagilardan birini tanlang:"
        await edit_message_safe(callback.message, text, user_faqs_menu(faqs))
    await callback.answer()

@router.callback_query(F.data.startswith("user_faq_"))
async def show_faq_answer(callback: CallbackQuery):
    faq_id = int(callback.data.split("_")[2])
    faq = database.get_faq(faq_id)
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
    # callback query handled by generic fallback if needed

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
    
    database.update_user_info(user_id, full_name, phone)
    database.update_user_auth_status(user_id, "waiting")
    
    await message.answer(
        "⏳ <b>Arizangiz ma'muriyatga yuborildi.</b>\n\nIltimos, tasdiqlashlarini kuting. Tasdiqlangach sizga xabar beramiz.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    
    # Adminga yuborish
    if ADMIN_ID:
        from keyboards.inline_keyboards import admin_approval_keyboard
        from main import bot
        text = (
            f"👤 <b>Yangi foydalanuvchi ruxsat so'rayapti!</b>\n\n"
            f"<b>Ism-familiya:</b> {full_name}\n"
            f"<b>Telefon:</b> {phone}\n"
            f"<b>ID:</b> {user_id}"
        )
        try:
            await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=admin_approval_keyboard(user_id))
        except Exception as e:
            pass
            
# ================= OTHER HANDLERS =================
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=main_inline_menu(callback.from_user.id))
    await callback.answer()

@router.message(F.text, StateFilter(None))
async def unknown_message(message: Message):
    # Har qanday tushunarsiz matn yozilganda shu xabar chiqadi
    await message.reply("Botimizga xush kelibsiz! 😊\n\nIltimos, botdan to'liq foydalanish uchun /start komandasini bosing.")

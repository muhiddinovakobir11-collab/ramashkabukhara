from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import AdminSettings, AdminGallery, AdminBroadcast, AdminCameraEdit, AdminFAQEdit
from keyboards.inline_keyboards import (admin_menu_keyboard, admin_edit_texts_menu, 
                                        admin_back_keyboard, admin_gallery_type_menu, 
                                        admin_gallery_categories_menu, admin_cameras_menu, 
                                        admin_camera_edit_menu, admin_food_days_menu, admin_faqs_menu)
from config import ADMIN_ID
import database
from handlers.user_handlers import edit_message_safe
import asyncio
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

router = Router()

# Faqat adminga ishlashi uchun filter
router.callback_query.filter(F.from_user.id == int(ADMIN_ID) if ADMIN_ID else False)
router.message.filter(F.from_user.id == int(ADMIN_ID) if ADMIN_ID else False)

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "👨‍💻 <b>Admin Panel</b>\n\nQuyidagi menyulardan birini tanlang:"
    await edit_message_safe(callback.message, text, admin_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    users = await database.get_all_users()
    total_users = len(users)
    active_users = len([u for u in users if u[3] == 1])
    blocked_users = total_users - active_users
    
    text = (
        "👨‍💻 <b>Admin Panel -> Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"✅ Faol foydalanuvchilar: {active_users}\n"
        f"❌ Botni bloklaganlar: {blocked_users}\n"
    )
    # Statistika ostiga admin_menu_keyboard ni qaytaramiz (chunki unda orqaga bor)
    await edit_message_safe(callback.message, text, admin_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_edit_texts")
async def admin_edit_texts(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "📝 <b>Qaysi bo'lim matnini o'zgartirmoqchisiz?</b>\n\nTanlang:"
    await edit_message_safe(callback.message, text, admin_edit_texts_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("edit_"))
async def start_editing_text(callback: CallbackQuery, state: FSMContext):
    section = callback.data.replace("edit_", "")
    
    # Kiritilgan nomlarni xaritalash
    names = {
        "services": "Xizmatlar va Narxlar",
        "location": "Manzil va aloqa",
        "gallery": "Bizning galereya",
        "schedule": "Kun tartibi",
        "teachers": "Tarbiyachilarimiz",
        "faq": "Ko'p so'raladigan savollar",
        "active_students": "Faol o'quvchilar",
        "food_menu": "Taomnoma",
        "payment": "To'lovlar qoidalari",
        "cameras": "Onlayn Kameralar",
        "psychologist": "Psixolog maslahati",
        "birthdays": "Tug'ilgan kunlar",
        "events": "Bayramlar va tadbirlar",
        "achievements": "Yutuqlarimiz",
        "dress_code": "Bog'cha formasi",
        "feedback": "Fikr va takliflar",
        "vacancies": "Vakansiyalar",
        "registration": "Farzandni yozdirish"
    }
    
    section_name = names.get(section, section)
    
    text = (
        f"Siz <b>{section_name}</b> bo'limini tahrirlashni tanladingiz.\n\n"
        f"Iltimos, ushbu bo'lim uchun yangi matnni (yoki rasm/video bilan birga izoh qilib) shu yerga yuboring."
    )
    
    await state.update_data(editing_section=section)
    await state.set_state(AdminSettings.waiting_for_text)
    
    await edit_message_safe(callback.message, text, admin_back_keyboard())
    await callback.answer()

@router.message(AdminSettings.waiting_for_text, F.text | F.photo | F.video)
async def save_new_text(message: Message, state: FSMContext):
    data = await state.get_data()
    section = data.get("editing_section")
    new_text = message.html_text if message.html_text else ""
    
    if message.photo:
        await database.set_setting_media(f"text_{section}", "photo", message.photo[-1].file_id, new_text)
    elif message.video:
        await database.set_setting_media(f"text_{section}", "video", message.video.file_id, new_text)
    else:
        await database.set_setting_media(f"text_{section}", "text", None, new_text)
    
    await message.reply(f"✅ Ma'lumot muvaffaqiyatli yangilandi!\nO'zgarishni ko'rish uchun /start tugmasini bosing.")
    await state.clear()

@router.callback_query(F.data == "admin_edit_gallery")
async def admin_edit_gallery(callback: CallbackQuery):
    text = "📸 <b>Galereyani tahrirlash</b>\n\nQaysi turdagi fayllarga yangi ma'lumot qo'shmoqchisiz?"
    await edit_message_safe(callback.message, text, admin_gallery_type_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_gal_type_"))
async def admin_gal_type_selection(callback: CallbackQuery):
    media_type = callback.data.split("_")[3] # photo or video
    m_type_char = 'p' if media_type == 'photo' else 'v'
    text = f"Qaysi jarayonga yangi {'rasm' if m_type_char == 'p' else 'video'} qo'shmoqchisiz?"
    await edit_message_safe(callback.message, text, admin_gallery_categories_menu(m_type_char))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_gal_cat_"))
async def admin_gal_cat_selection(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    media_type = parts[3] # 'p' or 'v'
    category = parts[4]
    
    names = {
        "food": "Ovqatlanish jarayoni",
        "sleep": "Uxlash jarayoni",
        "study": "Dars jarayoni",
        "other": "Boshqalar"
    }
    
    cat_name = names.get(category, category)
    m_name = "Rasm" if media_type == 'p' else "Video"
    
    text = (f"Siz <b>{cat_name}</b> bo'limiga yangi <b>{m_name}</b> qo'shishni tanladingiz.\n\n"
            f"Iltimos, menga 1 ta {m_name.lower()} yuboring va unga izoh qoldirishni unutmang (izoh rasm/video tagida yoziladi).")
            
    await state.update_data(gal_media_type=media_type, gal_category=category)
    await state.set_state(AdminGallery.waiting_for_media)
    
    await edit_message_safe(callback.message, text, admin_back_keyboard())
    await callback.answer()

@router.message(AdminGallery.waiting_for_media, F.photo | F.video)
async def save_new_gallery_media(message: Message, state: FSMContext):
    data = await state.get_data()
    media_type = data.get("gal_media_type")
    category = data.get("gal_category")
    
    if media_type == 'p' and not message.photo:
        await message.reply("Iltimos, rasm yuboring! Bekor qilish uchun 'Admin panel' orqali qayting yoki /start bosing.")
        return
    if media_type == 'v' and not message.video:
        await message.reply("Iltimos, video yuboring! Bekor qilish uchun 'Admin panel' orqali qayting yoki /start bosing.")
        return
        
    caption = message.html_text if message.html_text else ""
    
    if message.photo:
        media_id = message.photo[-1].file_id
    else:
        media_id = message.video.file_id
        
    await database.add_gallery_media(category, media_type, media_id, caption)
    
    await message.reply(f"✅ Muvaffaqiyatli saqlandi!\nGalereyaga kirsangiz ushbu ma'lumot oxirida paydo bo'ladi.\nYana boshqa narsa o'zgartirish uchun /start bosing.")
    await state.clear()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    text = "📢 <b>Ommaviy xabarnoma</b>\n\nIltimos, barcha foydalanuvchilarga yuboriladigan xabarni yuboring (matn, rasm yoki video)."
    await state.set_state(AdminBroadcast.waiting_for_message)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="admin_panel")]])
    await edit_message_safe(callback.message, text, markup)
    await callback.answer()

async def run_broadcast_task(bot_message: Message, target_message: Message, active_users: list, broadcast_id: int):
    success_count = 0
    fail_count = 0
    
    for u in active_users:
        user_id = u[0]
        try:
            sent_msg = await target_message.copy_to(user_id)
            await database.add_broadcast_message(broadcast_id, user_id, sent_msg.message_id)
            success_count += 1
        except TelegramForbiddenError:
            await database.update_user_status(user_id, False)
            fail_count += 1
        except Exception:
            fail_count += 1
        await asyncio.sleep(0.05)
        
    from keyboards.inline_keyboards import delete_broadcast_menu
    await bot_message.edit_text(
        f"✅ Xabar tarqatish yakunlandi!\n\nYetkazildi: {success_count} ta\nBloklagan/Xato: {fail_count} ta",
        reply_markup=delete_broadcast_menu(broadcast_id)
    )

@router.message(AdminBroadcast.waiting_for_message)
async def process_admin_broadcast(message: Message, state: FSMContext):
    await state.clear()
    users = await database.get_all_users()
    active_users = [u for u in users if u[3] == 1]
    
    msg = await message.reply(f"📨 Xabar {len(active_users)} ta foydalanuvchiga yuborilmoqda. Orqa fonda ishlayapti, kuting...")
    
    broadcast_id = await database.create_broadcast()
    asyncio.create_task(run_broadcast_task(msg, message, active_users, broadcast_id))

@router.callback_query(F.data.startswith("delete_broadcast_"))
async def delete_broadcast_handler(callback: CallbackQuery):
    broadcast_id = int(callback.data.split("_")[2])
    await callback.message.edit_text("🗑 Xabarlar o'chirilmoqda. Iltimos kuting...")
    
    messages = await database.get_broadcast_messages(broadcast_id)
    deleted = 0
    for user_id, message_id in messages:
        try:
            await callback.bot.delete_message(chat_id=user_id, message_id=message_id)
            deleted += 1
        except Exception:
            pass
        await asyncio.sleep(0.05)
        
    await callback.message.edit_text(f"✅ O'chirish yakunlandi!\nJami {deleted} ta xabar o'chirildi.")
    await callback.answer()

# ================= CAMERAS MANAGEMENT =================
@router.callback_query(F.data == "admin_manage_cameras")
async def admin_manage_cameras(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    cameras = await database.get_all_cameras()
    text = "🎥 <b>Kameralarni boshqarish</b>\n\nQaysi kamerani tahrirlamoqchisiz?"
    await edit_message_safe(callback.message, text, admin_cameras_menu(cameras))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_cam_"))
async def admin_camera_action(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data.startswith("admin_cam_toggle_"):
        cam_id = int(data.split("_")[3])
        await database.toggle_camera_status(cam_id)
        cam = await database.get_camera(cam_id)
        text = f"🎥 <b>{cam['name']}</b> holati o'zgartirildi.\n\nHozirgi ssilka: {cam['url'] if cam['url'] else 'Kiritilmagan'}"
        await edit_message_safe(callback.message, text, admin_camera_edit_menu(cam_id, cam['is_active']))
        
    elif data.startswith("admin_cam_link_"):
        cam_id = int(data.split("_")[3])
        cam = await database.get_camera(cam_id)
        text = f"🔗 <b>{cam['name']}</b> uchun yangi ssilkani yuboring (Masalan: https://... yoki rtmp://...):"
        await state.update_data(editing_cam_id=cam_id)
        await state.set_state(AdminCameraEdit.waiting_for_url)
        await edit_message_safe(callback.message, text, admin_back_keyboard())
        
    else:
        # Just viewing the camera
        try:
            cam_id = int(data.split("_")[2])
            cam = await database.get_camera(cam_id)
            if not cam:
                return
            status = "🟢 Yoqilgan" if cam['is_active'] else "🔴 O'chirilgan"
            url = cam['url'] if cam['url'] else "Hali kiritilmagan"
            text = f"🎥 <b>{cam['name']}</b>\n\nHolati: {status}\nSsilka (URL): {url}"
            await edit_message_safe(callback.message, text, admin_camera_edit_menu(cam_id, cam['is_active']))
        except ValueError:
            pass
            
    await callback.answer()

@router.message(AdminCameraEdit.waiting_for_url, F.text)
async def save_camera_url(message: Message, state: FSMContext):
    data = await state.get_data()
    cam_id = data.get("editing_cam_id")
    url = message.text.strip()
    
    await database.update_camera_url(cam_id, url)
    cam = await database.get_camera(cam_id)
    
    await message.reply(f"✅ <b>{cam['name']}</b> ssilkasi saqlandi!\n\nYangilangan ssilka: {url}")
    await state.clear()

# ================= FOOD MANAGEMENT =================
@router.callback_query(F.data == "admin_manage_food")
async def admin_manage_food(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🍲 <b>Taomnoma (Boshqarish)</b>\n\nQaysi kunning taomnomasini o'zgartirmoqchisiz?"
    await edit_message_safe(callback.message, text, admin_food_days_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_edit_food_"))
async def start_editing_food_day(callback: CallbackQuery, state: FSMContext):
    day_num = callback.data.split("_")[3]
    days = {"1": "Dushanba", "2": "Seshanba", "3": "Chorshanba", "4": "Payshanba", "5": "Juma"}
    day_name = days.get(day_num, "Noma'lum kun")
    
    text = (f"Siz <b>{day_name}</b> kungi taomnomasini tahrirlashni tanladingiz.\n\n"
            "Ushbu kun uchun rasm (yoki video) va matnni yuboring:")
            
    await state.update_data(editing_section=f"food_{day_num}")
    await state.set_state(AdminSettings.waiting_for_text)
    await edit_message_safe(callback.message, text, admin_back_keyboard())
    await callback.answer()

# ================= FAQ MANAGEMENT =================
@router.callback_query(F.data == "admin_manage_faqs")
async def admin_manage_faqs(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    faqs = await database.get_all_faqs()
    text = "💬 <b>Ko'p so'raladigan savollar (Boshqarish)</b>\n\nSavolni o'chirish uchun 🗑 ni bosing yoki yangi qo'shing:"
    await edit_message_safe(callback.message, text, admin_faqs_menu(faqs))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_faq_del_"))
async def admin_delete_faq(callback: CallbackQuery):
    faq_id = int(callback.data.split("_")[3])
    await database.delete_faq(faq_id)
    faqs = await database.get_all_faqs()
    text = "✅ Savol o'chirildi.\n\n💬 <b>Ko'p so'raladigan savollar:</b>"
    await edit_message_safe(callback.message, text, admin_faqs_menu(faqs))
    await callback.answer()

@router.callback_query(F.data == "admin_faq_add")
async def admin_add_faq_start(callback: CallbackQuery, state: FSMContext):
    text = "❓ <b>Yangi savol qo'shish</b>\n\nIltimos, ota-onalar tomonidan ko'p beriladigan savolni yozing:"
    await state.set_state(AdminFAQEdit.waiting_for_question)
    await edit_message_safe(callback.message, text, admin_back_keyboard())
    await callback.answer()

@router.message(AdminFAQEdit.waiting_for_question, F.text)
async def admin_add_faq_q(message: Message, state: FSMContext):
    await state.update_data(faq_question=message.text)
    text = f"✅ Savol qabul qilindi.\n\nEndi ushbu savolga <b>Javobni</b> yozing:"
    await message.reply(text)
    await state.set_state(AdminFAQEdit.waiting_for_answer)

@router.message(AdminFAQEdit.waiting_for_answer, F.text | F.photo | F.video)
async def admin_add_faq_a(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data.get("faq_question")
    answer = message.html_text if message.html_text else ""
    
    await database.add_faq(question, answer)
    await message.reply("✅ Yangi Savol-javob muvaffaqiyatli saqlandi! Ko'rish uchun menyuga qayting.")
    await state.clear()

# ================= AUTHENTICATION MANAGEMENT =================
@router.callback_query(F.data.startswith("auth_approve_"))
async def admin_approve_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    await database.update_user_auth_status(user_id, "approved")
    
    await callback.message.edit_text(callback.message.html_text + "\n\n<b>✅ TASDIQLANDI</b>", parse_mode="HTML")
    await callback.answer("Tasdiqlandi!")
    
    # Send main menu to user
    from config import START_VIDEO_ID
    from keyboards.inline_keyboards import main_inline_menu
    try:
        text = "🎉 <b>Tabriklaymiz, arizangiz qabul qilindi!</b>\n\nSiz endi botdan to'liq foydalanishingiz mumkin."
        await callback.bot.send_message(user_id, text, parse_mode="HTML")
        
        caption_text = (
            "Assalomu alaykum, akoshprod!\n"
            "Xususiy bog'chamizning rasmiy botiga xush kelibsiz.\n\n"
            "Botdan foydalanishingiz mumkin 😊"
        )
        
        if START_VIDEO_ID:
            try:
                await callback.bot.send_video(
                    chat_id=user_id,
                    video=START_VIDEO_ID,
                    caption=caption_text,
                    parse_mode="HTML",
                    reply_markup=main_inline_menu(user_id)
                )
            except Exception:
                await callback.bot.send_message(user_id, caption_text, parse_mode="HTML", reply_markup=main_inline_menu(user_id))
        else:
            await callback.bot.send_message(user_id, caption_text, parse_mode="HTML", reply_markup=main_inline_menu(user_id))
            
        await callback.message.reply("✅ <b>O'sha foydalanuvchiga bot tomonidan avtomatik ravishda tabriknoma va video yuborildi!</b>", parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to user: {e}")
        await callback.message.reply(f"❌ Xatolik yuz berdi: foydalanuvchiga xabar bormadi. Sabab: {e}")

@router.callback_query(F.data.startswith("auth_reject_"))
async def admin_reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    await database.update_user_auth_status(user_id, "rejected")
    
    await callback.message.edit_text(callback.message.html_text + "\n\n<b>❌ RAD ETILDI</b>", parse_mode="HTML")
    await callback.answer("Rad etildi!")
    
    try:
        text = "❌ <b>Kechirasiz, sizning arizangiz ma'muriyat tomonidan rad etildi.</b>"
        await callback.bot.send_message(user_id, text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to user: {e}")

# ================= USER MANAGEMENT =================
@router.callback_query(F.data == "admin_manage_users")
async def admin_manage_users(callback: CallbackQuery):
    from keyboards.inline_keyboards import admin_user_categories_menu
    await callback.message.edit_text(
        "👥 <b>Foydalanuvchilarni boshqarish</b>\n\nQaysi ro'yxatni ko'rmoqchisiz?",
        parse_mode="HTML",
        reply_markup=admin_user_categories_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery):
    from keyboards.inline_keyboards import admin_menu_keyboard
    await callback.message.edit_text("👨‍💻 <b>Admin Panel</b>\n\nQuyidagi menyulardan birini tanlang:", parse_mode="HTML", reply_markup=admin_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_users_cat_"))
async def admin_users_category(callback: CallbackQuery):
    status = callback.data.split("_")[3]
    users = await database.get_users_by_status(status)
    
    if not users:
        await callback.answer(f"{'Tasdiqlangan' if status == 'approved' else 'Bloklangan'} foydalanuvchilar topilmadi.", show_alert=True)
        return
        
    from keyboards.inline_keyboards import admin_users_menu
    title = "✅ Ruxsat etilganlar" if status == "approved" else "❌ Bloklanganlar"
    await callback.message.edit_text(
        f"<b>{title}:</b>\nJami: {len(users)} ta",
        parse_mode="HTML",
        reply_markup=admin_users_menu(users, page=1, status=status)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_users_page_"))
async def admin_users_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    status = parts[3]
    page = int(parts[4])
    users = await database.get_users_by_status(status)
    
    from keyboards.inline_keyboards import admin_users_menu
    try:
        await callback.message.edit_reply_markup(reply_markup=admin_users_menu(users, page=page, status=status))
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("admin_user_detail_"))
async def admin_user_detail(callback: CallbackQuery):
    parts = callback.data.split("_")
    status = parts[3]
    user_id = int(parts[4])
    db_user = await database.get_user(user_id)
    
    if not db_user:
        await callback.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return
        
    from keyboards.inline_keyboards import admin_user_detail_menu
    default_name = "Noma'lum"
    default_username = "Yo'q"
    text = (
        f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
        f"<b>Ismi:</b> {db_user.get('full_name', default_name)}\n"
        f"<b>Telefon:</b> {db_user.get('phone', 'Kiritilmagan')}\n"
        f"<b>Username:</b> {db_user.get('username', default_username)}\n"
        f"<b>ID:</b> <code>{user_id}</code>\n"
        f"<b>Holati:</b> {'✅ Tasdiqlangan' if status == 'approved' else '❌ Bloklangan'}"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_user_detail_menu(user_id, status))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_revoke_user_"))
async def admin_revoke_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    
    if str(user_id) == str(ADMIN_ID):
        await callback.answer("O'zingizni bloklay olmaysiz!", show_alert=True)
        return
        
    await database.update_user_auth_status(user_id, "rejected")
    
    from keyboards.inline_keyboards import admin_user_categories_menu
    await callback.message.edit_text(callback.message.html_text + "\n\n<b>🚫 BLOKLANDI</b>", parse_mode="HTML", reply_markup=admin_user_categories_menu())
    await callback.answer("Foydalanuvchi bloklandi!")
    
    try:
        await callback.bot.send_message(user_id, "🚫 <b>Sizning botdan foydalanish ruxsatingiz ma'muriyat tomonidan bekor qilindi.</b>", parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to user: {e}")

@router.callback_query(F.data.startswith("admin_unblock_user_"))
async def admin_unblock_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    await database.update_user_auth_status(user_id, "approved")
    
    from keyboards.inline_keyboards import admin_user_categories_menu
    await callback.message.edit_text(callback.message.html_text + "\n\n<b>✅ TASDIQLANDI</b>", parse_mode="HTML", reply_markup=admin_user_categories_menu())
    await callback.answer("Foydalanuvchi tasdiqlandi!")
    
    from config import START_VIDEO_ID
    from keyboards.inline_keyboards import main_inline_menu
    try:
        text = "🎉 <b>Tabriklaymiz, ma'muriyat sizga botdan yana foydalanishga ruxsat berdi!</b>"
        await callback.bot.send_message(user_id, text, parse_mode="HTML")
        
        caption_text = (
            "Assalomu alaykum!\n"
            "Xususiy bog'chamizning rasmiy botiga xush kelibsiz.\n\n"
            "Botdan foydalanishingiz mumkin 😊"
        )
        if START_VIDEO_ID:
            try:
                await callback.bot.send_video(chat_id=user_id, video=START_VIDEO_ID, caption=caption_text, parse_mode="HTML", reply_markup=main_inline_menu(user_id))
            except Exception:
                await callback.bot.send_message(user_id, caption_text, parse_mode="HTML", reply_markup=main_inline_menu(user_id))
        else:
            await callback.bot.send_message(user_id, caption_text, parse_mode="HTML", reply_markup=main_inline_menu(user_id))
    except Exception as e:
        print(f"Error sending to user: {e}")



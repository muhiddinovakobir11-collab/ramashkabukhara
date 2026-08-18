from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID

def main_inline_menu(user_id: int):
    # Asosiy tugmalar (barcha uchun)
    buttons = [
        [InlineKeyboardButton(text="📝 Xizmatlar va narxlar", callback_data="services"),
         InlineKeyboardButton(text="📍 Manzil va aloqa", callback_data="location")],
        [InlineKeyboardButton(text="📸 Bizning galereya", callback_data="gallery"),
         InlineKeyboardButton(text="🕒 Kun tartibi", callback_data="schedule")],
        [InlineKeyboardButton(text="👩‍🏫 Tarbiyachilarimiz", callback_data="teachers"),
         InlineKeyboardButton(text="❓ Savol-javoblar", callback_data="faq")],
        [InlineKeyboardButton(text="🌟 Faol o'quvchilar", callback_data="active_students"), 
         InlineKeyboardButton(text="🍲 Taomnoma", callback_data="food_menu")],
        [InlineKeyboardButton(text="💳 To'lov qilish", callback_data="payment"), 
         InlineKeyboardButton(text="💬 Fikr va takliflar", callback_data="feedback")],
        [InlineKeyboardButton(text="🎥 Onlayn kameralar", callback_data="cameras"),
         InlineKeyboardButton(text="🧠 Psixolog maslahati", callback_data="psychologist")],
        [InlineKeyboardButton(text="🎂 Tug'ilgan kunlar", callback_data="birthdays"),
         InlineKeyboardButton(text="🎈 Bayramlar", callback_data="events")],
        [InlineKeyboardButton(text="🏆 Yutuqlarimiz", callback_data="achievements"),
         InlineKeyboardButton(text="👗 Bog'cha formasi", callback_data="dress_code")],
        [InlineKeyboardButton(text="💼 Vakansiyalar (Ish)", callback_data="vacancies")],
        [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="registration")],
        [InlineKeyboardButton(text="🌡 Davomat va ogohlantirish", callback_data="attendance")],
        [InlineKeyboardButton(text="💬 Tarbiyachi bilan aloqa", callback_data="educator_contact")],
        [InlineKeyboardButton(text="📊 Ota-onalar bahosi", callback_data="polls")]
    ]
    
    # Faqat admin uchun tugma
    if str(user_id) == str(ADMIN_ID):
        buttons.insert(0, [InlineKeyboardButton(text="👨‍💻 Admin panel", callback_data="admin_panel")])
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
        ]
    )

def location_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Xaritada ochish", url="https://www.google.com/maps?q=39.813567,64.413308")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
        ]
    )

def admin_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilarni boshqarish", callback_data="admin_manage_users")],
            [InlineKeyboardButton(text="📝 Matnlarni tahrirlash", callback_data="admin_edit_texts")],
            [InlineKeyboardButton(text="📸 Galereyani tahrirlash", callback_data="admin_edit_gallery")],
            [InlineKeyboardButton(text="📢 Xabar tarqatish (Ommaviy)", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="🗑 Oxirgi xabarni o'chirish", callback_data="admin_delete_last_broadcast")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
        ]
    )

def admin_edit_texts_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Xizmatlar", callback_data="edit_services"),
             InlineKeyboardButton(text="📍 Manzil", callback_data="edit_location")],
            [InlineKeyboardButton(text="📸 Galereya", callback_data="edit_gallery"),
             InlineKeyboardButton(text="🕒 Kun tartibi", callback_data="edit_schedule")],
            [InlineKeyboardButton(text="👩‍🏫 Tarbiyachilar", callback_data="edit_teachers"),
             InlineKeyboardButton(text="💬 Ko'p so'raladigan savollar (FAQ)", callback_data="admin_manage_faqs")],
            [InlineKeyboardButton(text="🌟 Faol o'quvchilar", callback_data="edit_active_students"),
             InlineKeyboardButton(text="🍲 Taomnoma (Boshqarish)", callback_data="admin_manage_food")],
            [InlineKeyboardButton(text="💳 To'lovlar qoidalari", callback_data="edit_payment")],
            [InlineKeyboardButton(text="🎥 Onlayn Kameralar (Boshqarish)", callback_data="admin_manage_cameras"),
             InlineKeyboardButton(text="🧠 Psixolog maslahati", callback_data="edit_psychologist")],
            [InlineKeyboardButton(text="🎂 Tug'ilgan kunlar", callback_data="edit_birthdays"),
             InlineKeyboardButton(text="🎈 Bayramlar va tadbirlar", callback_data="edit_events")],
            [InlineKeyboardButton(text="🏆 Yutuqlarimiz", callback_data="edit_achievements"),
             InlineKeyboardButton(text="👗 Bog'cha formasi", callback_data="edit_dress_code")],
            [InlineKeyboardButton(text="💬 Fikr va takliflar", callback_data="edit_feedback"),
             InlineKeyboardButton(text="💼 Vakansiyalar", callback_data="edit_vacancies")],
            [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="edit_registration")],
            [InlineKeyboardButton(text="🌡 Davomat", callback_data="edit_attendance"),
             InlineKeyboardButton(text="💬 Tarbiyachi bilan aloqa", callback_data="edit_educator_contact")],
            [InlineKeyboardButton(text="📊 Ota-onalar bahosi", callback_data="edit_polls")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
        ]
    )

def admin_back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="admin_edit_texts")]
        ]
    )

def gallery_type_menu():
    buttons = [
        [InlineKeyboardButton(text="📸 Rasmlar", callback_data="view_gallery_photo"),
         InlineKeyboardButton(text="🎥 Videolar", callback_data="view_gallery_video")],
        [InlineKeyboardButton(text="Orqaga", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_cameras_menu(cameras: list):
    buttons = []
    # kameralarni 2 tadan qatorga joylash
    row = []
    for cam in cameras:
        status = "🟢" if cam['is_active'] else "🔴"
        text = f"{status} {cam['name']}"
        row.append(InlineKeyboardButton(text=text, callback_data=f"admin_cam_{cam['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="Orqaga", callback_data="admin_edit_texts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_camera_edit_menu(camera_id: int, is_active: bool):
    status_text = "🔴 O'chirish" if is_active else "🟢 Yoqish"
    buttons = [
        [InlineKeyboardButton(text=status_text, callback_data=f"admin_cam_toggle_{camera_id}")],
        [InlineKeyboardButton(text="🔗 Ssilkani o'zgartirish", callback_data=f"admin_cam_link_{camera_id}")],
        [InlineKeyboardButton(text="Orqaga", callback_data="admin_manage_cameras")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_cameras_menu(cameras: list):
    buttons = []
    # kameralarni 1 tadan qilib url bilan joylash
    for cam in cameras:
        # url bo'sh bo'lsa, xato bermasligi uchun qanaqadir fallback
        url = cam['url'] if cam['url'] and cam['url'].startswith("http") else "https://google.com"
        buttons.append([InlineKeyboardButton(text=f"📹 {cam['name']}", url=url)])
        
    buttons.append([InlineKeyboardButton(text="Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def gallery_categories_menu(media_type: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🍲 Ovqatlanish", callback_data=f"gal_cat_{media_type}_food"),
             InlineKeyboardButton(text="😴 Uxlash", callback_data=f"gal_cat_{media_type}_sleep")],
            [InlineKeyboardButton(text="📚 Dars jarayoni", callback_data=f"gal_cat_{media_type}_study"),
             InlineKeyboardButton(text="🎭 Boshqalar", callback_data=f"gal_cat_{media_type}_other")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="gallery")]
        ]
    )

def carousel_keyboard(media_type: str, category: str, current_index: int, total_count: int):
    buttons = []
    nav_row = []
    
    if current_index > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"gal_nav_{media_type}_{category}_{current_index-1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"{current_index + 1} / {total_count}", callback_data="ignore"))
    
    if current_index < total_count - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"gal_nav_{media_type}_{category}_{current_index+1}"))
        
    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"gal_type_{'photo' if media_type == 'p' else 'video'}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_gallery_type_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Rasmlarga qo'shish", callback_data="admin_gal_type_photo"),
             InlineKeyboardButton(text="🎥 Videolarga qo'shish", callback_data="admin_gal_type_video")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
        ]
    )

def admin_gallery_categories_menu(media_type: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🍲 Ovqatlanish", callback_data=f"admin_gal_cat_{media_type}_food"),
             InlineKeyboardButton(text="😴 Uxlash", callback_data=f"admin_gal_cat_{media_type}_sleep")],
            [InlineKeyboardButton(text="📚 Dars jarayoni", callback_data=f"admin_gal_cat_{media_type}_study"),
             InlineKeyboardButton(text="🎭 Boshqalar", callback_data=f"admin_gal_cat_{media_type}_other")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_edit_gallery")]
        ]
    )

def payment_groups_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Kichik guruh - 1,500,000 so'm", callback_data="pay_kichik")],
            [InlineKeyboardButton(text="O'rta guruh - 1,500,000 so'm", callback_data="pay_orta")],
            [InlineKeyboardButton(text="Katta guruh - 1,600,000 so'm", callback_data="pay_katta")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
        ]
    )

# ================= FOOD MENUS =================
def admin_food_days_menu():
    buttons = [
        [InlineKeyboardButton(text="Dushanba", callback_data="admin_edit_food_1"),
         InlineKeyboardButton(text="Seshanba", callback_data="admin_edit_food_2")],
        [InlineKeyboardButton(text="Chorshanba", callback_data="admin_edit_food_3"),
         InlineKeyboardButton(text="Payshanba", callback_data="admin_edit_food_4")],
        [InlineKeyboardButton(text="Juma", callback_data="admin_edit_food_5")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_edit_texts")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_food_days_menu(current_day: int):
    # current_day: 1 (Dushanba) dan 5 (Juma) gacha
    days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma"]
    buttons = []
    row = []
    for i, day in enumerate(days, 1):
        # Hozirgi kunni ajratib ko'rsatish
        text = f"✅ {day}" if i == current_day else day
        row.append(InlineKeyboardButton(text=text, callback_data=f"user_food_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================= FAQ MENUS =================
def admin_faqs_menu(faqs: list):
    buttons = []
    for faq in faqs:
        buttons.append([InlineKeyboardButton(text=f"🗑 {faq['question'][:30]}...", callback_data=f"admin_faq_del_{faq['id']}")])
        
    buttons.append([InlineKeyboardButton(text="➕ Yangi savol qo'shish", callback_data="admin_faq_add")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_edit_texts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_faqs_menu(faqs: list):
    buttons = []
    for faq in faqs:
        buttons.append([InlineKeyboardButton(text=f"🔘 {faq['question']}", callback_data=f"user_faq_{faq['id']}")])
        
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_faq_back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Savollarga qaytish", callback_data="faq")]
        ]
    )

def admin_approval_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"auth_approve_{user_id}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"auth_reject_{user_id}")]
        ]
    )

def admin_user_categories_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlanganlar", callback_data="admin_users_cat_approved")],
            [InlineKeyboardButton(text="❌ Bloklanganlar", callback_data="admin_users_cat_rejected")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin_menu")]
        ]
    )

def admin_users_menu(users: list, page: int = 1, limit: int = 10, status: str = "approved"):
    start = (page - 1) * limit
    end = start + limit
    current_users = users[start:end]
    
    keyboard = []
    for u in current_users:
        name = u.get('full_name', 'Ismsiz')
        keyboard.append([InlineKeyboardButton(text=f"👤 {name}", callback_data=f"admin_user_detail_{status}_{u['user_id']}")])
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"admin_users_page_{status}_{page-1}"))
    if end < len(users):
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"admin_users_page_{status}_{page+1}"))
        
    if nav_buttons:
        keyboard.append(nav_buttons)
        
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_manage_users")])
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_user_detail_menu(user_id: int, status: str):
    if status == "approved":
        action_btn = InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"admin_revoke_user_{user_id}")
    else:
        action_btn = InlineKeyboardButton(text="✅ Tasdiqlash (Ruxsat berish)", callback_data=f"admin_unblock_user_{user_id}")
        
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [action_btn],
            [InlineKeyboardButton(text="🔙 Ro'yxatga qaytish", callback_data=f"admin_users_cat_{status}")]
        ]
    )

def delete_broadcast_menu(broadcast_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Xabarni bekor qilish (O'chirish)", callback_data=f"delete_broadcast_{broadcast_id}")]
        ]
    )


def attendance_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤒 Bugun borolmaydi", callback_data="att_absent")],
            [InlineKeyboardButton(text="⏰ Kechikib boradi", callback_data="att_late")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ]
    )
def educator_contact_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Xabar yozish", callback_data="contact_educator_start")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ]
    )
def polls_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗳 So`rovnomani boshlash", callback_data="polls_start")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ]
    )


import database

async def attendance_late_keyboard():
    btn1 = await database.get_setting("late_btn_1", "10 minut")
    btn2 = await database.get_setting("late_btn_2", "15 minut")
    btn3 = await database.get_setting("late_btn_3", "20 minut")
    btn4 = await database.get_setting("late_btn_4", "1 soat")
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn1, callback_data="late_10"),
             InlineKeyboardButton(text=btn2, callback_data="late_15")],
            [InlineKeyboardButton(text=btn3, callback_data="late_20"),
             InlineKeyboardButton(text=btn4, callback_data="late_60")],
            [InlineKeyboardButton(text="✍️ O'zim yozaman", callback_data="late_manual")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ]
    )

def admin_attendance_submenu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Matn/rasmni tahrirlash", callback_data="edit_text_attendance")],
            [InlineKeyboardButton(text="⏳ Kechikish tugmalari", callback_data="admin_late_btns")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_edit_texts")]
        ]
    )

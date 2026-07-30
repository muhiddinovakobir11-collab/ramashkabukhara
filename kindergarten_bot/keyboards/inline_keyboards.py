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
        [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="registration")]
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

def admin_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📝 Matnlarni tahrirlash", callback_data="admin_edit_texts")],
            [InlineKeyboardButton(text="📸 Galereyani tahrirlash", callback_data="admin_edit_gallery")],
            [InlineKeyboardButton(text="📢 Xabar tarqatish (Ommaviy)", callback_data="admin_broadcast")],
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
             InlineKeyboardButton(text="❓ FAQ", callback_data="edit_faq")],
            [InlineKeyboardButton(text="🌟 Faol o'quvchilar", callback_data="edit_active_students"),
             InlineKeyboardButton(text="🍲 Taomnoma", callback_data="edit_food_menu")],
            [InlineKeyboardButton(text="💳 To'lovlar qoidalari", callback_data="edit_payment")],
            [InlineKeyboardButton(text="🎥 Kameralar", callback_data="edit_cameras"),
             InlineKeyboardButton(text="🧠 Psixolog", callback_data="edit_psychologist")],
            [InlineKeyboardButton(text="🎂 Tug'ilgan kunlar", callback_data="edit_birthdays"),
             InlineKeyboardButton(text="🎈 Bayramlar", callback_data="edit_events")],
            [InlineKeyboardButton(text="🏆 Yutuqlarimiz", callback_data="edit_achievements"),
             InlineKeyboardButton(text="👗 Bog'cha formasi", callback_data="edit_dress_code")],
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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Rasmlar", callback_data="gal_type_photo"),
             InlineKeyboardButton(text="🎥 Videolar", callback_data="gal_type_video")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
        ]
    )

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

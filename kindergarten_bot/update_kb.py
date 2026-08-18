import codecs

with codecs.open('keyboards/inline_keyboards.py', 'r', 'utf-8') as f:
    content = f.read()

main_old = '''        [InlineKeyboardButton(text="🎓 Vakansiyalar (Ish)", callback_data="vacancies")],
        [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="registration")]'''
main_new = '''        [InlineKeyboardButton(text="🎓 Vakansiyalar (Ish)", callback_data="vacancies")],
        [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="registration")],
        [InlineKeyboardButton(text="🌡 Davomat va ogohlantirish", callback_data="attendance")],
        [InlineKeyboardButton(text="💬 Tarbiyachi bilan aloqa", callback_data="educator_contact")],
        [InlineKeyboardButton(text="📊 Ota-onalar bahosi", callback_data="polls")]'''

content = content.replace(main_old, main_new)

admin_old = '''            [InlineKeyboardButton(text="💼 Vakansiyalar", callback_data="edit_vacancies")],
            [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="edit_registration")],'''
admin_new = '''            [InlineKeyboardButton(text="💼 Vakansiyalar", callback_data="edit_vacancies")],
            [InlineKeyboardButton(text="👶 Farzandni yozdirish", callback_data="edit_registration")],
            [InlineKeyboardButton(text="🌡 Davomat", callback_data="edit_attendance"),
             InlineKeyboardButton(text="💬 Tarbiyachi", callback_data="edit_educator_contact")],
            [InlineKeyboardButton(text="📊 Ota-onalar bahosi", callback_data="edit_polls")],'''

content = content.replace(admin_old, admin_new)

interactive = '''
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
            [InlineKeyboardButton(text="🗳 So'rovnomani boshlash", callback_data="polls_start")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
        ]
    )
'''
if "attendance_action_keyboard" not in content:
    content += interactive

with codecs.open('keyboards/inline_keyboards.py', 'w', 'utf-8') as f:
    f.write(content)

import re

with open('handlers/user_handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
@router.message(StateFilter("UserPoll:waiting_for_feedback"))
async def process_poll_feedback(message: Message, state: FSMContext):
    user_name = message.from_user.full_name
    
    data = await state.get_data()
    star_count = data.get("poll_star", 0)
    star_str = "⭐" * star_count if star_count else "Noma'lum"
    
    if ADMIN_ID:
        try:
            await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📊 <b>Yangi so'rovnoma javobi!</b>\n\n👤 Ota-ona: {user_name}\n⭐️ Baho: {star_str}\n\n💬 Taklif/Fikr:\n{message.text}",
                parse_mode="HTML"
            )
        except Exception:
            pass
            
    await message.reply("✅ Fikringiz qabul qilindi. Kattakon rahmat!", reply_markup=ReplyKeyboardRemove())
    await state.clear()
'''

content = re.sub(
    r'@router\.message\(StateFilter\("UserPoll:waiting_for_feedback"\)\).*?await state\.clear\(\)', 
    replacement.strip(), 
    content, 
    flags=re.DOTALL
)

with open('handlers/user_handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)

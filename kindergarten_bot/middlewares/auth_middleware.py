from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
import database
from config import ADMIN_ID
from states import UserRegistration

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
            
        if str(user.id) == str(ADMIN_ID).strip():
            return await handler(event, data)
            
        db_user = database.get_user(user.id)
        if not db_user:
            return await handler(event, data)
            
        status = db_user.get("status", "pending")
        if status == "approved":
            return await handler(event, data)
            
        # Allowed exceptions for unapproved users
        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)
            
        state: FSMContext = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state in [UserRegistration.waiting_for_name.state, UserRegistration.waiting_for_phone.state]:
                return await handler(event, data)
                
        if isinstance(event, Message):
            await event.answer("🛑 <b>Siz hali ma'muriyat tomonidan tasdiqlanmagansiz.</b>\n\nTasdiqdan o'tish uchun /start ni bosing.", parse_mode="HTML")
        elif isinstance(event, CallbackQuery):
            await event.answer("Siz hali ma'muriyat tomonidan tasdiqlanmagansiz.", show_alert=True)
            
        return

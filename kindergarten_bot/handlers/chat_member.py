from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
import database

router = Router()

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    # Bot bloklandi
    database.update_user_status(event.from_user.id, False)

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    # Bot qulfdan chiqarildi (unblock)
    database.update_user_status(event.from_user.id, True)

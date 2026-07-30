from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo
import database
from keyboards.inline_keyboards import gallery_type_menu, gallery_categories_menu, carousel_keyboard
from config import START_VIDEO_ID

router = Router()

@router.callback_query(F.data == "gallery")
async def gallery_main_menu(callback: CallbackQuery):
    text = "📸 <b>Bizning galereya</b>\n\nNimalarni ko'rmoqchisiz?"
    
    try:
        if START_VIDEO_ID:
            await callback.message.edit_media(
                media=InputMediaVideo(media=START_VIDEO_ID, caption=text, parse_mode="HTML"), 
                reply_markup=gallery_type_menu()
            )
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=gallery_type_menu())
    except Exception:
        try:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=gallery_type_menu())
        except Exception:
            pass
    await callback.answer()

@router.callback_query(F.data.startswith("gal_type_"))
async def gallery_type_selection(callback: CallbackQuery):
    media_type = callback.data.split("_")[2] # photo or video
    m_type_char = 'p' if media_type == 'photo' else 'v'
    text = f"Qaysi jarayon {'rasmlari' if m_type_char == 'p' else 'videolari'}ni ko'rmoqchisiz?"
    
    try:
        if callback.message.video or callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=gallery_categories_menu(m_type_char))
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=gallery_categories_menu(m_type_char))
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("gal_cat_"))
async def gallery_category_selection(callback: CallbackQuery):
    parts = callback.data.split("_")
    media_type = parts[2] # 'p' or 'v'
    category = parts[3]
    
    # Ma'lumotlarni bazadan olish
    media_items = database.get_gallery_media(category, media_type)
    
    if not media_items:
        await callback.answer("Bu bo'limda hozircha fayllar yo'q!", show_alert=True)
        return
        
    # Birinchi elementni ko'rsatish
    await show_carousel_item(callback, media_type, category, media_items, 0)
    await callback.answer()

@router.callback_query(F.data.startswith("gal_nav_"))
async def gallery_navigation(callback: CallbackQuery):
    parts = callback.data.split("_")
    media_type = parts[2]
    category = parts[3]
    index = int(parts[4])
    
    media_items = database.get_gallery_media(category, media_type)
    
    if not media_items or index < 0 or index >= len(media_items):
        await callback.answer("Xatolik yuz berdi.", show_alert=True)
        return
        
    await show_carousel_item(callback, media_type, category, media_items, index)
    await callback.answer()

async def show_carousel_item(callback: CallbackQuery, media_type: str, category: str, media_items: list, index: int):
    item = media_items[index]
    media_id = item[1]
    caption = item[2]
    total = len(media_items)
    
    markup = carousel_keyboard(media_type, category, index, total)
    
    try:
        if media_type == 'p':
            media = InputMediaPhoto(media=media_id, caption=caption, parse_mode="HTML")
        else:
            media = InputMediaVideo(media=media_id, caption=caption, parse_mode="HTML")
            
        await callback.message.edit_media(media=media, reply_markup=markup)
    except Exception:
        pass

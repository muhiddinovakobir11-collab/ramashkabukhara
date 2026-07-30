from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from config import PAYMENT_PROVIDER_TOKEN, ADMIN_ID
import database
from keyboards.inline_keyboards import main_inline_menu

router = Router()

prices = {
    "pay_kichik": {"title": "Kichik guruh to'lovi", "description": "Kichik guruh (2-3 yosh) uchun oylik to'lov", "amount": 1500000},
    "pay_orta": {"title": "O'rta guruh to'lovi", "description": "O'rta guruh (4-5 yosh) uchun oylik to'lov", "amount": 1500000},
    "pay_katta": {"title": "Katta guruh to'lovi", "description": "Katta guruh (6-7 yosh) uchun oylik to'lov", "amount": 1600000},
}

@router.callback_query(F.data.startswith("pay_"))
async def process_payment_selection(callback: CallbackQuery, bot: Bot):
    if not PAYMENT_PROVIDER_TOKEN:
        await callback.answer("Hozircha avtomatik to'lovlar ishlamayapti (Token kiritilmagan).", show_alert=True)
        return
        
    payment_info = prices.get(callback.data)
    if not payment_info:
        await callback.answer("Xatolik: To'lov turi topilmadi.", show_alert=True)
        return
        
    title = payment_info["title"]
    description = payment_info["description"]
    amount = payment_info["amount"] * 100 # UZS tiyinda ko'rsatiladi
    
    labeled_price = LabeledPrice(label=title, amount=amount)
    
    try:
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=title,
            description=description,
            payload=f"invoice_{callback.data}_{callback.from_user.id}",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="UZS",
            prices=[labeled_price],
            start_parameter="kindergarten-payment",
            photo_url="https://img.freepik.com/premium-vector/online-payment-concept-with-3d-credit-card-and-receipt_634289-42.jpg",
            photo_width=512,
            photo_height=512
        )
    except Exception as e:
        await callback.message.reply(f"To'lov tizimida xatolik yuz berdi: {e}")
        
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, bot: Bot):
    payment_info = message.successful_payment
    user = message.from_user
    
    # Bazaga yozish
    database.add_payment(
        user_id=user.id,
        amount=payment_info.total_amount,
        currency=payment_info.currency,
        payload=payment_info.invoice_payload,
        provider_payment_charge_id=payment_info.provider_payment_charge_id
    )
    
    # Ota-onaga rahmat aytish
    await message.reply(
        f"✅ <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"To'lov summasi: {payment_info.total_amount // 100:,.0f} {payment_info.currency}\n"
        f"ID: <code>{payment_info.provider_payment_charge_id}</code>\n\n"
        f"Bog'chamizni tanlaganingiz uchun rahmat!", 
        parse_mode="HTML",
        reply_markup=main_inline_menu(user.id)
    )
    
    # Adminga xabar berish
    if ADMIN_ID:
        admin_text = (
            f"💰 <b>YANGI TO'LOV KELIB TUSHDI!</b>\n\n"
            f"👤 Kimdan: {user.full_name} (@{user.username if user.username else 'yoq'})\n"
            f"💵 Summa: {payment_info.total_amount // 100:,.0f} {payment_info.currency}\n"
            f"📝 Ma'lumot: {payment_info.invoice_payload}\n"
            f"🆔 To'lov ID: <code>{payment_info.provider_payment_charge_id}</code>"
        )
        try:
            await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        except Exception:
            pass

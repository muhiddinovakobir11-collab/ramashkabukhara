import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import BOT_TOKEN
from handlers import user_handlers, registration, chat_member, admin_handlers, gallery_handlers, payment_handlers
import database

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Webhook sozlamalari
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://ramashkabukhara.onrender.com" + WEBHOOK_PATH

async def on_startup(bot: Bot):
    # Eski polling ulanishlarni o'chirish va Webhook o'rnatish
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logging.info("Webhook muvaffaqiyatli o'rnatildi!")

def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return

    # Bot va Dispatcher yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Baza yaratilishi/ulanishi
    database.init_db()

    # Routerlarni ulash
    dp.include_router(chat_member.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(gallery_handlers.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(registration.router)

    # Startup eventiga webhook o'rnatishni qo'shish
    dp.startup.register(on_startup)

    # Aiohttp serverini yaratish
    app = web.Application()
    
    # UptimeRobot uchun yengil ping (Dummy server)
    app.router.add_get('/', lambda request: web.Response(text="Bot is running smoothly on Webhooks!"))
    
    # WebApp handler
    async def webapp_handler(request):
        try:
            with open("webapp.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            return web.Response(text=html_content, content_type="text/html")
        except Exception as e:
            return web.Response(text=f"Error loading WebApp: {e}", status=500)
            
    app.router.add_get('/webapp', webapp_handler)
    
    # Webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Render.com porti
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Veb server portda ishga tushdi: {port}")
    
    # Serverni ishga tushirish (Polling o'rniga)
    web.run_app(app, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()

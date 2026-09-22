import sys, os, certifi, ssl, asyncio, logging, aiohttp

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv('.env')
from config import BOT_TOKEN
from handlers import user_handlers, registration, chat_member, admin_handlers, gallery_handlers, payment_handlers
from middlewares.auth_middleware import AuthMiddleware
import database
from timer_worker import timer_loop

logging.basicConfig(level=logging.DEBUG)

class MySession(AiohttpSession):
    async def create_session(self):
        connector = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(connector=connector)

async def main():
    bot = Bot(token=BOT_TOKEN, session=MySession())
    dp = Dispatcher()

    await database.init_db()
    asyncio.create_task(timer_loop(bot))
    
    dp.update.middleware(AuthMiddleware())
    dp.include_router(chat_member.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(gallery_handlers.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(registration.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook o'chirildi, Polling boshlanmoqda...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

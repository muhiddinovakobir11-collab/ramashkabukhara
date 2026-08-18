import asyncio
import database
from datetime import datetime
import logging
from aiogram.exceptions import TelegramBadRequest

async def timer_loop(bot):
    logging.info("Timer background loop started.")
    while True:
        try:
            timers = await database.get_active_timers()
            now = datetime.now()
            
            for t in timers:
                try:
                    end_time = datetime.fromisoformat(t['end_time'])
                except:
                    await database.delete_timer(t['id'])
                    continue
                
                if now >= end_time:
                    final_text = t['base_text'] + "\n\n⏰ <b>Vaqt tugadi!</b>"
                    try:
                        await bot.edit_message_text(chat_id=t['chat_id'], message_id=t['message_id'], text=final_text, parse_mode="HTML")
                    except TelegramBadRequest as e:
                        pass
                    except Exception:
                        pass
                    await database.delete_timer(t['id'])
                else:
                    diff = end_time - now
                    total_seconds = int(diff.total_seconds())
                    if total_seconds < 0: total_seconds = 0
                    
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    
                    new_text = t['base_text'] + f"\n\n🔄 <b>Qolgan vaqt: {time_str}</b>"
                    try:
                        await bot.edit_message_text(chat_id=t['chat_id'], message_id=t['message_id'], text=new_text, parse_mode="HTML")
                    except TelegramBadRequest as e:
                        if "message to edit not found" in str(e).lower() or "message can't be edited" in str(e).lower():
                            await database.delete_timer(t['id'])
                    except Exception:
                        pass
                        
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Timer loop error: {e}")
            await asyncio.sleep(5)

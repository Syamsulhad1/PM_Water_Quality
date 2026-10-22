import httpx
from app.config import settings
async def send_telegram(message: str, chat_id: str|None=None) -> tuple[bool,str]:
    token=settings.telegram_bot_token; target=chat_id or settings.telegram_chat_id
    if not token or not target: return False,"Telegram belum dikonfigurasi"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r=await client.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":target,"text":message})
            r.raise_for_status()
        return True,"terkirim"
    except Exception as e: return False,str(e)[:250]

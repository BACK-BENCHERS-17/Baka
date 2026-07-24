import random
import string
import asyncio
from datetime import datetime, timedelta
import pytz
from config import TIMEZONE

def generate_random_word(length: int = 16) -> str:
    """Generate random alphanumeric word"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def format_time_remaining(seconds: int) -> str:
    """Format remaining time as Xd Yh Zm"""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:  # Always show at least minutes
        parts.append(f"{minutes}m")
    
    return " ".join(parts)

def get_ist_date() -> str:
    """Get current date in IST"""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d")

def can_claim_daily(last_claim_date: str) -> bool:
    """Check if user can claim daily (IST date-based)"""
    if not last_claim_date:
        return True
    
    today = get_ist_date()
    return last_claim_date != today

async def send_with_typing(update, context, text: str, parse_mode: str = None):
    """Send message with typing indicator"""
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        await asyncio.sleep(random.uniform(0.8, 1.4))
        
        kwargs = {}
        if parse_mode:
            kwargs['parse_mode'] = parse_mode
        
        await update.message.reply_text(text, **kwargs)
    except Exception:
        # Fallback without typing
        try:
            kwargs = {}
            if parse_mode:
                kwargs['parse_mode'] = parse_mode
            await update.message.reply_text(text, **kwargs)
        except Exception:
            pass

def get_mention_html(user_id: int, first_name: str, username: str = None) -> str:
    """Get HTML mention link for user"""
    if username:
        return f'<a href="https://t.me/{username}">{first_name}</a>'
    else:
        return f'<a href="tg://user?id={user_id}">{first_name}</a>'
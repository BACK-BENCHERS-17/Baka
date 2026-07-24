import time
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_protection_expiry, is_premium
from utils.permissions import is_bot, is_baka_bot
from config import BOT_USERNAME

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check command"""
    user = update.effective_user
    message = update.message
    
    # Premium only
    if not await is_premium(user.id):
        await update.message.reply_text("❌ This command is only for Premium users.")
        return
    
    # Check reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await update.message.reply_text("⚠️ Reply to a user to rob.")
        return
    
    target = message.reply_to_message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        await update.message.reply_text("🐥 I am always protected baby.")
        return
    
    # Check if target is a bot
    if is_bot(target):
        await update.message.reply_text("🤖 Specified user is a bot!")
        return
    
    # Ensure target exists
    await ensure_user(target.id, target.first_name, target.username)
    
    # Get protection expiry
    expiry = await get_protection_expiry(target.id)
    now = int(time.time())
    
    if expiry and expiry > now:
        # Send to DM
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(expiry)
            time_str = dt.strftime("%H:%M")
            date_str = dt.strftime("%d/%m/%Y")
            
            await context.bot.send_message(
                user.id,
                f"⏳ {target.first_name}'s protection ends at\n"
                f"{time_str}\n"
                f"{date_str}"
            )
            
            await update.message.reply_text(f"📩 {target.first_name}'s protection details sent to your DM!")
            
        except Exception:
            await update.message.reply_text("⚠️ Could not send DM. Please start a chat with me.")
    else:
        await update.message.reply_text(f"🛡️ {target.first_name} is not protected.")
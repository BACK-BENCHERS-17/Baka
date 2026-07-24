import time
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    ensure_user, get_protection_expiry, set_protection_expiry,
    is_premium, get_user, update_balance
)
from utils.helpers import format_time_remaining
from config import PROTECT_COST

async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /protect command"""
    user = update.effective_user
    # Check if economy is enabled in group
    if chat.type in ["group", "supergroup"]:
        from utils.permissions import is_economy_enabled
        if not await is_economy_enabled(chat.id):
            await update.message.reply_text("⚠️ Economy commands are disabled in this group. Use /open to enable.")
            return
    
    # Check arguments
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /protect <b>1d</b>", parse_mode="HTML")
        return
    
    duration_arg = context.args[0].lower()
    
    # Parse duration - accept both "1" and "1d"
    if duration_arg.endswith('d'):
        try:
            days = int(duration_arg[:-1])
        except ValueError:
            days = 0
    else:
        try:
            days = int(duration_arg)
        except ValueError:
            days = 0
    
    # Validate days
    if days < 1:
        await update.message.reply_text("⚠️ Usage: /protect <b>1d</b>", parse_mode="HTML")
        return
    
    # Check premium status for days > 1
    premium = await is_premium(user.id)
    
    if days > 1 and not premium:
        await update.message.reply_text(
            "❗<b>Normal</b> users can use upto: <b>1d</b>\n"
            "💓 Upgrade to <b>Premium</b>: /pay",
            parse_mode="HTML"
        )
        return
    
    if days > 3:
        await update.message.reply_text(
            "💓 ❗<b>Premium</b> users can use upto: <b>3d</b>",
            parse_mode="HTML"
        )
        return
    
    # Ensure user exists
    await ensure_user(user.id, user.first_name, user.username)
    
    # Check existing protection
    current_expiry = await get_protection_expiry(user.id)
    now = int(time.time())
    
    if current_expiry and current_expiry > now:
        remaining = current_expiry - now
        formatted = format_time_remaining(remaining)
        await update.message.reply_text(f"🛡️ You are already protected!\n⏳ Remaining: <b>{formatted}</b>", parse_mode="HTML")
        return
    
    # Calculate new expiry
    new_expiry = now + (days * 86400)
    
    # Apply protection (free)
    await set_protection_expiry(user.id, new_expiry)
    
    # Send success message
    await update.message.reply_text(f"🛡️ You are now protected for <b>{days}d</b>.", parse_mode="HTML")
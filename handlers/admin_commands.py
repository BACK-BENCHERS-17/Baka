from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_group, get_economy_status, set_economy_status
from utils.permissions import is_admin

async def open_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /open command"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check admin permissions
    if not await is_admin(chat, user.id, context.bot):
        await update.message.reply_text("⚠️ Admin Command only.")
        return
    
    # Ensure group exists in database
    await ensure_group(chat.id, chat.title)
    
    # Enable economy
    await set_economy_status(chat.id, True)
    
    await update.message.reply_text("✅ All economy commands have been enabled.")

async def close_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /close command"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check admin permissions
    if not await is_admin(chat, user.id, context.bot):
        await update.message.reply_text("⚠️ Admin Command only.")
        return
    
    # Ensure group exists in database
    await ensure_group(chat.id, chat.title)
    
    # Disable economy
    await set_economy_status(chat.id, False)
    
    await update.message.reply_text("✅ All economy commands have been disabled.")
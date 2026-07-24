from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_group, get_economy_status, set_economy_status
from utils.permissions import is_admin

async def open_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /open command to enable economy in group"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Group only
    if chat.type == "private":
        await update.message.reply_text("⚠️ This command works in groups only.")
        return
    
    # Check if user is admin
    if not await is_admin(chat, user.id, context.bot):
        await update.message.reply_text("⚠️ Admin Command only.")
        return
    
    # Ensure group exists in database
    await ensure_group(chat.id, chat.title)
    
    # Check current status
    current_status = await get_economy_status(chat.id)
    if current_status:
        await update.message.reply_text("⚠️ Economy commands are already enabled.")
        return
    
    # Enable economy
    await set_economy_status(chat.id, True)
    
    await update.message.reply_text("✅ All economy commands have been enabled.")

async def close_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /close command to disable economy in group"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Group only
    if chat.type == "private":
        await update.message.reply_text("⚠️ This command works in groups only.")
        return
    
    # Check if user is admin
    if not await is_admin(chat, user.id, context.bot):
        await update.message.reply_text("⚠️ Admin Command only.")
        return
    
    # Ensure group exists in database
    await ensure_group(chat.id, chat.title)
    
    # Check current status
    current_status = await get_economy_status(chat.id)
    if not current_status:
        await update.message.reply_text("⚠️ Economy commands are already disabled.")
        return
    
    # Disable economy
    await set_economy_status(chat.id, False)
    
    await update.message.reply_text("✅ All economy commands have been disabled.")
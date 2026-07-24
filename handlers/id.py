from telegram import Update
from telegram.ext import ContextTypes

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /id command"""
    chat = update.effective_chat
    user = update.effective_user
    message = update.message
    
    text = ""
    
    # Check if reply
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        text = f"👤 Replied User ID: {target.id}\n"
    else:
        text = f"👤 Your User ID: {user.id}\n"
    
    # Add group ID if in group
    if chat.type in ["group", "supergroup"]:
        text += f"👥 Group ID: {chat.id}"
    
    await update.message.reply_text(text)
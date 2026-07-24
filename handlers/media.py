from telegram import Update
from telegram.ext import ContextTypes
from database import add_media, get_random_media
from config import OWNER_IDS, BOT_USERNAME
import time

async def addgif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addgif command (owner only)"""
    # Owner only
    if update.effective_user.id not in OWNER_IDS:
        return
    
    # Check reply
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a GIF or Sticker to add it.")
        return
    
    # Check command argument
    if not context.args:
        await update.message.reply_text("Usage: /addgif <command>")
        return
    
    command = context.args[0].lower()
    msg = update.message.reply_to_message
    
    # Determine media type
    if msg.animation:  # GIF
        file_id = msg.animation.file_id
        media_type = "gif"
    elif msg.sticker:
        file_id = msg.sticker.file_id
        media_type = "sticker"
    else:
        await update.message.reply_text("❌ Unsupported media type.")
        return
    
    # Add to database
    await add_media(command, media_type, file_id, update.effective_user.id)
    
    await update.message.reply_text("✅ Media added successfully!")

async def sticker_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sticker/GIF replies to Baka bot"""
    msg = update.message
    
    # Check if reply to Baka
    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        return
    
    if msg.reply_to_message.from_user.username != BOT_USERNAME:
        return
    
    # Check if message contains sticker or GIF
    if msg.sticker:
        # Get random sticker
        sticker_id = await get_random_media("baka_stickers", "sticker")
        if sticker_id:
            try:
                await msg.reply_sticker(sticker_id)
            except Exception:
                pass
    
    elif msg.animation:  # GIF
        # Get random sticker for GIF reply too
        sticker_id = await get_random_media("baka_stickers", "sticker")
        if sticker_id:
            try:
                await msg.reply_sticker(sticker_id)
            except Exception:
                pass
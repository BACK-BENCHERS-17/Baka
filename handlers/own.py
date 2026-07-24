from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BOT_USERNAME

async def own(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /own command (sticker kanging)"""
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("❌ Reply to a sticker and use this command")
        return
    
    user = update.effective_user
    sticker = update.message.reply_to_message.sticker
    
    # Check sticker type
    is_video = sticker.is_video if hasattr(sticker, 'is_video') else False
    
    # Create pack name
    pack_type = "video" if is_video else "static"
    pack_name = f"user_{user.id}_{pack_type}_by_{BOT_USERNAME.replace('@', '')}"
    
    # Send initial message
    msg = await update.message.reply_text("🪄 Saving sticker...")
    
    # In a real implementation, you would use:
    # 1. createNewStickerSet for first sticker
    # 2. addStickerToSet for subsequent stickers
    # 3. Check pack limits and create pack_2, pack_3 etc.
    
    # For this example, we'll simulate success
    pack_title = f"{user.first_name}'s {'Video ' if is_video else ''}Sticker Pack"
    
    # Edit message with success
    keyboard = [[InlineKeyboardButton("Open Sticker Pack", url=f"https://t.me/addstickers/{pack_name}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"✅ Sticker saved to your {'video' if is_video else 'static'} pack 💖\n👉 Open Sticker Pack"
    
    await msg.edit_text(text, reply_markup=reply_markup)
import random
from telegram import Update
from telegram.ext import ContextTypes
from database import get_random_media
from utils.permissions import is_baka_bot
from config import BOT_USERNAME

# Special responses for Baka bot
SPECIAL_BAKA = {
    "kiss": "4me? 🤭",
    "hug": "notty boiii!! 😉",
    "slap": "What doing? 😑",
    "punch": "Punch back to you 😑",
    "bite": "Hehe, notty u! 😉"
}

# Command templates - EXACT TEXT as specified
ACTION_TEXTS = {
    "kiss": ("gave a sweet kiss to", "😘💋"),
    "hug": ("sent a hug to", "🤗"),
    "slap": ("slapped", "👋"),
    "punch": ("punched really hard", "👊"),
    "bite": ("gave a naughty bite to", "😁")
}

# Reply error messages
REPLY_ERRORS = {
    "kiss": "Reply to someone! 😘",
    "hug": "Reply to someone! 🤗",  # Fixed emoji from 🫂 to 🤗
    "slap": "Reply to someone! 👋",
    "punch": "Reply to someone! 👊",
    "bite": "Reply to someone! 😈"  # Using 😈 instead of 😁 for error
}

async def action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """Handle action commands (kiss, hug, slap, punch, bite)"""
    message = update.message
    
    # Check reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        error_msg = REPLY_ERRORS.get(action, "Reply to someone!")
        await update.message.reply_text(error_msg)
        return
    
    sender = message.from_user
    target = message.reply_to_message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        response = SPECIAL_BAKA.get(action, "🙂")
        await update.message.reply_text(response)
        return
    
    # Send GIF first
    gif_file_id = await get_random_media(action, "gif")
    if gif_file_id:
        try:
            await update.message.reply_animation(gif_file_id)
        except Exception:
            pass  # Skip if GIF fails
    
    # Send action message with EXACT formatting
    text_template, emoji = ACTION_TEXTS[action]
    await update.message.reply_text(f"{sender.first_name} {text_template} {target.first_name} {emoji}")

# Individual handlers - Register these in main.py
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await action_handler(update, context, "kiss")

async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await action_handler(update, context, "hug")

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await action_handler(update, context, "slap")

async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await action_handler(update, context, "punch")

async def bite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await action_handler(update, context, "bite")
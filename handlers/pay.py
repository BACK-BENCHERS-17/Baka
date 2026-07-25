from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PAYMENT_LINK, OWNER_PROFILE
from handlers.premium import PREMIUM_IMG, PREMIUM_CAPTION, premium_keyboard


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pay command — shows premium info with QR image"""
    try:
        await update.message.reply_photo(
            photo=PREMIUM_IMG,
            caption=PREMIUM_CAPTION,
            parse_mode="HTML",
            reply_markup=premium_keyboard()
        )
    except Exception:
        await update.message.reply_text(
            PREMIUM_CAPTION,
            parse_mode="HTML",
            reply_markup=premium_keyboard()
        )

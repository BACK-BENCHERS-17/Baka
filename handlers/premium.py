from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_PROFILE

# Direct image URL
PREMIUM_IMG = "https://i.ibb.co/q3mmJgM3/IMG-20260724-170231-155.jpg"

PREMIUM_CAPTION = (
    "💖🌸 <b>𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐔𝐁𝐒𝐂𝐑𝐈𝐏𝐓𝐈𝐎𝐍</b> 🌸💖\n\n"

    "<blockquote>"
    "💞 <b>Price:</b>  <code>₹19 Only</code>\n"
    "🎀 <b>Validity:</b>  <code>1 Month</code>"
    "</blockquote>\n\n"

    "💎🩷 <b>𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒</b> 🩷💎\n\n"

    "<blockquote expandable>"
    "🌷 <code>/check</code>  ✔  Exclusive Access\n"
    "💖 <code>/protect</code>  ✔  2 Days Duration\n"
    "🎀 <code>/kill</code>  ✔  Higher Reward\n"
    "🌸 <code>/rob</code>  ✔  High Limit\n"
    "💝  ✔  Free Revive Boost\n"
    "🩷  ✔  Priority Support\n"
    "💗  ✔  Exclusive Premium Commands\n"
    "🌺  ✔  Faster Game Progress\n"
    "💓  ✔  Early Access To New Features\n"
    "🎗  ✔  Special Premium Badge\n"
    "🌹  ✔  Premium Event Rewards\n"
    "💕  ✔  More Future Updates"
    "</blockquote>\n\n"

    "📌🌸 <b>𝐇𝐎𝐖 𝐓𝐎 𝐁𝐔𝐘</b> 🌸📌\n\n"

    "<blockquote>"
    "🦋  Pay using QR below\n"
    "🎀  Screenshot lo\n"
    "💌  Owner DM mein bhejo\n"
    "🌷  Approval ka wait karo\n\n"
    "⚡ <b>Payment ke baad → Premium Instantly Active</b> ⚡"
    "</blockquote>"
)

def premium_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 💳 𝐁𝐮𝐲 𝐍𝐨𝐰 — ₹𝟏𝟗", url=OWNER_PROFILE),
        ],
        [
            InlineKeyboardButton("🔵 💌 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐎𝐰𝐧𝐞𝐫", url=OWNER_PROFILE),
            InlineKeyboardButton("🩷 🌸 𝐕𝐢𝐞𝐰 𝐐𝐑", callback_data="prem_qr"),
        ],
    ])


async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /premium command"""
    try:
        await update.message.reply_photo(
            photo=PREMIUM_IMG,
            caption=PREMIUM_CAPTION,
            parse_mode="HTML",
            reply_markup=premium_keyboard()
        )
    except Exception:
        # Fallback to text if image fails
        await update.message.reply_text(
            PREMIUM_CAPTION,
            parse_mode="HTML",
            reply_markup=premium_keyboard()
        )


async def premium_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for premium inline buttons"""
    query = update.callback_query
    await query.answer()

    if query.data == "prem_qr":
        try:
            await query.message.reply_photo(
                photo=PREMIUM_IMG,
                caption=(
                    "🌸 <b>QR Code — ₹19 Pay Karo</b>\n\n"
                    "<blockquote>"
                    "📸 Screenshot lo → Owner ko bhejo\n"
                    "⚡ Premium turant active hoga!"
                    "</blockquote>"
                ),
                parse_mode="HTML"
            )
        except Exception:
            await query.answer("⚠️ Image load nahi hui, Owner ko DM karo!", show_alert=True)

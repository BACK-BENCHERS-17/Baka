from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BOT_USERNAME, OWNER_PROFILE, FRIENDS_GROUP, GAMES_GROUP

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    text = f"""✨ 𝐇𝐞𝐲 {user.first_name} ~
𖦹 Yᴏᴜ'ʀᴇ Tᴀʟᴋɪɴɢ Tᴏ Bᴀᴋᴀ, A Sᴀssʏ Cᴜᴛɪᴇ Gɪʀʟ 💕

𖥔 Cʜᴏᴏsᴇ Aɴ Oᴘᴛɪᴏɴ Bᴇʟᴏᴡ:"""
    
    keyboard = [
        [
            InlineKeyboardButton("𖥔 Tᴀʟᴋ Tᴏ Bᴀᴋᴀ 💬", callback_data="talk_baka"),
            InlineKeyboardButton("𖥔 Bʟᴀᴄ 🥀", url=OWNER_PROFILE)
        ],
        [
            InlineKeyboardButton("𖥔 Fʀɪᴇɴᴅꜱ 🧸", url=FRIENDS_GROUP),
            InlineKeyboardButton("𖥔 Gᴀᴍᴇꜱ 🎮", url=GAMES_GROUP)
        ],
        [
            InlineKeyboardButton(
                "➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ 👥",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "talk_baka":
        await query.message.reply_text(
            "To talk to me, just send me any message 💬✨"
        )
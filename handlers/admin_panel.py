from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_IDS
from utils.permissions import is_admin


OWNER_PANEL_TEXT = (
    "👑 <b>Oᴡɴᴇʀ Pᴀɴᴇʟ — Bᴀᴋᴀ Bᴏᴛ</b>\n\n"
    "<blockquote>"
    "🔐 Yᴇ ᴘᴀɴᴇʟ sɪʀꜰ ᴏᴡɴᴇʀ ᴋᴇ ʟɪʏᴇ ʜᴀɪ!"
    "</blockquote>\n\n"

    "💎 <b>Pʀᴇᴍɪᴜᴍ Mᴀɴᴀɢᴇ</b>\n"
    "<code>/addpremium [uid] [days]</code>   — Pʀᴇᴍɪᴜᴍ ᴅᴏ\n"
    "<code>/removepremium [uid]</code>   — Pʀᴇᴍɪᴜᴍ ʜᴀᴛᴀᴏ\n\n"

    "💰 <b>Bᴀʟᴀɴᴄᴇ Mᴀɴᴀɢᴇ</b>\n"
    "<code>/setbal [uid] [amount]</code>   — Bᴀʟᴀɴᴄᴇ sᴇᴛ ᴋᴀʀᴏ\n"
    "<code>/resetbal [uid]</code>   — Bᴀʟᴀɴᴄᴇ ʀᴇsᴇᴛ ᴋᴀʀᴏ\n\n"

    "📢 <b>Bʀᴏᴀᴅᴄᴀsᴛ</b>\n"
    "<code>/broadcast</code>   — Sᴀʙ ᴜsᴇʀs ᴋᴏ ᴍᴇssᴀɢᴇ ᴋᴀʀᴏ\n\n"

    "🤖 <b>Sʏsᴛᴇᴍ</b>\n"
    "<code>/addgif [cmd]</code>   — GIF ᴄᴏᴍᴍᴀɴᴅ ᴀᴅᴅ ᴋᴀʀᴏ\n"
    "<code>/ownercommands</code>   — Yᴇ ᴘᴜʀɪ ʟɪsᴛ ᴅᴇᴋʜᴏ"
)

ADMIN_MOD_TEXT = (
    "🛡️ <b>Aᴅᴍɪɴ Mᴏᴅᴇʀᴀᴛɪᴏɴ Cᴍᴅs</b>\n\n"
    "<blockquote>"
    "Sᴀʙ ᴄᴍᴅs <b>.(ᴅᴏᴛ)</b> ᴘʀᴇꜰɪx sᴇ\n"
    "Rᴇᴘʟʏ ᴋᴀʀᴋᴇ ɪsᴛᴇᴍᴀᴀʟ ᴋᴀʀᴏ"
    "</blockquote>\n\n"

    "⚠️ <b>Wᴀʀɴ Sʏsᴛᴇᴍ</b>\n"
    "<code>.warn</code>   → User ᴋᴏ ᴡᴀʀɴ ᴋᴀʀᴏ\n"
    "<code>.unwarn</code>   → 1 ᴡᴀʀɴɪɴɢ ᴋᴀᴍ ᴋᴀʀᴏ\n"
    "┗━ <i>3 ᴡᴀʀɴɪɴɢs = ᴀᴜᴛᴏ ʙᴀɴ ☠️</i>\n\n"

    "🔇 <b>Mᴜᴛᴇ</b>\n"
    "<code>.mute 10m</code>   → Mᴜᴛᴇ <i>(m=ᴍɪɴ · h=ʜʀ · d=ᴅᴀʏ · w=ᴡᴇᴇᴋ)</i>\n"
    "<code>.unmute</code>   → Uɴᴍᴜᴛᴇ ᴋᴀʀᴏ\n\n"

    "🚫 <b>Bᴀɴ &amp; Kɪᴄᴋ</b>\n"
    "<code>.ban</code>   → Pᴇʀᴍᴀɴᴇɴᴛ ʙᴀɴ\n"
    "<code>.unban [uid]</code>   → Uɴʙᴀɴ ᴋᴀʀᴏ\n"
    "<code>.kick</code>   → Gʀᴏᴜᴘ sᴇ ɴɪᴋᴀʟᴏ\n\n"

    "⬆️ <b>Rᴀɴᴋ Mᴀɴᴀɢᴇ</b>\n"
    "<code>.promote</code>   → Aᴅᴍɪɴ ʙᴀɴᴀᴏ\n"
    "<code>.demote</code>   → Aᴅᴍɪɴ sᴇ ʜᴀᴛᴀᴏ\n\n"

    "📌 <b>Mᴇssᴀɢᴇ Cᴏɴᴛʀᴏʟ</b>\n"
    "<code>.pin</code>   → Mᴇssᴀɢᴇ ᴘɪɴ ᴋᴀʀᴏ\n"
    "<code>.unpin</code>   → Uɴᴘɪɴ ᴋᴀʀᴏ\n"
    "<code>.d</code>   → Mᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇ ᴋᴀʀᴏ\n\n"

    "💹 <b>Eᴄᴏɴᴏᴍʏ Tᴏɢɢʟᴇ</b>\n"
    "<code>/open</code>   → Eᴄᴏɴᴏᴍʏ ᴏɴ ᴋᴀʀᴏ\n"
    "<code>/close</code>   → Eᴄᴏɴᴏᴍʏ ᴏꜰꜰ ᴋᴀʀᴏ"
)

ACCESS_DENIED_TEXT = (
    "🔒 <b>Aᴄᴄᴇss Dᴇɴɪᴇᴅ!</b>\n\n"
    "<blockquote>"
    "❌ Yᴇ ᴘᴀɴᴇʟ sɪʀꜰ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs\n"
    "ᴀᴜʀ ʙᴏᴛ ᴏᴡɴᴇʀ ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ!"
    "</blockquote>"
)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command — owner or group admin only."""
    user = update.effective_user
    chat = update.effective_chat

    is_owner = user.id in OWNER_IDS

    # In groups also allow group admins
    is_grp_admin = False
    if chat.type != "private":
        is_grp_admin = await is_admin(chat, user.id, context.bot)

    if not is_owner and not is_grp_admin:
        await update.message.reply_text(ACCESS_DENIED_TEXT, parse_mode="HTML")
        return

    if is_owner:
        # Owner sees full owner panel + toggle button for mod cmds
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🛡️ Mᴏᴅᴇʀᴀᴛɪᴏɴ Cᴍᴅs", callback_data="adminp_mod"),
            ]
        ])
        await update.message.reply_text(
            OWNER_PANEL_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        # Group admin sees only moderation commands
        await update.message.reply_text(ADMIN_MOD_TEXT, parse_mode="HTML")


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for admin panel inline buttons."""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "adminp_mod":
        if user.id not in OWNER_IDS:
            await query.answer("❌ Sirf owner dekh sakta hai!", show_alert=True)
            return
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Owner Panel", callback_data="adminp_back")]
        ])
        await query.edit_message_text(
            ADMIN_MOD_TEXT,
            parse_mode="HTML",
            reply_markup=back_kb
        )

    elif query.data == "adminp_back":
        if user.id not in OWNER_IDS:
            await query.answer("❌ Sirf owner dekh sakta hai!", show_alert=True)
            return
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🛡️ Mᴏᴅᴇʀᴀᴛɪᴏɴ Cᴍᴅs", callback_data="adminp_mod"),
            ]
        ])
        await query.edit_message_text(
            OWNER_PANEL_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard
        )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BOT_USERNAME, OWNER_PROFILE, FRIENDS_GROUP, GAMES_GROUP, OWNER_IDS
from utils.permissions import is_admin


# ─────────────────────────────────────────────
#  Keyboard builders
# ─────────────────────────────────────────────

def start_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟣 💬 Tᴀʟᴋ ᴛᴏ Bᴀᴋᴀ", callback_data="talk_baka"),
            InlineKeyboardButton("🔵 📖 Hᴇʟᴘ & Cᴍᴅs", callback_data="help_home"),
        ],
        [
            InlineKeyboardButton("🟢 🎮 Gᴀᴍᴇs", callback_data="help_games"),
            InlineKeyboardButton("🔴 🛡️ Aᴅᴍɪɴ Pᴀɴᴇʟ", callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("🩷 🥀 Kʜᴜsʜɪ", url=OWNER_PROFILE),
            InlineKeyboardButton("🟡 🧸 Fʀɪᴇɴᴅs", url=FRIENDS_GROUP),
        ],
        [
            InlineKeyboardButton(
                "🟠 ➕ Aᴅᴅ Mᴇ ᴛᴏ Yᴏᴜʀ Gʀᴏᴜᴘ 👥",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ]
    ])


def help_home_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟡 💰 Economy",      callback_data="help_economy"),
            InlineKeyboardButton("🟢 🎮 Games",        callback_data="help_games"),
        ],
        [
            InlineKeyboardButton("🟣 🎭 Fun & Actions", callback_data="help_fun"),
            InlineKeyboardButton("🔴 🛡️ Admin Cmds",   callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("⬅️ 🏠 Back to Start", callback_data="back_start"),
        ]
    ])


def back_help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 📖 Help Menu", callback_data="help_home"),
            InlineKeyboardButton("🏠 Start",        callback_data="back_start"),
        ]
    ])


# ─────────────────────────────────────────────
#  Message texts
# ─────────────────────────────────────────────

def start_text(name: str) -> str:
    return (
        f"✨ <b>Hᴇʏ {name}!</b>\n"
        "𖦹 <i>Yᴏᴜ'ʀᴇ ᴛᴀʟᴋɪɴɢ ᴛᴏ Bᴀᴋᴀ — Sassʏ Cᴜᴛɪᴇ Gɪʀʟ 💕</i>\n\n"
        "<blockquote>"
        "🤖 Mᴀɪ ᴇᴋ ꜰᴜʟʟ-ꜰᴇᴀᴛᴜʀᴇᴅ ɢʀᴏᴜᴘ ʙᴏᴛ ʜᴜɴ —\n"
        "Gᴀᴍᴇs 🎮 · Eᴄᴏɴᴏᴍʏ 💰 · Aᴅᴍɪɴ ᴛᴏᴏʟs 🛡️ · Aɪ Cʜᴀᴛ 🧠"
        "</blockquote>\n\n"
        "<b>Nɪᴄʜᴇ sᴇ ᴄʜᴜɴᴏ 👇</b>"
    )


HELP_HOME_TEXT = (
    "📖 <b>Bᴀᴋᴀ — Hᴇʟᴘ Mᴇɴᴜ</b>\n\n"
    "<blockquote>"
    "Nɪᴄʜᴇ ᴅɪʏᴇ ʙᴜᴛᴛᴏɴs sᴇ ᴀᴘɴɪ ᴘᴀsᴀɴᴅ ᴋɪ ᴄᴀᴛᴇɢᴏʀʏ ᴄʜᴜɴᴏ:"
    "</blockquote>\n\n"
    "💰 <b>Economy</b> — Cᴏɪɴs, ʀᴏʙ, ᴋɪʟʟ, ɪᴛᴇᴍs, ɢɪꜰᴛs\n"
    "🎮 <b>Games</b> — Cᴀʀᴅ, Bʟᴜꜰꜰ, Hᴀᴄᴋ, Rᴏᴜʟᴇᴛᴛᴇ, Bᴏᴍʙ, Wᴏʀᴅ\n"
    "🎭 <b>Fun & Actions</b> — Cᴏᴜᴘʟᴇs, ᴍᴇᴛᴇʀs, ᴋɪss/ʜᴜɢ/sʟᴀᴘ\n"
    "🛡️ <b>Admin</b> — Wᴀʀɴ, ᴍᴜᴛᴇ, ʙᴀɴ, ᴘʀᴏᴍᴏᴛᴇ, ᴘɪɴ"
)


ECONOMY_TEXT = (
    "💰 <b>Eᴄᴏɴᴏᴍʏ Cᴏᴍᴍᴀɴᴅs</b>\n\n"
    "<blockquote>Sɪʀꜰ ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴋᴀᴀᴍ ᴋᴀʀᴛᴇ ʜᴀɪɴ 🏘️</blockquote>\n\n"
    "<code>/daily</code>   — Rᴏᴢ ᴋᴇ ᴄᴏɪɴs ʟᴏ <i>(1000 / 2000 ᴘʀᴇᴍɪᴜᴍ)</i>\n"
    "<code>/bal</code>   — Aᴘɴᴀ ʙᴀʟᴀɴᴄᴇ ᴅᴇᴋʜᴏ\n"
    "<code>/balance @user</code>   — Kɪsɪ ᴋᴀ ʙᴀʟᴀɴᴄᴇ ᴅᴇᴋʜᴏ\n"
    "<code>/give @user 500</code>   — Cᴏɪɴs ᴅᴏ (ᴛᴀx ᴋᴀᴛᴛᴀ)\n"
    "<code>/pay @user 500</code>   — Pᴀʏ ᴋᴀʀᴏ\n"
    "<code>/rob @user</code>   — Kɪsɪ ᴋᴏ ʟᴜᴛᴏ 🔫\n"
    "<code>/kill @user</code>   — Kɪsɪ ᴋᴏ ᴍᴀᴀʀᴏ ☠️\n"
    "<code>/protect</code>   — Xᴜᴅ ᴋᴏ ʙᴀᴄʜᴀᴏ 🛡️\n"
    "<code>/revive</code>   — Xᴜᴅ ᴋᴏ ᴊɪʟᴀᴏ ❤️\n"
    "<code>/claim</code>   — Gʀᴏᴜᴘ ᴋᴀ ᴄʟᴀɪᴍ ʟᴏ 👑\n"
    "<code>/check @user</code>   — Sᴛᴀᴛᴜs ᴄʜᴇᴄᴋ ᴋᴀʀᴏ\n\n"
    "<blockquote expandable>🛍️ <b>Iᴛᴇᴍs &amp; Gɪꜰᴛs</b>\n"
    "<code>/items</code>   — Sʜᴏᴘ ᴅᴇᴋʜᴏ\n"
    "<code>/item rose</code>   — Iᴛᴇᴍ ᴋʜᴀʀɪᴅᴏ\n"
    "<code>/gift @user rose</code>   — Kɪsɪ ᴋᴏ ɢɪꜰᴛ ᴅᴏ 🎁\n"
    "<code>/toprich</code>   — Sᴀʙsᴇ ᴀᴍɪʀ ʟᴏɢ 💎\n"
    "<code>/topkill</code>   — Sᴀʙsᴇ ᴢʏᴀᴅᴀ ᴋɪʟʟ 🏆</blockquote>"
)


GAMES_TEXT = (
    "🎮 <b>Gᴀᴍᴇs Mᴇɴᴜ</b>\n\n"
    "<blockquote>Sᴀʙ ɢᴀᴍᴇs ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴋʜᴇʟᴏ!\n"
    "<code>/game</code> — ꜰᴜʟʟ ɢᴀᴍᴇ ᴍᴇɴᴜ ᴋᴇ ʟɪʏᴇ</blockquote>\n\n"

    "🃏 <b>Card Game</b>\n"
    "<code>/card 500</code>   — Gᴀᴍᴇ sʜᴜʀᴜ ᴋᴀʀᴏ\n"
    "<code>/bet</code>   — Jᴏɪɴ ᴋᴀʀᴏ\n"
    "<code>/flip A</code>   — Cᴀʀᴅ ᴄʜᴜɴᴏ (A/B/C/D)\n\n"

    "🎭 <b>Bluff Game</b>\n"
    "<code>/bluff 500</code>   — Gᴀᴍᴇ sʜᴜʀᴜ ᴋᴀʀᴏ\n"
    "<code>/enter</code>   — Jᴏɪɴ ᴋᴀʀᴏ\n"
    "<code>/drop 7</code>   — Cᴀʀᴅ ᴅᴀᴀʟᴏ (ᴊʜᴏᴏᴛʜ ʙʜɪ ᴄʜᴀʟᴇɢᴀ!)\n"
    "<code>/judge</code>   — Sᴀᴍɴᴇ ᴡᴀʟᴇ ᴋᴏ ᴘᴀᴋᴅᴏ 🕵️\n\n"

    "💻 <b>Hack Game</b>\n"
    "<code>/hack 500</code>   — Gᴀᴍᴇ sʜᴜʀᴜ ᴋᴀʀᴏ\n"
    "<code>/register</code>   — Jᴏɪɴ ᴋᴀʀᴏ\n"
    "<code>/guess 1234</code>   — 4-ᴅɪɢɪᴛ ᴄᴏᴅᴇ ᴄʀᴀᴄᴋ ᴋᴀʀᴏ 🎯\n"
    "<code>/end</code>   — Gᴀᴍᴇ ᴋʜᴀᴛᴀᴍ ᴋᴀʀᴏ\n\n"

    "🎰 <b>Roulette</b>\n"
    "<code>/roulette 500</code>   — Gᴀᴍᴇ sʜᴜʀᴜ ᴋᴀʀᴏ\n"
    "<code>/join</code>   — Jᴏɪɴ ᴋᴀʀᴏ\n"
    "<code>/bid 200</code>   — Hᴀʀ ʀᴀᴜɴᴅ ᴍᴇɪɴ ʙɪᴅ ᴋᴀʀᴏ\n\n"

    "💣 <b>Bomb Game</b>\n"
    "<code>/bomb</code>   — Bᴏᴍʙ sʜᴜʀᴜ ᴋᴀʀᴏ\n"
    "<code>/join</code>   — Jᴏɪɴ ᴋᴀʀᴏ\n"
    "<code>/pass @user</code>   — Bᴏᴍʙ ᴘᴀss ᴋᴀʀᴏ 💥\n\n"

    "📝 <b>Word Game</b>\n"
    "<code>/wordgame</code>   — Sʜᴜʀᴜ ᴋᴀʀᴏ\n"
    "<code>/enter</code>   — Jᴏɪɴ ᴋᴀʀᴏ\n\n"

    "<blockquote><code>/rank</code>   — Aᴘɴɪ ɢᴀᴍᴇ ʀᴀɴᴋ ᴅᴇᴋʜᴏ\n"
    "<code>/leaders</code>   — Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ 🏆</blockquote>"
)


FUN_TEXT = (
    "🎭 <b>Fᴜɴ &amp; Cᴏᴜᴘʟᴇs Cᴏᴍᴍᴀɴᴅs</b>\n\n"
    "<blockquote>Gʀᴏᴜᴘ ᴍᴇɪɴ ᴍᴀsᴛɪ ᴋᴀʀᴏ! 🥳</blockquote>\n\n"

    "💑 <b>Cᴏᴜᴘʟᴇs</b>\n"
    "<code>/couples</code>   — Aᴀᴊ ᴋᴇ ᴄᴏᴜᴘʟᴇ 💕\n"
    "<code>/crush</code>   — Kɪsɪ ᴋᴀ ᴄʀᴜsʜ ᴅᴇᴋʜᴏ 💘\n"
    "<code>/love</code>   — Lᴏᴠᴇ ᴍᴇᴛᴇʀ ❤️\n\n"

    "📊 <b>Mᴇᴛᴇʀs</b>\n"
    "<code>/brain @user</code>   — Dɪᴍᴀɢ ᴄʜᴇᴄᴋ 🧠\n"
    "<code>/look @user</code>   — Kɪᴛɴᴀ sᴜɴᴅᴀʀ ʜᴀɪ 😍\n"
    "<code>/stupid_meter @user</code>   — Uʟʟᴜ ᴍᴇᴛᴇʀ 🦉\n\n"

    "🎲 <b>Fᴜɴ Cᴏᴍᴍᴀɴᴅs</b>\n"
    "<code>/truth</code>   — Sᴀᴄʜ ʙᴏʟᴏ 🫣\n"
    "<code>/dare</code>   — Dᴀʀᴇ ᴋᴀʀᴏ 😈\n"
    "<code>/puzzle</code>   — Dɪᴍᴀɢ ᴘʜᴀɴsᴀᴏ 🧩\n"
    "<code>/music</code>   — Gᴀᴀɴᴀ sᴜɴᴏ 🎵\n\n"

    "💥 <b>Aᴄᴛɪᴏɴs</b> <i>(reply ᴋᴀʀᴋᴇ)</i>\n"
    "<code>/kiss @user</code>   — 😘\n"
    "<code>/hug @user</code>   — 🤗\n"
    "<code>/slap @user</code>   — 👋\n"
    "<code>/punch @user</code>   — 👊\n"
    "<code>/bite @user</code>   — 🫦"
)


ADMIN_TEXT = (
    "🛡️ <b>Aᴅᴍɪɴ Cᴏᴍᴍᴀɴᴅs</b>\n\n"
    "<blockquote>"
    "Yᴇ ᴄᴍᴅs sɪʀꜰ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ!\n"
    "Sᴀʙ <b>.(ᴅᴏᴛ)</b> ᴘʀᴇꜰɪx sᴇ — ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ ɪsᴛᴇᴍᴀᴀʟ ᴋᴀʀᴏ"
    "</blockquote>\n\n"

    "⚠️ <b>Wᴀʀɴ Sʏsᴛᴇᴍ</b>\n"
    "<code>.warn</code>   → User ᴋᴏ ᴡᴀʀɴ ᴋᴀʀᴏ\n"
    "<code>.unwarn</code>   → 1 ᴡᴀʀɴɪɴɢ ᴋᴀᴍ ᴋᴀʀᴏ\n"
    "┗━ <i>3 ᴡᴀʀɴɪɴɢs = ᴀᴜᴛᴏ ʙᴀɴ ☠️</i>\n\n"

    "🔇 <b>Mᴜᴛᴇ</b>\n"
    "<code>.mute 10m</code>   → Mᴜᴛᴇ <i>(m/h/d/w)</i>\n"
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
    "<code>/close</code>   → Eᴄᴏɴᴏᴍʏ ᴏꜰꜰ ᴋᴀʀᴏ\n\n"

    "<blockquote>👑 Owner-only full panel ke liye: <code>/admin</code></blockquote>"
)


# ─────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        start_text(user.first_name),
        reply_markup=start_keyboard(),
        parse_mode="HTML"
    )


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    # ── Back to start ──
    if data == "back_start":
        await query.edit_message_text(
            start_text(user.first_name),
            reply_markup=start_keyboard(),
            parse_mode="HTML"
        )

    # ── Talk to Baka ──
    elif data == "talk_baka":
        await query.message.reply_text(
            "💬 <b>Mᴜᴊʜsᴇ ʙᴀᴀᴛ ᴋᴀʀɴɪ ʜᴀɪ?</b>\n\n"
            "<blockquote>Bᴀs ᴋᴜᴄʜ ʙʜɪ ʟɪᴋʜᴏ — ᴍᴀɪ ʀᴇᴘʟʏ ᴋᴀʀᴜɴɢɪ ✨</blockquote>",
            parse_mode="HTML"
        )

    # ── Help home ──
    elif data == "help_home":
        await query.edit_message_text(
            HELP_HOME_TEXT,
            reply_markup=help_home_keyboard(),
            parse_mode="HTML"
        )

    # ── Economy ──
    elif data == "help_economy":
        await query.edit_message_text(
            ECONOMY_TEXT,
            reply_markup=back_help_keyboard(),
            parse_mode="HTML"
        )

    # ── Games ──
    elif data == "help_games":
        await query.edit_message_text(
            GAMES_TEXT,
            reply_markup=back_help_keyboard(),
            parse_mode="HTML"
        )

    # ── Fun ──
    elif data == "help_fun":
        await query.edit_message_text(
            FUN_TEXT,
            reply_markup=back_help_keyboard(),
            parse_mode="HTML"
        )

    # ── Admin cmds ──
    elif data == "help_admin":
        await query.edit_message_text(
            ADMIN_TEXT,
            reply_markup=back_help_keyboard(),
            parse_mode="HTML"
        )

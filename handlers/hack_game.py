import asyncio
import random
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, update_balance, is_premium
from utils.permissions import GROUP_ONLY_MSG

HACK_GAMES = {}  # chat_id -> HackGame
JOIN_WINDOW = 60
GAME_TIMEOUT = 300  # 5 minutes


def _generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])


def _bulls_cows(secret, guess):
    """Bulls = right digit right pos; Cows = right digit wrong pos."""
    bulls = sum(s == g for s, g in zip(secret, guess))
    cows = sum(min(secret.count(d), guess.count(d)) for d in set(guess)) - bulls
    return bulls, cows


class HackGame:
    def __init__(self, chat_id, amount, starter_id, code):
        self.chat_id = chat_id
        self.amount = amount
        self.starter_id = starter_id
        self.code = code
        self.players = {}   # uid -> {name}
        self.guesses = {}   # uid -> count
        self.started = False
        self.task = None
        self.timeout_task = None


async def hack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hack — start hack game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id in HACK_GAMES:
        await update.message.reply_text("💻 A hack game is already active!")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /hack <amount>")
        return
    amount = int(context.args[0])
    if amount < 50:
        await update.message.reply_text("❌ Minimum bet is $50")
        return
    await ensure_user(user.id, user.first_name, user.username)
    ud = await get_user(user.id)
    if not ud or ud['balance'] < amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return
    code = _generate_code()
    await update_balance(user.id, -amount)
    game = HackGame(chat.id, amount, user.id, code)
    game.players[user.id] = {'name': user.first_name}
    game.guesses[user.id] = 0
    HACK_GAMES[chat.id] = game
    # Send code to starter
    try:
        await context.bot.send_message(
            user.id,
            f"💻 <b>Sᴇᴄʀᴇᴛ Hᴀᴄᴋ Cᴏᴅᴇ</b>\n\n"
            f"4-ᴅɪɢɪᴛ ᴄᴏᴅᴇ: <code>{code}</code>\n\n"
            f"Oᴛʜᴇʀs ᴡɪʟʟ ᴛʀʏ ᴛᴏ ɢᴜᴇss ɪᴛ!\n"
            f"🎯 = ʀɪɢʜᴛ ᴅɪɢɪᴛ ʀɪɢʜᴛ ᴘᴏs (Bᴜʟʟ)\n"
            f"🐮 = ʀɪɢʜᴛ ᴅɪɢɪᴛ ᴡʀᴏɴɢ ᴘᴏs (Cᴏᴡ)",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await update.message.reply_text(
        f"💻 <b>Bᴀᴋᴀ Hᴀᴄᴋ Gᴀᴍᴇ</b> Sᴛᴀʀᴛᴇᴅ!\n\n"
        f"💰 Eɴᴛʀʏ Fᴇᴇ: <b>${amount}</b>\n"
        f"⏳ Jᴏɪɴ ɪɴ 60s: /register\n\n"
        f"🔐 A sᴇᴄʀᴇᴛ 4-ᴅɪɢɪᴛ ᴄᴏᴅᴇ ɪs sᴇᴛ!\n"
        f"Uꜱᴇ /guess &lt;4-ᴅɪɢɪᴛs&gt; ᴛᴏ ᴄʀᴀᴄᴋ ɪᴛ!\n\n"
        f"🎯 Bull = ʀɪɢʜᴛ ᴅɪɢɪᴛ ʀɪɢʜᴛ ᴘᴏs\n"
        f"🐮 Cᴏᴡ = ʀɪɢʜᴛ ᴅɪɢɪᴛ ᴡʀᴏɴɢ ᴘᴏs",
        parse_mode="HTML"
    )
    game.task = asyncio.create_task(_hack_join_timer(chat.id, context))


async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /register — join hack game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in HACK_GAMES:
        await update.message.reply_text("❌ No hack game active. Start with /hack <amount>")
        return
    game = HACK_GAMES[chat.id]
    if game.started:
        await update.message.reply_text("❌ Game already started! Use /guess to play.")
        return
    if user.id in game.players:
        await update.message.reply_text("✅ You're already registered!")
        return
    await ensure_user(user.id, user.first_name, user.username)
    ud = await get_user(user.id)
    if not ud or ud['balance'] < game.amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return
    await update_balance(user.id, -game.amount)
    game.players[user.id] = {'name': user.first_name}
    game.guesses[user.id] = 0
    await update.message.reply_text(
        f"✅ <b>{user.first_name}</b> ʀᴇɢɪsᴛᴇʀᴇᴅ!\n👥 Players: {len(game.players)}",
        parse_mode="HTML"
    )


async def _hack_join_timer(chat_id, context):
    await asyncio.sleep(JOIN_WINDOW)
    if chat_id not in HACK_GAMES:
        return
    game = HACK_GAMES[chat_id]
    if len(game.players) < 2:
        for uid in game.players:
            await update_balance(uid, game.amount)
        await context.bot.send_message(chat_id, "❌ Not enough players (min 2). Fees refunded.")
        del HACK_GAMES[chat_id]
        return
    game.started = True
    pot = game.amount * len(game.players)
    await context.bot.send_message(
        chat_id,
        f"💻 <b>Hᴀᴄᴋ Gᴀᴍᴇ Sᴛᴀʀᴛᴇᴅ!</b>\n\n"
        f"💰 Pᴏᴛ: <b>${pot}</b>\n"
        f"👥 Players: {len(game.players)}\n\n"
        f"🔐 Cʀᴀᴄᴋ ᴛʜᴇ 4-ᴅɪɢɪᴛ ᴄᴏᴅᴇ!\n"
        f"Uꜱᴇ /guess &lt;4-ᴅɪɢɪᴛs&gt;\n"
        f"⏰ 5 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴄʀᴀᴄᴋ ɪᴛ!",
        parse_mode="HTML"
    )
    game.timeout_task = asyncio.create_task(_hack_timeout(chat_id, context))


async def _hack_timeout(chat_id, context):
    await asyncio.sleep(GAME_TIMEOUT)
    if chat_id not in HACK_GAMES:
        return
    game = HACK_GAMES[chat_id]
    if game.started:
        for uid in game.players:
            await update_balance(uid, game.amount)
        await context.bot.send_message(
            chat_id,
            f"⏰ <b>Tɪᴍᴇ Up!</b> Nᴏ ᴏɴᴇ ᴄʀᴀᴄᴋᴇᴅ ɪᴛ!\n"
            f"🔐 Tʜᴇ ᴄᴏᴅᴇ ᴡᴀs: <code>{game.code}</code>\n"
            f"💸 Fᴇᴇs ʀᴇꜰᴜɴᴅᴇᴅ.",
            parse_mode="HTML"
        )
        del HACK_GAMES[chat_id]


async def guess_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /guess — guess the code"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in HACK_GAMES:
        await update.message.reply_text("❌ No hack game active.")
        return
    game = HACK_GAMES[chat.id]
    if not game.started:
        await update.message.reply_text("⏳ Game hasn't started yet! Use /register first.")
        return
    if user.id not in game.players:
        await update.message.reply_text("❌ You're not registered in this game.")
        return
    if not context.args or not context.args[0].isdigit() or len(context.args[0]) != 4:
        await update.message.reply_text("❗ Usage: /guess <4-digit code>\nExample: /guess 1234")
        return
    guess = context.args[0]
    game.guesses[user.id] = game.guesses.get(user.id, 0) + 1

    if guess == game.code:
        if game.timeout_task:
            game.timeout_task.cancel()
        pot = game.amount * len(game.players)
        premium = await is_premium(user.id)
        tax_pct = 5 if premium else 10
        tax = int(pot * tax_pct / 100)
        reward = pot - tax
        await update_balance(user.id, reward)
        await update.message.reply_text(
            f"🎉 <b>{user.first_name} CRACKED THE CODE!</b>\n\n"
            f"🔐 Cᴏᴅᴇ: <code>{game.code}</code>\n"
            f"💰 Pᴏᴛ: ${pot} — Tᴀx: ${tax} ({tax_pct}%)\n"
            f"🤑 Rᴇᴡᴀʀᴅ: <b>${reward}</b>",
            parse_mode="HTML"
        )
        del HACK_GAMES[chat.id]
    else:
        bulls, cows = _bulls_cows(game.code, guess)
        await update.message.reply_text(
            f"💻 <b>{user.first_name}</b> ɢᴜᴇssᴇᴅ <code>{guess}</code>\n"
            f"🎯 Bulls: <b>{bulls}</b>  🐮 Cᴏᴡs: <b>{cows}</b>",
            parse_mode="HTML"
        )


async def end_hack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /end — cancel hack game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        return
    if chat.id not in HACK_GAMES:
        await update.message.reply_text("❌ No hack game active.")
        return
    game = HACK_GAMES[chat.id]
    from utils.permissions import is_owner, is_admin
    if user.id != game.starter_id and not is_owner(user.id) and not await is_admin(chat, user.id, context.bot):
        await update.message.reply_text("❌ Only the game starter or admins can end the game.")
        return
    if game.timeout_task:
        game.timeout_task.cancel()
    for uid in game.players:
        await update_balance(uid, game.amount)
    await update.message.reply_text(
        f"🛑 Hᴀᴄᴋ ɢᴀᴍᴇ ᴇɴᴅᴇᴅ!\n🔐 Cᴏᴅᴇ: <code>{game.code}</code>\n💸 Fᴇᴇs ʀᴇꜰᴜɴᴅᴇᴅ.",
        parse_mode="HTML"
    )
    del HACK_GAMES[chat.id]

import asyncio
import random
import time
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, update_balance, is_premium
from utils.permissions import GROUP_ONLY_MSG

BLUFF_GAMES = {}  # chat_id -> BluffGame
JOIN_WINDOW = 90


class BluffGame:
    def __init__(self, chat_id, amount, starter_id):
        self.chat_id = chat_id
        self.amount = amount
        self.starter_id = starter_id
        self.players = {}     # uid -> {name, card, lives}
        self.player_order = []
        self.current_turn = 0
        self.last_drop = None  # (uid, claimed_val, actual_val)
        self.started = False
        self.task = None
        self.turn_task = None


async def bluff_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bluff — start bluff game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id in BLUFF_GAMES:
        await update.message.reply_text("🎭 A bluff game is already active!")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /bluff <amount>")
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
    await update_balance(user.id, -amount)
    game = BluffGame(chat.id, amount, user.id)
    game.players[user.id] = {'name': user.first_name, 'card': 0, 'lives': 3}
    BLUFF_GAMES[chat.id] = game
    await update.message.reply_text(
        f"🎭 <b>Bᴀᴋᴀ Bʟᴜꜰꜰ Gᴀᴍᴇ</b> Sᴛᴀʀᴛᴇᴅ!\n\n"
        f"💰 Bᴇᴛ: <b>${amount}</b>\n"
        f"⏳ Jᴏɪɴ ɪɴ 90s ᴜsɪɴɢ /enter\n\n"
        f"📖 <b>Rᴜʟᴇs:</b>\n"
        f"• Eᴀᴄʜ ᴘʟᴀʏᴇʀ ɢᴇᴛs ᴀ ʜɪᴅᴅᴇɴ ᴄᴀʀᴅ (1-10)\n"
        f"• /drop &lt;ᴠᴀʟᴜᴇ&gt; — ᴘʟᴀʏ ʏᴏᴜʀ ᴄᴀʀᴅ (ᴄᴀɴ ʟɪᴇ!)\n"
        f"• /judge — ᴄᴀʟʟ ᴛʜᴇ ʟᴀsᴛ ᴘʟᴀʏᴇʀ's ʙʟᴜꜰꜰ\n"
        f"• 3 ʟɪᴠᴇs ᴇᴀᴄʜ — ʟᴀsᴛ sᴛᴀɴᴅɪɴɢ ᴡɪɴs! 🏆",
        parse_mode="HTML"
    )
    game.task = asyncio.create_task(_bluff_join_timer(chat.id, context))


async def bluff_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Called by enter_router when bluff game is active. Returns True if handled."""
    chat = update.effective_chat
    user = update.effective_user
    if chat.id not in BLUFF_GAMES:
        return False
    game = BLUFF_GAMES[chat.id]
    if game.started:
        await update.message.reply_text("❌ Bluff game already started!")
        return True
    if user.id in game.players:
        await update.message.reply_text("✅ You're already in the bluff game!")
        return True
    await ensure_user(user.id, user.first_name, user.username)
    ud = await get_user(user.id)
    if not ud or ud['balance'] < game.amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return True
    await update_balance(user.id, -game.amount)
    game.players[user.id] = {'name': user.first_name, 'card': 0, 'lives': 3}
    await update.message.reply_text(
        f"✅ <b>{user.first_name}</b> joined the bluff game!\n👥 Players: {len(game.players)}",
        parse_mode="HTML"
    )
    return True


async def _bluff_join_timer(chat_id, context):
    await asyncio.sleep(JOIN_WINDOW)
    if chat_id not in BLUFF_GAMES:
        return
    game = BLUFF_GAMES[chat_id]
    if len(game.players) < 2:
        for uid in game.players:
            await update_balance(uid, game.amount)
        await context.bot.send_message(chat_id, "❌ Not enough players (min 2). Fees refunded.")
        del BLUFF_GAMES[chat_id]
        return
    await _start_bluff_game(chat_id, context)


async def _start_bluff_game(chat_id, context):
    game = BLUFF_GAMES[chat_id]
    game.started = True
    game.player_order = list(game.players.keys())
    random.shuffle(game.player_order)
    for uid in game.players:
        game.players[uid]['card'] = random.randint(1, 10)
    # DM cards
    for uid, pdata in game.players.items():
        try:
            await context.bot.send_message(
                uid,
                f"🎭 <b>Yᴏᴜʀ Bʟᴜꜰꜰ Cᴀʀᴅ</b>\n\n"
                f"Yᴏᴜʀ ᴄᴀʀᴅ ᴠᴀʟᴜᴇ: <b>{pdata['card']}</b>\n\n"
                f"Yᴏᴜ ᴄᴀɴ ʟɪᴇ ᴡʜᴇɴ ʏᴏᴜ /drop! Gᴏᴏᴅ ʟᴜᴄᴋ 😏",
                parse_mode="HTML"
            )
        except Exception:
            pass
    order_text = "\n".join(f"{i+1}. {game.players[uid]['name']}" for i, uid in enumerate(game.player_order))
    await context.bot.send_message(
        chat_id,
        f"🎭 <b>Bʟᴜꜰꜰ Gᴀᴍᴇ Sᴛᴀʀᴛᴇᴅ!</b>\n\n"
        f"💰 Pᴏᴛ: <b>${game.amount * len(game.players)}</b>\n"
        f"📩 Cᴀʀᴅs sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ DM!\n\n"
        f"🔄 Tᴜʀɴ Oʀᴅᴇʀ:\n{order_text}",
        parse_mode="HTML"
    )
    await asyncio.sleep(3)
    await _bluff_next_turn(chat_id, context)


async def _bluff_next_turn(chat_id, context):
    if chat_id not in BLUFF_GAMES:
        return
    game = BLUFF_GAMES[chat_id]
    alive = [uid for uid, p in game.players.items() if p['lives'] > 0]
    if len(alive) <= 1:
        await _bluff_end(chat_id, context)
        return
    # Find current alive player
    attempts = 0
    while attempts < len(game.player_order):
        uid = game.player_order[game.current_turn % len(game.player_order)]
        if game.players[uid]['lives'] > 0:
            break
        game.current_turn += 1
        attempts += 1
    else:
        await _bluff_end(chat_id, context)
        return

    pdata = game.players[uid]
    lives_str = "❤️" * pdata['lives'] + "🖤" * (3 - pdata['lives'])
    turn_mark = game.current_turn

    if game.last_drop:
        prev_uid, claimed, _ = game.last_drop
        prev_name = game.players[prev_uid]['name']
        msg = (
            f"🎭 <b>{pdata['name']}'s Turn</b> {lives_str}\n\n"
            f"📢 {prev_name} ᴄʟᴀɪᴍᴇᴅ: <b>{claimed}</b>\n\n"
            f"⏰ 45s ᴛᴏ:\n"
            f"• /drop &lt;ᴠᴀʟᴜᴇ&gt; — ᴘʟᴀʏ ʏᴏᴜʀ ᴄᴀʀᴅ\n"
            f"• /judge — ᴄᴀʟʟ ᴛʜᴇɪʀ ʙʟᴜꜰꜰ!"
        )
    else:
        msg = (
            f"🎭 <b>{pdata['name']}'s Turn</b> {lives_str}\n\n"
            f"⏰ 45s ᴛᴏ:\n"
            f"• /drop &lt;ᴠᴀʟᴜᴇ&gt; — ᴘʟᴀʏ ʏᴏᴜʀ ᴄᴀʀᴅ (ᴄᴀɴ ʟɪᴇ!)"
        )
    await context.bot.send_message(chat_id, msg, parse_mode="HTML")

    async def auto_drop():
        await asyncio.sleep(45)
        if chat_id not in BLUFF_GAMES:
            return
        g = BLUFF_GAMES[chat_id]
        curr_uid = g.player_order[g.current_turn % len(g.player_order)]
        if g.current_turn != turn_mark or curr_uid != uid:
            return
        # Auto-drop a random claimed value
        actual = g.players[uid]['card']
        claimed = random.randint(1, 10)
        g.last_drop = (uid, claimed, actual)
        g.current_turn += 1
        g.players[uid]['card'] = random.randint(1, 10)
        try:
            await context.bot.send_message(
                chat_id,
                f"⏰ <b>{pdata['name']}</b> ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ! Aᴜᴛᴏ-ᴅʀᴏᴘᴘᴇᴅ <b>{claimed}</b>.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await _bluff_next_turn(chat_id, context)

    if game.turn_task:
        game.turn_task.cancel()
    game.turn_task = asyncio.create_task(auto_drop())


async def drop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /drop — play card in bluff game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in BLUFF_GAMES:
        await update.message.reply_text("❌ No bluff game active. Start with /bluff <amount>")
        return
    game = BLUFF_GAMES[chat.id]
    if not game.started:
        await update.message.reply_text("⏳ Game hasn't started yet!")
        return
    if user.id not in game.players or game.players[user.id]['lives'] <= 0:
        await update.message.reply_text("❌ You're not in this game or already eliminated.")
        return
    curr_uid = game.player_order[game.current_turn % len(game.player_order)]
    if user.id != curr_uid:
        await update.message.reply_text(f"❌ Not your turn! Wait for {game.players[curr_uid]['name']}.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /drop <value 1-10>")
        return
    claimed = int(context.args[0])
    if not 1 <= claimed <= 10:
        await update.message.reply_text("❗ Value must be 1-10.")
        return
    actual = game.players[user.id]['card']
    game.last_drop = (user.id, claimed, actual)
    game.current_turn += 1
    game.players[user.id]['card'] = random.randint(1, 10)
    if game.turn_task:
        game.turn_task.cancel()
    await update.message.reply_text(
        f"📤 <b>{user.first_name}</b> ᴘʟᴀʏᴇᴅ ᴀ ᴄᴀʀᴅ ᴀɴᴅ ᴄʟᴀɪᴍᴇᴅ: <b>{claimed}</b>\n"
        f"💭 <i>Tʀᴜᴛʜ ᴏʀ ʙʟᴜꜰꜰ? Others can /judge!</i>",
        parse_mode="HTML"
    )
    await asyncio.sleep(2)
    await _bluff_next_turn(chat.id, context)


async def judge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /judge — call a bluff"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in BLUFF_GAMES:
        await update.message.reply_text("❌ No bluff game active.")
        return
    game = BLUFF_GAMES[chat.id]
    if not game.started:
        await update.message.reply_text("⏳ Game hasn't started yet!")
        return
    if user.id not in game.players or game.players[user.id]['lives'] <= 0:
        await update.message.reply_text("❌ You're not in this game or already eliminated.")
        return
    if game.last_drop is None:
        await update.message.reply_text("❌ No card played yet to judge!")
        return
    prev_uid, claimed, actual = game.last_drop
    if user.id == prev_uid:
        await update.message.reply_text("❌ You can't judge your own card!")
        return
    was_bluff = (claimed != actual)
    if was_bluff:
        game.players[prev_uid]['lives'] -= 1
        lives_left = game.players[prev_uid]['lives']
        loser_name = game.players[prev_uid]['name']
        result = (
            f"🔍 <b>BUSTED!</b> {loser_name} ᴡᴀs ʙʟᴜꜰꜰɪɴɢ!\n"
            f"Cʟᴀɪᴍᴇᴅ: <b>{claimed}</b> | Aᴄᴛᴜᴀʟ: <b>{actual}</b>\n\n"
            + (f"💀 <b>{loser_name}</b> ɪs ᴇʟɪᴍɪɴᴀᴛᴇᴅ!" if lives_left <= 0 else f"❤️ {loser_name} ʜᴀs {lives_left} ʟɪᴠᴇ(s) ʟᴇꜰᴛ!")
        )
    else:
        game.players[user.id]['lives'] -= 1
        lives_left = game.players[user.id]['lives']
        result = (
            f"🔍 <b>WRONG!</b> {game.players[prev_uid]['name']} ᴡᴀs ʜᴏɴᴇsᴛ!\n"
            f"Cʟᴀɪᴍᴇᴅ: <b>{claimed}</b> | Aᴄᴛᴜᴀʟ: <b>{actual}</b>\n\n"
            + (f"💀 <b>{user.first_name}</b> ɪs ᴇʟɪᴍɪɴᴀᴛᴇᴅ!" if lives_left <= 0 else f"❤️ {user.first_name} ʜᴀs {lives_left} ʟɪᴠᴇ(s) ʟᴇꜰᴛ!")
        )
    game.last_drop = None
    if game.turn_task:
        game.turn_task.cancel()
    await update.message.reply_text(result, parse_mode="HTML")
    await asyncio.sleep(2)
    await _bluff_next_turn(chat.id, context)


async def _bluff_end(chat_id, context):
    if chat_id not in BLUFF_GAMES:
        return
    game = BLUFF_GAMES[chat_id]
    alive = [uid for uid, p in game.players.items() if p['lives'] > 0]
    pot = game.amount * len(game.players)
    if alive:
        winner_id = alive[0]
        winner = game.players[winner_id]
        premium = await is_premium(winner_id)
        tax_pct = 5 if premium else 10
        tax = int(pot * tax_pct / 100)
        reward = pot - tax
        await update_balance(winner_id, reward)
        await context.bot.send_message(
            chat_id,
            f"🏆 <b>Bʟᴜꜰꜰ Gᴀᴍᴇ Oᴠᴇʀ!</b>\n\n"
            f"🎭 Wɪɴɴᴇʀ: <b>{winner['name']}</b>\n"
            f"💰 Pᴏᴛ: ${pot} — Tᴀx: ${tax} ({tax_pct}%)\n"
            f"🤑 Rᴇᴡᴀʀᴅ: <b>${reward}</b>",
            parse_mode="HTML"
        )
    else:
        for uid in game.players:
            await update_balance(uid, game.amount)
        await context.bot.send_message(chat_id, "🤝 Dʀᴀᴡ! Fᴇᴇs ʀᴇꜰᴜɴᴅᴇᴅ.")
    del BLUFF_GAMES[chat_id]

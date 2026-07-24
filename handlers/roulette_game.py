import asyncio
import random
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, update_balance, is_premium
from utils.permissions import GROUP_ONLY_MSG

ROULETTE_GAMES = {}  # chat_id -> RouletteGame
JOIN_WINDOW = 120
BID_WINDOW = 30


class RouletteGame:
    def __init__(self, chat_id, amount, starter_id):
        self.chat_id = chat_id
        self.amount = amount
        self.starter_id = starter_id
        self.players = {}          # uid -> {name, eliminated}
        self.bids = {}             # uid -> bid amount (current round)
        self.round = 0
        self.started = False
        self.collecting_bids = False
        self.task = None


async def roulette_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /roulette — start roulette game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id in ROULETTE_GAMES:
        await update.message.reply_text("🎰 A roulette game is already active!")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /roulette <amount>\nExample: /roulette 500")
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
    game = RouletteGame(chat.id, amount, user.id)
    game.players[user.id] = {'name': user.first_name, 'eliminated': False}
    ROULETTE_GAMES[chat.id] = game
    await update.message.reply_text(
        f"🎰 <b>Bᴀᴋᴀ Rᴏᴜʟᴇᴛᴛᴇ</b> Sᴛᴀʀᴛᴇᴅ!\n\n"
        f"💰 Eɴᴛʀʏ Fᴇᴇ: <b>${amount}</b>\n"
        f"⏳ 2 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴊᴏɪɴ\n\n"
        f"👉 /join {amount} ᴛᴏ ᴇɴᴛᴇʀ!\n\n"
        f"📖 <b>Rᴜʟᴇs:</b>\n"
        f"• Eᴀᴄʜ ʀᴏᴜɴᴅ: /bid &lt;ᴀᴍᴏᴜɴᴛ&gt; ᴡɪᴛʜɪɴ 30s\n"
        f"• Pʟᴀʏᴇʀ ᴡɪᴛʜ <b>ʟᴏᴡᴇsᴛ ʙɪᴅ</b> ɪs ᴇʟɪᴍɪɴᴀᴛᴇᴅ\n"
        f"• Lᴀsᴛ ᴘʟᴀʏᴇʀ sᴛᴀɴᴅɪɴɢ ᴡɪɴs! 🏆",
        parse_mode="HTML"
    )
    game.task = asyncio.create_task(_roulette_join_timer(chat.id, context))


async def roulette_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Called by join_router when roulette game is active. Returns True if handled."""
    chat = update.effective_chat
    user = update.effective_user
    if chat.id not in ROULETTE_GAMES:
        return False
    game = ROULETTE_GAMES[chat.id]
    if game.started:
        await update.message.reply_text("❌ Roulette already started!")
        return True
    if user.id in game.players:
        await update.message.reply_text("✅ You're already in the roulette!")
        return True
    # Check amount from args
    if context.args and context.args[0].isdigit():
        amount = int(context.args[0])
        if amount != game.amount:
            await update.message.reply_text(f"❌ Entry fee is ${game.amount}. Use /join {game.amount}")
            return True
    await ensure_user(user.id, user.first_name, user.username)
    ud = await get_user(user.id)
    if not ud or ud['balance'] < game.amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return True
    await update_balance(user.id, -game.amount)
    game.players[user.id] = {'name': user.first_name, 'eliminated': False}
    await update.message.reply_text(
        f"✅ <b>{user.first_name}</b> ᴊᴏɪɴᴇᴅ Rᴏᴜʟᴇᴛᴛᴇ!\n👥 Players: {len(game.players)}",
        parse_mode="HTML"
    )
    return True


async def _roulette_join_timer(chat_id, context):
    await asyncio.sleep(JOIN_WINDOW - 30)
    if chat_id not in ROULETTE_GAMES:
        return
    game = ROULETTE_GAMES[chat_id]
    if not game.started:
        await context.bot.send_message(chat_id, f"⏳ 30s left! /join {game.amount} for Roulette!")
    await asyncio.sleep(30)
    if chat_id not in ROULETTE_GAMES:
        return
    game = ROULETTE_GAMES[chat_id]
    if len(game.players) < 2:
        for uid in game.players:
            await update_balance(uid, game.amount)
        await context.bot.send_message(chat_id, "❌ Not enough players (min 2). Fees refunded.")
        del ROULETTE_GAMES[chat_id]
        return
    await _start_roulette(chat_id, context)


async def _start_roulette(chat_id, context):
    game = ROULETTE_GAMES[chat_id]
    game.started = True
    pot = game.amount * len(game.players)
    total_rounds = len(game.players) - 1
    await context.bot.send_message(
        chat_id,
        f"🎰 <b>Rᴏᴜʟᴇᴛᴛᴇ Bᴇɢɪɴs!</b>\n\n"
        f"💰 Pᴏᴛ: <b>${pot}</b>\n"
        f"👥 Players: {len(game.players)}\n"
        f"🔄 Rᴏᴜɴᴅs: {total_rounds}\n\n"
        f"⚡ Eᴀᴄʜ ʀᴏᴜɴᴅ: /bid &lt;ᴀᴍᴏᴜɴᴛ&gt; — ʟᴏᴡᴇsᴛ ʙɪᴅ ɪs ᴇʟɪᴍɪɴᴀᴛᴇᴅ!",
        parse_mode="HTML"
    )
    await asyncio.sleep(3)
    for round_num in range(1, total_rounds + 1):
        if chat_id not in ROULETTE_GAMES:
            return
        game = ROULETTE_GAMES[chat_id]
        game.round = round_num
        game.bids = {}
        game.collecting_bids = True
        alive = [uid for uid, p in game.players.items() if not p['eliminated']]
        if len(alive) <= 1:
            break
        player_list = " | ".join(game.players[uid]['name'] for uid in alive)
        await context.bot.send_message(
            chat_id,
            f"🎯 <b>Rᴏᴜɴᴅ {round_num}/{total_rounds}</b>\n\n"
            f"👥 Aʟɪᴠᴇ: {player_list}\n\n"
            f"⏰ 30s — /bid &lt;ᴀᴍᴏᴜɴᴛ&gt;\n"
            f"💡 Bɪᴅ ʜɪɢʜᴇʀ ᴛʜᴀɴ ᴛʜᴇ ʟᴏᴡᴇsᴛ ᴛᴏ sᴜʀᴠɪᴠᴇ!",
            parse_mode="HTML"
        )
        await asyncio.sleep(BID_WINDOW)
        if chat_id not in ROULETTE_GAMES:
            return
        game = ROULETTE_GAMES[chat_id]
        game.collecting_bids = False
        # Auto-bid 0 for no-shows
        for uid in alive:
            if uid not in game.bids:
                game.bids[uid] = 0
        min_bid = min(game.bids.values())
        losers = [uid for uid, b in game.bids.items() if b == min_bid]
        loser_id = random.choice(losers)
        game.players[loser_id]['eliminated'] = True
        bid_lines = sorted(game.bids.items(), key=lambda x: x[1], reverse=True)
        bid_text = "\n".join(
            f"{'💀' if uid == loser_id else '✅'} {game.players[uid]['name']}: ${b}"
            for uid, b in bid_lines
        )
        await context.bot.send_message(
            chat_id,
            f"🎰 <b>Rᴏᴜɴᴅ {round_num} Rᴇsᴜʟᴛ</b>\n\n{bid_text}\n\n"
            f"💀 Eʟɪᴍɪɴᴀᴛᴇᴅ: <b>{game.players[loser_id]['name']}</b> (ʟᴏᴡᴇsᴛ ʙɪᴅ: ${min_bid})",
            parse_mode="HTML"
        )
        await asyncio.sleep(3)
    await _roulette_end(chat_id, context)


async def bid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bid — place a bid in roulette"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in ROULETTE_GAMES:
        await update.message.reply_text("❌ No roulette game active.")
        return
    game = ROULETTE_GAMES[chat.id]
    if not game.started or not game.collecting_bids:
        await update.message.reply_text("⏳ No active bidding round right now.")
        return
    if user.id not in game.players or game.players[user.id]['eliminated']:
        await update.message.reply_text("❌ You're not in this game or already eliminated.")
        return
    if user.id in game.bids:
        await update.message.reply_text("✅ You already placed your bid this round!")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /bid <amount>")
        return
    bid = int(context.args[0])
    ud = await get_user(user.id)
    if not ud or ud['balance'] < bid:
        await update.message.reply_text("❌ Insufficient balance for this bid.")
        return
    game.bids[user.id] = bid
    await update.message.reply_text(
        f"✅ <b>{user.first_name}</b> ᴘʟᴀᴄᴇᴅ ʙɪᴅ: <b>${bid}</b> 🎰",
        parse_mode="HTML"
    )


async def _roulette_end(chat_id, context):
    if chat_id not in ROULETTE_GAMES:
        return
    game = ROULETTE_GAMES[chat_id]
    alive = [uid for uid, p in game.players.items() if not p['eliminated']]
    pot = game.amount * len(game.players)
    if alive:
        winner_id = alive[0] if len(alive) == 1 else random.choice(alive)
        winner = game.players[winner_id]
        premium = await is_premium(winner_id)
        tax_pct = 5 if premium else 10
        tax = int(pot * tax_pct / 100)
        reward = pot - tax
        await update_balance(winner_id, reward)
        await context.bot.send_message(
            chat_id,
            f"🎰 <b>Rᴏᴜʟᴇᴛᴛᴇ Oᴠᴇʀ!</b>\n\n"
            f"🏆 Wɪɴɴᴇʀ: <b>{winner['name']}</b>\n"
            f"💰 Pᴏᴛ: ${pot} — Tᴀx: ${tax} ({tax_pct}%)\n"
            f"🤑 Rᴇᴡᴀʀᴅ: <b>${reward}</b>",
            parse_mode="HTML"
        )
    del ROULETTE_GAMES[chat_id]

import asyncio
import random
import time
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, update_balance, is_premium
from utils.permissions import GROUP_ONLY_MSG

CARD_GAMES = {}  # chat_id -> CardGame
JOIN_WINDOW = 120
ROUND_TIMEOUT = 60
CARD_LABELS = ['A', 'B', 'C', 'D']


class CardGame:
    def __init__(self, chat_id, amount, starter_id):
        self.chat_id = chat_id
        self.amount = amount
        self.starter_id = starter_id
        self.players = {}  # uid -> {name, cards, flipped, score}
        self.current_round_flips = {}
        self.round = 0
        self.started = False
        self.task = None
        self.current_turn_mark = 0  # incremented each round for auto-play detection


def _generate_cards(num_players):
    """Each player gets 4 cards labeled A-D; all players share the same sum."""
    base = [random.randint(2, 8) for _ in range(4)]
    target = sum(base)
    all_cards = [dict(zip(CARD_LABELS, base))]
    for _ in range(num_players - 1):
        vals = [random.randint(1, 9) for _ in range(3)]
        fourth = target - sum(vals)
        fourth = max(1, min(10, fourth))
        # Adjust first element if needed
        if sum(vals) + fourth != target:
            vals[0] = target - sum(vals[1:]) - fourth
            vals[0] = max(1, min(10, vals[0]))
        combo = vals + [fourth]
        random.shuffle(combo)
        all_cards.append(dict(zip(CARD_LABELS, combo)))
    return all_cards, target


async def card_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /card — start a card game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id in CARD_GAMES:
        g = CARD_GAMES[chat.id]
        msg = "🃏 Card game waiting for players! /bet to join." if not g.started else "🃏 Card game in progress!"
        await update.message.reply_text(msg)
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /card <amount>\nExample: /card 500")
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
    game = CardGame(chat.id, amount, user.id)
    game.players[user.id] = {'name': user.first_name, 'cards': {}, 'flipped': [], 'score': 0}
    CARD_GAMES[chat.id] = game
    await update.message.reply_text(
        f"🃏 <b>Bᴀᴋᴀ Cᴀʀᴅ Gᴀᴍᴇ</b> Sᴛᴀʀᴛᴇᴅ!\n\n"
        f"💰 Eɴᴛʀʏ Fᴇᴇ: <b>${amount}</b>\n"
        f"⏳ 2 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴊᴏɪɴ\n\n"
        f"👉 /bet {amount} ᴛᴏ ᴊᴏɪɴ!\n"
        f"📌 Mɪɴ 2 ᴘʟᴀʏᴇʀs ɴᴇᴇᴅᴇᴅ.",
        parse_mode="HTML"
    )
    game.task = asyncio.create_task(_card_join_timer(chat.id, context))


async def bet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bet — join a card game"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in CARD_GAMES:
        await update.message.reply_text("❌ No card game active. Start with /card <amount>")
        return
    game = CARD_GAMES[chat.id]
    if game.started:
        await update.message.reply_text("❌ Game already started.")
        return
    if user.id in game.players:
        await update.message.reply_text("✅ You're already in!")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(f"❗ Usage: /bet {game.amount}")
        return
    amount = int(context.args[0])
    if amount != game.amount:
        await update.message.reply_text(f"❌ Entry fee is exactly ${game.amount}.")
        return
    await ensure_user(user.id, user.first_name, user.username)
    ud = await get_user(user.id)
    if not ud or ud['balance'] < amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return
    await update_balance(user.id, -amount)
    game.players[user.id] = {'name': user.first_name, 'cards': {}, 'flipped': [], 'score': 0}
    await update.message.reply_text(
        f"✅ <b>{user.first_name}</b> joined!\n👥 Players: {len(game.players)}",
        parse_mode="HTML"
    )


async def flip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /flip A/B/C/D"""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    if chat.id not in CARD_GAMES:
        await update.message.reply_text("❌ No card game active.")
        return
    game = CARD_GAMES[chat.id]
    if not game.started:
        await update.message.reply_text("⏳ Game hasn't started yet.")
        return
    if user.id not in game.players:
        await update.message.reply_text("❌ You're not in this game.")
        return
    if user.id in game.current_round_flips:
        await update.message.reply_text("✅ Already flipped this round!")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /flip A  or  /flip B  or  /flip C  or  /flip D")
        return
    label = context.args[0].upper()
    if label not in CARD_LABELS:
        await update.message.reply_text("❗ Choose A, B, C, or D")
        return
    pdata = game.players[user.id]
    if label in pdata['flipped']:
        await update.message.reply_text(f"❌ Card {label} already used! Choose another.")
        return
    pdata['flipped'].append(label)
    game.current_round_flips[user.id] = label
    await update.message.reply_text(
        f"✅ <b>{user.first_name}</b> flipped card <b>{label}</b> 🔒",
        parse_mode="HTML"
    )


async def _card_join_timer(chat_id, context):
    await asyncio.sleep(JOIN_WINDOW - 30)
    if chat_id not in CARD_GAMES:
        return
    game = CARD_GAMES[chat_id]
    if not game.started:
        await context.bot.send_message(chat_id, f"⏳ 30s left! /bet {game.amount} to join card game!")
    await asyncio.sleep(30)
    if chat_id not in CARD_GAMES:
        return
    game = CARD_GAMES[chat_id]
    if len(game.players) < 2:
        for uid in game.players:
            await update_balance(uid, game.amount)
        await context.bot.send_message(chat_id, "❌ Not enough players (min 2). Fees refunded.")
        del CARD_GAMES[chat_id]
        return
    await _start_card_game(chat_id, context)


async def _start_card_game(chat_id, context):
    game = CARD_GAMES[chat_id]
    game.started = True
    player_ids = list(game.players.keys())
    all_cards, card_sum = _generate_cards(len(player_ids))
    for i, uid in enumerate(player_ids):
        game.players[uid]['cards'] = all_cards[i]

    # Notify in group
    await context.bot.send_message(
        chat_id,
        f"🃏 <b>Cᴀʀᴅs Dɪsᴛʀɪʙᴜᴛᴇᴅ!</b>\n\n"
        f"💰 Pᴏᴛ: <b>${game.amount * len(player_ids)}</b>\n"
        f"🎯 Cᴀʀᴅ Sᴜᴍ Fᴏʀ Aʟʟ: <b>{card_sum}</b>\n\n"
        f"📩 Cʜᴇᴄᴋ ʏᴏᴜʀ DM ꜰᴏʀ ᴄᴀʀᴅ ᴠᴀʟᴜᴇs!\n"
        f"🎮 Uꜱᴇ /flip A/B/C/D ᴛᴏ ᴘʟᴀʏ!",
        parse_mode="HTML"
    )
    # DM cards to each player
    for uid, pdata in game.players.items():
        card_str = " | ".join(f"{k}: {v}" for k, v in pdata['cards'].items())
        try:
            await context.bot.send_message(
                uid,
                f"🃏 <b>Yᴏᴜʀ Sᴇᴄʀᴇᴛ Cᴀʀᴅs</b>\n\n"
                f"<code>{card_str}</code>\n\n"
                f"Uꜱᴇ /flip A, /flip B, /flip C, ᴏʀ /flip D ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ!",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await asyncio.sleep(3)
    await _run_card_rounds(chat_id, context)


async def _run_card_rounds(chat_id, context):
    for round_num in range(1, 5):
        if chat_id not in CARD_GAMES:
            return
        game = CARD_GAMES[chat_id]
        game.round = round_num
        game.current_round_flips = {}
        mark = round_num
        game.current_turn_mark = mark

        scoreboard = "\n".join(f"• {p['name']}: {p['score']} ᴘᴛs" for p in game.players.values())
        await context.bot.send_message(
            chat_id,
            f"🎯 <b>Rᴏᴜɴᴅ {round_num}/4</b>\n\n{scoreboard}\n\n"
            f"⏰ 60s — /flip A/B/C/D ᴛᴏ ᴘʟᴀʏ!",
            parse_mode="HTML"
        )
        deadline = time.time() + ROUND_TIMEOUT
        while time.time() < deadline:
            if chat_id not in CARD_GAMES:
                return
            if all(uid in CARD_GAMES[chat_id].current_round_flips for uid in CARD_GAMES[chat_id].players):
                break
            await asyncio.sleep(2)

        if chat_id not in CARD_GAMES:
            return
        game = CARD_GAMES[chat_id]
        # Auto-flip for slow players
        for uid, pdata in game.players.items():
            if uid not in game.current_round_flips:
                available = [k for k in CARD_LABELS if k not in pdata['flipped']]
                if available:
                    chosen = random.choice(available)
                    pdata['flipped'].append(chosen)
                    game.current_round_flips[uid] = chosen

        # Determine round winner
        round_vals = {uid: game.players[uid]['cards'].get(lbl, 0)
                      for uid, lbl in game.current_round_flips.items()}
        if round_vals:
            max_val = max(round_vals.values())
            round_winners = [uid for uid, v in round_vals.items() if v == max_val]
            for uid in round_winners:
                game.players[uid]['score'] += 1

            lines = [
                f"• {game.players[uid]['name']}: Card <b>{lbl}</b> = {game.players[uid]['cards'].get(lbl, '?')}"
                for uid, lbl in game.current_round_flips.items()
            ]
            winner_names = " & ".join(game.players[uid]['name'] for uid in round_winners)
            await context.bot.send_message(
                chat_id,
                f"🃏 <b>Rᴏᴜɴᴅ {round_num} Rᴇsᴜʟᴛ</b>\n\n" + "\n".join(lines) +
                f"\n\n🏆 Rᴏᴜɴᴅ Wɪɴɴᴇʀ: <b>{winner_names}</b> (+1 ᴘᴛ)",
                parse_mode="HTML"
            )
        await asyncio.sleep(3)

    await _card_game_end(chat_id, context)


async def _card_game_end(chat_id, context):
    if chat_id not in CARD_GAMES:
        return
    game = CARD_GAMES[chat_id]
    pot = game.amount * len(game.players)
    max_score = max(p['score'] for p in game.players.values())
    winners = [uid for uid, p in game.players.items() if p['score'] == max_score]
    winner_id = random.choice(winners)
    winner = game.players[winner_id]

    premium = await is_premium(winner_id)
    tax_pct = 5 if premium else 10
    tax = int(pot * tax_pct / 100)
    reward = pot - tax
    await update_balance(winner_id, reward)

    scores = sorted(game.players.items(), key=lambda x: x[1]['score'], reverse=True)
    board = "\n".join(
        f"{'🥇' if uid == winner_id else '▪️'} {p['name']}: {p['score']} ᴘᴛs"
        for uid, p in scores
    )
    await context.bot.send_message(
        chat_id,
        f"🏆 <b>Gᴀᴍᴇ Oᴠᴇʀ!</b>\n\n{board}\n\n"
        f"🎉 Wɪɴɴᴇʀ: <b>{winner['name']}</b>\n"
        f"💰 Pᴏᴛ: ${pot} — Tᴀx: ${tax} ({tax_pct}%)\n"
        f"🤑 Rᴇᴡᴀʀᴅ: <b>${reward}</b>",
        parse_mode="HTML"
    )
    del CARD_GAMES[chat_id]

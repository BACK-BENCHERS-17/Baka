import asyncio
import random
import time
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    ensure_user, get_user, update_balance, update_bomb_stats,
    get_bomb_stats, get_top_bomb, get_bomb_rank
)
from config import BOMB_JOIN_WINDOW, BOMB_BLAST_RANGE, OWNER_IDS

# In-memory game states
BOMB_GAMES = {}

class BombGame:
    """Bomb game instance"""
    
    def __init__(self, chat_id, entry_fee, starter_id):
        self.chat_id = chat_id
        self.entry_fee = entry_fee
        self.starter_id = starter_id
        self.players = {}  # user_id -> user_object
        self.alive = []  # user_ids still in game
        self.current_holder = None
        self.started = False
        self.join_end_time = 0
        self.task = None
    
    def add_player(self, user):
        """Add player to game"""
        if user.id not in self.players:
            self.players[user.id] = user
            self.alive.append(user.id)
            return True
        return False
    
    def remove_player(self, user_id):
        """Remove player from game"""
        if user_id in self.players:
            del self.players[user_id]
            if user_id in self.alive:
                self.alive.remove(user_id)
            if self.current_holder == user_id:
                self.current_holder = None
    
    def get_random_alive_except(self, except_id):
        """Get random alive player except given ID"""
        available = [uid for uid in self.alive if uid != except_id]
        return random.choice(available) if available else None

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bomb command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        return
    
    # Check if game already running
    if chat.id in BOMB_GAMES:
        await update.message.reply_text("💣 Bomb game already started ⛔")
        return
    
    # Check amount
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /bomb <amount>")
        return
    
    amount = int(context.args[0])
    if amount < 10:
        await update.message.reply_text("❌ Minimum entry fee is $10")
        return
    
    # Check starter's balance
    user = update.effective_user
    await ensure_user(user.id, user.first_name, user.username)
    user_data = await get_user(user.id)
    
    if not user_data or user_data['balance'] < amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return
    
    # Create game
    game = BombGame(chat.id, amount, user.id)
    BOMB_GAMES[chat.id] = game
    
    await update.message.reply_text(
        f"💣 Bomb Game Started\n"
        f"Entry Fee: ${amount}\n"
        f"Join using: /join {amount}"
    )
    
    # Start join window
    game.join_end_time = time.time() + BOMB_JOIN_WINDOW
    game.task = asyncio.create_task(_bomb_join_timer(chat.id, context))

async def _bomb_join_timer(chat_id, context):
    """Handle bomb game join timer"""
    await asyncio.sleep(BOMB_JOIN_WINDOW - 30)  # 90 seconds left
    
    if chat_id not in BOMB_GAMES:
        return
    
    game = BOMB_GAMES[chat_id]
    await context.bot.send_message(chat_id, "⏳ 30 seconds left! /join fast 💣")
    
    await asyncio.sleep(30)
    
    if chat_id not in BOMB_GAMES:
        return
    
    game = BOMB_GAMES[chat_id]
    
    # Check player count
    if len(game.players) < 2:
        # Refund all players
        for user_id in game.players:
            await update_balance(user_id, game.entry_fee)
        
        await context.bot.send_message(
            chat_id,
            "❌ At least 2 players are required. Entry fees have been refunded."
        )
        del BOMB_GAMES[chat_id]
        return
    
    # Start game
    game.started = True
    game.current_holder = random.choice(game.alive)
    
    await context.bot.send_message(
        chat_id,
        f"🎯 Round 1/1 started!\n"
        f"💣 Bomb is with {game.players[game.current_holder].first_name}\n"
        f"Use /pass fast!"
    )
    
    # Start explosion timer
    explosion_time = random.randint(*BOMB_BLAST_RANGE)
    game.task = asyncio.create_task(_bomb_explosion_timer(chat_id, context, explosion_time))

async def _bomb_explosion_timer(chat_id, context, wait_time):
    """Handle bomb explosion"""
    await asyncio.sleep(wait_time)
    
    if chat_id not in BOMB_GAMES:
        return
    
    game = BOMB_GAMES[chat_id]
    
    if not game.current_holder or game.current_holder not in game.players:
        # End game
        del BOMB_GAMES[chat_id]
        return
    
    loser = game.players[game.current_holder]
    await context.bot.send_message(chat_id, f"💥 BOOM! {loser.first_name} is OUT 🤯")
    
    # Remove loser
    game.remove_player(game.current_holder)
    
    # Check if game over
    if len(game.alive) == 1:
        await _end_bomb_game(chat_id, context)
        return
    
    # Continue with next round
    game.current_holder = random.choice(game.alive)
    await context.bot.send_message(
        chat_id,
        f"💣 Bomb is with {game.players[game.current_holder].first_name}\nUse /pass!"
    )
    
    # Schedule next explosion
    explosion_time = random.randint(*BOMB_BLAST_RANGE)
    game.task = asyncio.create_task(_bomb_explosion_timer(chat_id, context, explosion_time))

async def _end_bomb_game(chat_id, context):
    """End bomb game and distribute rewards"""
    if chat_id not in BOMB_GAMES:
        return
    
    game = BOMB_GAMES[chat_id]
    
    if len(game.alive) != 1:
        return
    
    winner_id = game.alive[0]
    winner = game.players[winner_id]
    
    # Calculate reward
    total_pool = game.entry_fee * len(game.players)
    reward = int(total_pool * 0.9)  # 90% to winner
    
    # Update balances and stats
    await update_balance(winner_id, reward)
    await update_bomb_stats(winner_id, reward)
    
    # Try to send winner's profile photo
    try:
        photos = await context.bot.get_user_profile_photos(winner_id, limit=1)
        if photos.total_count > 0:
            photo = photos.photos[0][-1]
            await context.bot.send_photo(chat_id, photo.file_id)
    except Exception:
        pass
    
    await context.bot.send_message(
        chat_id,
        f"🏆 Winner: {winner.first_name}\n💰 Won ${reward}"
    )
    
    # Cleanup
    del BOMB_GAMES[chat_id]

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /join command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        return
    
    # Check if game exists
    if chat.id not in BOMB_GAMES:
        await update.message.reply_text("❌ No bomb game is running.")
        return
    
    game = BOMB_GAMES[chat.id]
    
    # Check if game started
    if game.started:
        await update.message.reply_text("⛔ Game already started.")
        return
    
    # Check amount
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /join <amount>")
        return
    
    amount = int(context.args[0])
    if amount != game.entry_fee:
        await update.message.reply_text("❌ Wrong entry amount.")
        return
    
    user = update.effective_user
    
    # Check if already joined
    if user.id in game.players:
        return
    
    # Check if bot or owner
    if user.is_bot or user.id in OWNER_IDS:
        return
    
    # Check balance
    await ensure_user(user.id, user.first_name, user.username)
    user_data = await get_user(user.id)
    
    if not user_data or user_data['balance'] < amount:
        await update.message.reply_text("❌ Insufficient balance.")
        return
    
    # Deduct entry fee
    await update_balance(user.id, -amount)
    
    # Add player
    game.add_player(user)
    
    await update.message.reply_text(f"{user.first_name} joined 💥 (${game.entry_fee})")

async def pass_bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pass command"""
    chat = update.effective_chat
    
    if chat.id not in BOMB_GAMES:
        return
    
    game = BOMB_GAMES[chat.id]
    user = update.effective_user
    
    if not game.started or game.current_holder != user.id:
        await update.message.reply_text("You don't have the bomb. 😐")
        return
    
    # Pass to random other player
    new_holder = game.get_random_alive_except(user.id)
    if not new_holder:
        return
    
    game.current_holder = new_holder
    await update.message.reply_text(
        f"🏃 Bomb passed to {game.players[new_holder].first_name} 💣"
    )

async def myrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myrank command (bomb game)"""
    user = update.effective_user
    
    # Get bomb stats
    stats = await get_bomb_stats(user.id)
    
    if not stats or stats['wins'] == 0:
        await update.message.reply_text(f"⚠️ {user.first_name} has not played bomb game yet.")
        return
    
    # Get rank
    rank, total = await get_bomb_rank(user.id)
    
    await update.message.reply_text(
        f"📊 Bomb Rank\n\n"
        f"👤 {user.first_name}\n"
        f"🏆 Wins: {stats['wins']}\n"
        f"💰 Total Won: ${stats['total_won']}\n"
        f"👤 Rank: {rank} out of {total}"
    )

async def leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaders command (bomb game)"""
    top_players = await get_top_bomb(10)
    
    if not top_players:
        await update.message.reply_text("⚠️ No bomb stats yet.")
        return
    
    text = "🏆 Bomb Game Leaders\n\n"
    
    for i, (user_id, first_name, username, total_won) in enumerate(top_players, 1):
        # Get mention
        if username:
            mention = f'<a href="https://t.me/{username}">{first_name or "User"}</a>'
        else:
            mention = f'<a href="tg://user?id={user_id}">{first_name or "User"}</a>'
        
        # Medal emojis
        if i == 1:
            icon = "🥇"
        elif i == 2:
            icon = "🥈"
        elif i == 3:
            icon = "🥉"
        else:
            icon = "👤"
        
        text += f"{icon} {mention} — 💰 ${total_won}\n"
    
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)
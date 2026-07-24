import asyncio
import random
import string
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import ensure_user, get_user, update_balance
from config import WORD_GAME_JOIN_WINDOW, WORD_LENGTH

# In-memory game states
WORD_GAMES = {}

class WordGame:
    """Word typing game instance"""
    
    def __init__(self, chat_id, entry_fee, starter_id):
        self.chat_id = chat_id
        self.entry_fee = entry_fee
        self.starter_id = starter_id
        self.players = {}  # user_id -> user_object
        self.word = self.generate_word()
        self.started = False
        self.join_end_time = 0
        self.task = None
        self.message_id = None
    
    def generate_word(self):
        """Generate random alphanumeric word"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(WORD_LENGTH))
    
    def add_player(self, user):
        """Add player to game"""
        if user.id not in self.players:
            self.players[user.id] = user
            return True
        return False

async def wordgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /wordgame command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check if game already running
    if chat.id in WORD_GAMES:
        await update.message.reply_text("🎮 A word game is already running.")
        return
    
    # Check amount
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /wordgame <amount>")
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
    game = WordGame(chat.id, amount, user.id)
    WORD_GAMES[chat.id] = game
    
    await update.message.reply_text(
        f"⌨️ Word Typing Game Started\n\n"
        f"💰 Entry Fee: ₹{amount}\n"
        f"👉 Join using: /enter {amount}\n"
        f"⏳ Join window: 2 minute"
    )
    
    # Start join window
    game.join_end_time = time.time() + WORD_GAME_JOIN_WINDOW
    game.task = asyncio.create_task(_wordgame_join_timer(chat.id, context))

async def _wordgame_join_timer(chat_id, context):
    """Handle word game join timer"""
    await asyncio.sleep(WORD_GAME_JOIN_WINDOW - 90)  # 90 seconds left
    
    if chat_id not in WORD_GAMES:
        return
    
    game = WORD_GAMES[chat_id]
    await context.bot.send_message(chat_id, "⏳ 90 seconds left! Use /enter to join.")
    
    await asyncio.sleep(60)  # 30 seconds left
    
    if chat_id not in WORD_GAMES:
        return
    
    await context.bot.send_message(chat_id, "⚡ 30 seconds left! Use /enter to join.")
    
    await asyncio.sleep(30)
    
    if chat_id not in WORD_GAMES:
        return
    
    game = WORD_GAMES[chat_id]
    game.started = True
    
    # Check player count
    if len(game.players) < 2:
        # Refund all players
        for user_id in game.players:
            await update_balance(user_id, game.entry_fee)
        
        await context.bot.send_message(
            chat_id,
            "❌ At least 2 players are required. Entry fees have been refunded."
        )
        del WORD_GAMES[chat_id]
        return
    
    # Send word reveal message with button
    keyboard = [[InlineKeyboardButton("Sᴇᴇ Wᴏʀᴅ 👁️", callback_data=f"word:{chat_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = await context.bot.send_message(
        chat_id,
        "⌨️ WORD IS READY!\n\n"
        "⚡ The first player to type it correctly wins!",
        reply_markup=reply_markup
    )
    
    game.message_id = msg.message_id

async def enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /enter command"""
    chat = update.effective_chat
    
    if chat.id not in WORD_GAMES:
        await update.message.reply_text("❌ No word game is currently running.")
        return
    
    game = WORD_GAMES[chat.id]
    
    if game.started:
        await update.message.reply_text("⛔ Game already started.")
        return
    
    # Check amount
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /enter <amount>")
        return
    
    amount = int(context.args[0])
    if amount != game.entry_fee:
        await update.message.reply_text("❌ Wrong entry amount.")
        return
    
    user = update.effective_user
    
    # Check if already joined
    if user.id in game.players:
        return
    
    # Check balance
    await ensure_user(user.id, user.first_name, user.username)
    user_data = await get_user(user.id)
    
    if not user_data or user_data['balance'] < game.entry_fee:
        await update.message.reply_text("❌ Insufficient balance.")
        return
    
    # Deduct entry fee
    await update_balance(user.id, -game.entry_fee)
    
    # Add player
    game.add_player(user)
    
    await update.message.reply_text(f"✅ {user.first_name} has joined the game.")

async def word_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle word reveal button"""
    query = update.callback_query
    await query.answer()
    
    try:
        chat_id = int(query.data.split(":")[1])
    except:
        return
    
    if chat_id not in WORD_GAMES:
        await query.answer("This Game Has Ended.", show_alert=True)
        return
    
    game = WORD_GAMES[chat_id]
    await query.answer(
        f"First To Type This Word Wins\n\n{game.word}",
        show_alert=True
    )

async def word_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Listen for correct word typing"""
    chat = update.effective_chat
    msg = update.message
    
    if not msg or chat.id not in WORD_GAMES:
        return
    
    game = WORD_GAMES[chat.id]
    
    if not game.started:
        return
    
    if msg.from_user.id not in game.players:
        return
    
    # Case-sensitive exact match
    if msg.text != game.word:
        return
    
    winner = msg.from_user
    
    # Calculate prize (90% of pool)
    prize = int(game.entry_fee * len(game.players) * 0.9)
    
    # Update winner's balance
    await update_balance(winner.id, prize)
    
    # Update button message
    try:
        if game.message_id:
            keyboard = [[InlineKeyboardButton("Game Ended", callback_data="word:ended")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.edit_message_reply_markup(
                chat_id=chat.id,
                message_id=game.message_id,
                reply_markup=reply_markup
            )
    except Exception:
        pass
    
    await context.bot.send_message(
        chat.id,
        f"🏆 Winner: {winner.first_name}\n💰 Prize Won: ₹{prize}"
    )
    
    # Cleanup
    del WORD_GAMES[chat.id]
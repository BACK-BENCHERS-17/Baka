"""
Routes /join and /enter to the correct game based on which game is active in the chat.

/join  → Roulette (if active) → Bomb game (fallback)
/enter → Bluff   (if active) → Word game (fallback)
"""
from telegram import Update
from telegram.ext import ContextTypes


async def join_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route /join to roulette or bomb game."""
    from handlers.roulette_game import ROULETTE_GAMES, roulette_join
    from handlers.bomb_game import join as bomb_join

    chat_id = update.effective_chat.id
    if chat_id in ROULETTE_GAMES:
        handled = await roulette_join(update, context)
        if handled:
            return
    await bomb_join(update, context)


async def enter_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route /enter to bluff or word game."""
    from handlers.bluff_game import BLUFF_GAMES, bluff_enter
    from handlers.word_game import enter as word_enter

    chat_id = update.effective_chat.id
    if chat_id in BLUFF_GAMES:
        handled = await bluff_enter(update, context)
        if handled:
            return
    await word_enter(update, context)

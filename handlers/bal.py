from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, get_global_rank, is_premium
from utils.permissions import is_bot, is_baka_bot, is_owner
from config import BOT_USERNAME

async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bal and /balance commands"""
    message = update.message
    chat = update.effective_chat
    # Check if economy is enabled in group
    if chat.type in ["group", "supergroup"]:
        from utils.permissions import is_economy_enabled
        if not await is_economy_enabled(chat.id):
            await update.message.reply_text("⚠️ Economy commands are disabled in this group. Use /open to enable.")
            return
    
    # Determine target
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    else:
        target = update.effective_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        await update.message.reply_text(
            f"👤 Name: {target.first_name or target.username or 'Baka'}\n"
            f"💰 Balance: $ Infinite\n"
            f"🏆 Global Rank: Prime\n"
            f"❤️ Status: Immortal\n"
            f"⚔️ Kills: WarGod"
        )
        return
    
    # Check if target is a bot
    if is_bot(target):
        await update.message.reply_text("🤖 Specified user is a bot!")
        return
    
    # Ensure user exists
    await ensure_user(target.id, target.first_name, target.username)
    
    # Get user data
    user_data = await get_user(target.id)
    if not user_data:
        await update.message.reply_text("❌ User data not found.")
        return
    
    # Get rank
    rank = await get_global_rank(target.id)
    
    # Format status with emoji
    status_emoji = "💀" if user_data['status'] == 'dead' else "❤️"
    
    # Premium icon
    premium = await is_premium(target.id)
    premium_icon = "💓" if premium else "👤"
    
    response = (
        f"{premium_icon} Name: {target.first_name}\n"
        f"💰 Balance: ${user_data['balance']}\n"
        f"🏆 Global Rank: {rank}\n"
        f"{status_emoji} Status: {user_data['status']}\n"
        f"⚔️ Kills: {user_data['kills']}"
    )
    
    await update.message.reply_text(response,parse_mode="HTML")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for /bal"""
    await bal(update, context)
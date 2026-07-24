from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, update_balance, set_status
from utils.permissions import is_baka_bot, is_bot
from config import REVIVE_COST, BOT_USERNAME

async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /revive command"""
    user = update.effective_user
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
        target = user  # No reply means self-revive
    
    # Check if target is Baka bot
    if is_baka_bot(target):
        await update.message.reply_text("😇 I'm immortal, You pathetic human!")
        return
    
    # Check if target is a bot
    if is_bot(target):
        await update.message.reply_text("🤖 You cannot revive a bot!")
        return
    
    # Ensure users exist
    await ensure_user(user.id, user.first_name, user.username)
    await ensure_user(target.id, target.first_name, target.username)
    
    # Get user data
    user_data = await get_user(user.id)
    target_data = await get_user(target.id)
    
    if not target_data:
        await update.message.reply_text("❌ Target user not found.")
        return
    
    # Check if target is already alive
    if target_data['status'] == 'alive':
        await update.message.reply_text(f"✅ <b>{target.first_name}</b> is already alive!", parse_mode="HTML")
        return
    
    # Check giver's balance
    if not user_data or user_data['balance'] < REVIVE_COST:
        await update.message.reply_text(
            f"❌ You need <b>${REVIVE_COST}</b> to revive, but you have only <b>${user_data['balance'] if user_data else 0}</b>",
            parse_mode="HTML"
        )
        return
    
    # Update database
    await update_balance(user.id, -REVIVE_COST)
    await set_status(target.id, "alive")
    
    # Send success message
    if user.id == target.id:
        await update.message.reply_text(f"❤️ You revived yourself! -<b>${REVIVE_COST}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text(
            f"❤️ <b>{user.first_name}</b> revived <b>{target.first_name}</b>! -<b>${REVIVE_COST}</b>",
            parse_mode="HTML"
        )
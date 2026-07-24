import random
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    ensure_user, get_user, update_balance, add_item,
    get_random_media, is_premium
)
from utils.permissions import is_baka_bot, is_bot
from config import ITEMS, BOT_USERNAME
from utils.helpers import get_mention_html

async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gift command"""
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("⚠️ Reply to the user you want to gift.")
        return
    
    # Check item
    if not context.args:
        await update.message.reply_text("🎁 Usage: /gift <item_name>\nExample: /gift rose")
        return
    
    giver = update.effective_user
    target = update.message.reply_to_message.from_user
    item_key = context.args[0].lower()
    
    # Special case: Baka bot
    if is_baka_bot(target):
        # Allow sending gifts to Baka bot
        pass
    elif is_bot(target):
        await update.message.reply_text("😼 They don't need gifts, keep it for someone special.")
        return
    
    # Check item validity
    if item_key not in ITEMS:
        await update.message.reply_text("❌ Invalid item.\nCheck available items with /items")
        return
    
    # Get item details
    item_name, price = ITEMS[item_key]
    
    # Ensure users exist
    await ensure_user(giver.id, giver.first_name, giver.username)
    await ensure_user(target.id, target.first_name, target.username)
    
    # Check giver's balance
    giver_data = await get_user(giver.id)
    if not giver_data or giver_data['balance'] < price:
        await update.message.reply_text(
            f"💸 You need <b>${price}</b> to gift {item_name}.\n"
            f"Your balance: <b>${giver_data['balance'] if giver_data else 0}</b>",
            parse_mode="HTML"
        )
        return
    
    # Update database
    await update_balance(giver.id, -price)
    await add_item(target.id, item_key)
    
    # Try to send GIF
    media_pool_name = f"gift_{item_key}"
    gif_file_id = await get_random_media(media_pool_name, "gif")
    if gif_file_id:
        try:
            await update.message.reply_animation(gif_file_id)
        except Exception:
            pass  # Skip if GIF fails
    
    # Get mentions with hyperlinks
    giver_mention = get_mention_html(giver.id, giver.first_name, giver.username)
    target_mention = get_mention_html(target.id, target.first_name, target.username)
    
    # Send success message
    await update.message.reply_text(
        f"{giver_mention} gifted {target_mention} <b>{item_name}</b> 💞🥰",
        parse_mode="HTML"
    )
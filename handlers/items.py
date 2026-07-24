from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user_items
from config import ITEMS
from utils.permissions import is_bot, is_baka_bot
from utils.helpers import get_mention_html

async def items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /items command - Show available items"""
    message = update.message
    
    # Show available items (no reply needed)
    text = "📦 Available Gift Items:\n\n"
    for item_key, (item_name, price) in ITEMS.items():
        text += f"{item_name} — ${price}\n"
    
    await update.message.reply_text(text)

async def item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /item command - Show inventory"""
    message = update.message
    
    # Determine target
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        show_inventory = True
    else:
        target = update.effective_user
        show_inventory = False
    
    # Special case for bots
    if is_bot(target):
        if is_baka_bot(target):
            # Baka bot has inventory
            pass
        else:
            await update.message.reply_text("✨ It doesn't have any gifts inventory.")
            return
    
    # Show self inventory (no reply)
    if not show_inventory:
        await ensure_user(target.id, target.first_name, target.username)
        user_items = await get_user_items(target.id)
        
        if not user_items:
            mention = get_mention_html(target.id, target.first_name, target.username)
            await update.message.reply_text(f"🎁 {mention}'s Inventory:\n\nNo items yet 😢", parse_mode="HTML")
            return
        
        mention = get_mention_html(target.id, target.first_name, target.username)
        text = f"🎁 {mention}'s Inventory:\n\n"
        
        item_count = {}
        for item_name, quantity in user_items:
            if item_name in item_count:
                item_count[item_name] += quantity
            else:
                item_count[item_name] = quantity
        
        for item_name, total_quantity in item_count.items():
            if item_name in ITEMS:
                item_display = ITEMS[item_name][0]
                text += f"{item_display} × <b>{total_quantity}</b>\n"
        
        await update.message.reply_text(text, parse_mode="HTML")
        return
    
    # Show other's inventory (with reply)
    await ensure_user(target.id, target.first_name, target.username)
    user_items = await get_user_items(target.id)
    
    if not user_items:
        mention = get_mention_html(target.id, target.first_name, target.username)
        await update.message.reply_text(f"<b>{target.first_name}</b> has no items yet 😢", parse_mode="HTML")
        return
    
    mention = get_mention_html(target.id, target.first_name, target.username)
    text = f"🎁 {mention}'s Inventory:\n\n"
    
    item_count = {}
    for item_name, quantity in user_items:
        if item_name in item_count:
            item_count[item_name] += quantity
        else:
            item_count[item_name] = quantity
    
    for item_name, total_quantity in item_count.items():
        if item_name in ITEMS:
            item_display = ITEMS[item_name][0]
            text += f"{item_display} × <b>{total_quantity}</b>\n"
    
    await update.message.reply_text(text, parse_mode="HTML")
import math
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_user, get_user, update_balance, is_premium, get_economy_status
from utils.permissions import can_target_user
from config import GIVE_TAX_NORMAL, GIVE_TAX_PREMIUM, BOT_USERNAME

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /give command"""
    message = update.message
    chat = update.effective_chat
    
    # Check reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await update.message.reply_text("❗ Usage: /give {amount} (as reply)")
        return
    
    # Check if economy is enabled in this group (only for groups)
    if chat.type in ["group", "supergroup"]:
        if not await get_economy_status(chat.id):
            await update.message.reply_text("⛔ Economy commands are disabled in this group.")
            return
    
    # Check amount
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /give {amount} (as reply)")
        return
    
    giver = update.effective_user
    target = message.reply_to_message.from_user
    amount = int(context.args[0])
    
    # Check if giving to self
    if giver.id == target.id:
        await update.message.reply_text("❌ You cannot give money to yourself!")
        return
    
    # Special case: Baka bot
    if target.username == BOT_USERNAME:
        await update.message.reply_text("💸 I'm Rich Bi$ch !")
        return
    
    # Check if target is a bot
    if target.is_bot:
        await update.message.reply_text("🤖 You cannot give balance to a bot!")
        return
    
    # Check permissions
    can_target, msg = can_target_user(target, giver)
    if not can_target:
        await update.message.reply_text(msg)
        return
    
    # Ensure users exist
    await ensure_user(giver.id, giver.first_name, giver.username)
    await ensure_user(target.id, target.first_name, target.username)
    
    # Check premium status
    premium = await is_premium(giver.id)
    
    # Calculate tax
    tax_rate = GIVE_TAX_PREMIUM if premium else GIVE_TAX_NORMAL
    fee = int(amount * tax_rate)  # Floor tax
    total_required = amount + fee
    
    # Check giver's balance
    giver_data = await get_user(giver.id)
    if not giver_data or giver_data['balance'] < total_required:
        await update.message.reply_text(
            f"❌ You need ${total_required} (including {int(tax_rate*100)}% fee) to give ${amount}!"
        )
        return
    
    # Update balances
    await update_balance(giver.id, -total_required)
    await update_balance(target.id, amount)
    
    # Send success message
    await update.message.reply_text(
        f"✅ You gave <b>${amount}</b> to <b>{target.first_name}</b> with <b>${fee}</b> fee deducted! "
        f"({int(tax_rate*100)}% tax applied) 💸",
        parse_mode="HTML"
    )
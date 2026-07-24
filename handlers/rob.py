import time

from telegram import Update
from telegram.ext import ContextTypes

from database import (
    ensure_user,
    get_user,
    update_balance,
    check_daily_limit,
    is_premium,
    get_protection_expiry,
    get_economy_status
)
from utils.permissions import can_target_user
from config import (
    ROB_MAX_NORMAL,
    ROB_MAX_PREMIUM,
    GIVE_TAX_NORMAL,
    GIVE_TAX_PREMIUM,
    BOT_USERNAME
)

async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.message
    robber = update.effective_user

    # DM check
    if chat.type == "private":
        await message.reply_text("⚠️ This command works in groups only.")
        return
    
    # Check if economy is enabled in this group
    if not await get_economy_status(chat.id):
        await message.reply_text("⛔ Economy commands are disabled in this group.")
        return

    # Must reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("⚠️ Reply to a user to rob.")
        return

    victim = message.reply_to_message.from_user

    # Amount check
    if not context.args or not context.args[0].isdigit():
        await message.reply_text("❗ Usage: /rob <amount>")
        return

    amount = int(context.args[0])

    # Rob on bot
    if victim.is_bot:
        if victim.username == BOT_USERNAME:
            await message.reply_text("😂 Don't try to be over smart.")
        else:
            await message.reply_text("🤖 You cannot rob a bot!")
        return

    # Rob on self
    if robber.id == victim.id:
        await message.reply_text("😂 How to bcum pro lik u?")
        return

    # Ensure users exist
    await ensure_user(robber.id, robber.first_name, robber.username)
    await ensure_user(victim.id, victim.first_name, victim.username)

    # Check if robber is dead
    robber_data = await get_user(robber.id)
    if robber_data and robber_data['status'] == 'dead':
        await message.reply_text("💀 Dead users cannot rob anyone!")
        return

    # Check if victim is dead
    victim_data = await get_user(victim.id)
    if victim_data and victim_data['status'] == 'dead':
        await message.reply_text("💀 Victim is already dead!")
        return

    premium = await is_premium(robber.id)

    # Daily rob limit
    if not await check_daily_limit(robber.id, "rob", premium):
        await message.reply_text("⛔ Daily rob limit reached!")
        return

    max_amount = ROB_MAX_PREMIUM if premium else ROB_MAX_NORMAL
    if amount < 1 or amount > max_amount:
        await message.reply_text(
            f"❗ You can only rob between <b>1</b> - <b>{max_amount}</b>.\n"
            f"⬆️ Upgrade to <b>PREMIUM</b> → /pay",
            parse_mode="HTML"
        )
        return

    # Permission check
    allowed, reason = can_target_user(victim, robber)
    if not allowed:
        await message.reply_text(reason)
        return

    # Protection check
    protected_until = await get_protection_expiry(victim.id)
    if protected_until and protected_until > int(time.time()):
        await message.reply_text("🛡️ Target is protected!")
        return

    victim_balance = victim_data.get("balance", 0) if victim_data else 0

    # Insufficient funds
    if victim_balance < amount:
        await message.reply_text(
            f"❌ Victim only has <b>${victim_balance}</b>",
            parse_mode="HTML"
        )
        return

    # Tax calculation
    tax_rate = GIVE_TAX_PREMIUM if premium else GIVE_TAX_NORMAL
    tax = int(amount * tax_rate)
    gained = amount - tax

    await update_balance(victim.id, -amount)
    await update_balance(robber.id, gained)

    # Success message
    await message.reply_text(
        f"👤 <b>{robber.first_name}</b> robbed <b>${amount}</b> from <b>{victim.first_name}</b>\n"
        f"💰 gained: <b>${gained}</b>",
        parse_mode="HTML"
    )
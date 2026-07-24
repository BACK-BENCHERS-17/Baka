from telegram import Update
from telegram.ext import ContextTypes

from database import (
    ensure_user,
    get_user,
    update_balance,
    check_daily_limit,
    is_premium,
    add_kill,
    set_status,
    get_economy_status
)
from utils.permissions import can_target_user
from config import (
    KILL_REWARD_NORMAL,
    KILL_REWARD_PREMIUM,
    BOT_USERNAME
)

import random

async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.message
    killer = update.effective_user

    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check if economy is enabled in this group
    if not await get_economy_status(chat.id):
        await message.reply_text("⛔ Economy commands are disabled in this group.")
        return

    # Must reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("⚠️ Reply to someone to kill them.")
        return

    target = message.reply_to_message.from_user

    # Kill on bot
    if target.is_bot:
        if target.username == BOT_USERNAME:
            await message.reply_text("😂 Nice try on me, better luck next time!")
        else:
            await message.reply_text("🤖 You cannot kill a bot!")
        return

    # Kill on self
    if killer.id == target.id:
        await message.reply_text("❌ You cannot kill yourself!")
        return

    # Ensure users exist
    await ensure_user(killer.id, killer.first_name, killer.username)
    await ensure_user(target.id, target.first_name, target.username)

    killer_data = await get_user(killer.id)
    target_data = await get_user(target.id)

    # Killer already dead
    if killer_data and killer_data['status'] == 'dead':
        await message.reply_text("💀 Dead users cannot kill anyone!")
        return

    # Target already dead
    if target_data and target_data['status'] == 'dead':
        await message.reply_text("💀 Victim is already dead!")
        return

    # Permission check
    allowed, reason = can_target_user(target, killer)
    if not allowed:
        await message.reply_text(reason)
        return

    premium = await is_premium(killer.id)

    # Daily kill limit
    if not await check_daily_limit(killer.id, "kill", premium):
        await message.reply_text("⛔ Daily kill limit reached!")
        return

    # Reward calculation
    reward_range = KILL_REWARD_PREMIUM if premium else KILL_REWARD_NORMAL
    reward = random.randint(*reward_range)

    # Update database
    await update_balance(killer.id, reward)
    await add_kill(killer.id)  # Increment killer's kill count
    await set_status(target.id, "dead")  # Mark target as dead

    await message.reply_text(
        f"👤 <b>{killer.first_name}</b> killed <b>{target.first_name}</b>!\n"
        f"💰 Reward: <b>${reward}</b>",
        parse_mode="HTML"
    )
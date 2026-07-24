import time
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    ensure_user, ensure_group, is_group_claimed, mark_group_claimed,
    update_balance, get_user
)
from config import CLAIM_MIN_MEMBERS, CLAIM_PER_MEMBER

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /claim command"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Group only
    if chat.type == "private":
        await update.message.reply_text("⚠️ This command only works in groups!")
        return
    
    # Check member count
    try:
        member_count = await context.bot.get_chat_member_count(chat.id)
    except Exception:
        await update.message.reply_text("⚠️ Unable to fetch group members.")
        return
    
    if member_count < CLAIM_MIN_MEMBERS:
        await update.message.reply_text(
            f"❌ At least {CLAIM_MIN_MEMBERS} members are required to claim the reward!"
        )
        return
    
    # Check if group already claimed
    if await is_group_claimed(chat.id):
        await update.message.reply_text(
            "❌ Someone has already claimed the reward for this group!"
        )
        return
    
    # Ensure user and group exist
    await ensure_user(user.id, user.first_name, user.username)
    await ensure_group(chat.id, chat.title)
    
    # Calculate reward
    reward = member_count * CLAIM_PER_MEMBER
    
    # Update database with transaction
    import aiosqlite
    from config import DB_PATH
    
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("BEGIN IMMEDIATE")
            
            # Mark group as claimed
            await db.execute(
                "INSERT INTO claim_rewards (group_id, claimed_by, claimed_at) VALUES (?, ?, ?)",
                (chat.id, user.id, int(time.time()))
            )
            
            # Add reward to user
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id=?",
                (reward, user.id)
            )
            
            await db.commit()
            
        except Exception:
            await db.rollback()
            await update.message.reply_text("⚠️ Claim failed. Try again later.")
            return
    
    # Send success message
    await update.message.reply_text(
        f"✅ You claimed the group bonus.\n"
        f"💰 You recieved ${reward} bonus!"
    )
import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes

from database import ensure_user, get_user, update_balance, is_premium
from utils.helpers import get_ist_date, can_claim_daily
from config import DAILY_NORMAL, DAILY_PREMIUM, DB_PATH

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command"""
    chat = update.effective_chat
    user = update.effective_user

    # DM only
    if chat.type != "private":
        await update.message.reply_text("⚠️ You can claim daily reward in DM only.")
        return

    # Ensure user exists
    await ensure_user(user.id, user.first_name, user.username)

    # Get user data
    user_data = await get_user(user.id)
    if not user_data:
        await update.message.reply_text("❌ User data not found.")
        return

    # Check if already claimed today
    last_claim = user_data.get("last_daily_claim")
    if last_claim and not can_claim_daily(last_claim):
        await update.message.reply_text(
            "⏳ You already claimed today's reward!\n"
            "Come back after 12:00 AM IST tonight."
        )
        return

    # Determine reward amount
    premium = await is_premium(user.id)
    amount = DAILY_PREMIUM if premium else DAILY_NORMAL

    # Update balance
    await update_balance(user.id, amount)

    # Update last claim date
    today = get_ist_date()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_daily_claim=? WHERE user_id=?",
            (today, user.id)
        )
        await db.commit()

    # Success message
    await update.message.reply_text(
        f"✅ You received: ${amount} daily reward!\n"
        f"💓 Upgrade to premium using /pay to get ${DAILY_PREMIUM} daily reward!"
    )
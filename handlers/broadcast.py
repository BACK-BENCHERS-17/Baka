import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import RetryAfter, Forbidden, BadRequest
from database import get_all_users, get_all_groups
from config import OWNER_IDS

PENDING_BROADCASTS = {}

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("❌ You are not allowed to use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message to broadcast.")
        return

    PENDING_BROADCASTS[update.effective_user.id] = update.message.reply_to_message

    keyboard = [
        [
            InlineKeyboardButton("Cᴏɴғɪʀᴍ ✅", callback_data="bc_yes"),
            InlineKeyboardButton("Cᴀɴᴄᴇʟ ❌", callback_data="bc_no"),
        ]
    ]

    await update.message.reply_text(
        "⚠️ Are you sure you want to broadcast this message?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in OWNER_IDS:
        return

    if query.data == "bc_no":
        PENDING_BROADCASTS.pop(user_id, None)
        await query.edit_message_text("❌ Broadcast cancelled.")
        return

    msg = PENDING_BROADCASTS.pop(user_id, None)
    if not msg:
        await query.edit_message_text("❌ Nothing to send.")
        return

    await query.edit_message_text("📢 Broadcasting…")

    users = await get_all_users()
    groups = await get_all_groups()
    targets = users + groups

    sent = failed = 0

    for target_id in targets:
        try:
            await msg.copy(target_id)
            sent += 1
            await asyncio.sleep(random.uniform(0.8, 1.2))

        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                await msg.copy(target_id)
                sent += 1
            except Exception:
                failed += 1

        except (Forbidden, BadRequest):
            failed += 1

        except Exception:
            failed += 1

    await context.bot.send_message(
        user_id,
        f"✅ Broadcast completed.\n\n"
        f"👤 Users reached: {sent}\n"
        f"❌ Failed: {failed}"
    )
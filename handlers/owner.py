import time
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    ensure_user, add_premium, remove_premium,
    update_balance, get_user
)
from config import OWNER_IDS

async def addpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addpremium command (owner only)"""
    # Owner only
    if update.effective_user.id not in OWNER_IDS:
        return
    
    # Check arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addpremium <user_id> <days>")
        return
    
    try:
        uid = int(context.args[0])
        days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid arguments.")
        return
    
    # Add premium
    expiry = await add_premium(uid, days)
    
    # Get user info
    await ensure_user(uid)
    user_data = await get_user(uid)
    
    if user_data and user_data['first_name']:
        name = user_data['first_name']
    else:
        name = f"User {uid}"
    
    # Format expiry date — cap at year 3000 to avoid ValueError
    from datetime import datetime
    try:
        expiry_date = datetime.fromtimestamp(min(expiry, 32503680000)).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        expiry_date = "Extended"

    await update.message.reply_text(
        f"✅ Premium activated for {name}\n"
        f"⏳ Duration: {days} days\n"
        f"📅 Expires: {expiry_date}"
    )

async def removepremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removepremium command (owner only)"""
    # Owner only
    if update.effective_user.id not in OWNER_IDS:
        return
    
    # Check arguments
    if not context.args:
        await update.message.reply_text("Usage: /removepremium <user_id>")
        return
    
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return
    
    # Remove premium
    await remove_premium(uid)
    
    # Get user info
    user_data = await get_user(uid)
    
    if user_data and user_data['first_name']:
        name = user_data['first_name']
    else:
        name = f"User {uid}"
    
    await update.message.reply_text(f"❌ Premium removed from {name}")

async def setbal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setbal command (owner only)"""
    # Owner only
    if update.effective_user.id not in OWNER_IDS:
        return
    
    # Check arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setbal <user_id> <amount>")
        return
    
    try:
        uid = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid arguments.")
        return
    
    # Ensure user exists
    await ensure_user(uid)
    
    # Set balance (by clearing and adding)
    user_data = await get_user(uid)
    if user_data:
        current = user_data['balance']
        diff = amount - current
        await update_balance(uid, diff)
    else:
        # Set initial balance
        import aiosqlite
        from config import DB_PATH
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE users SET balance=? WHERE user_id=?",
                (amount, uid)
            )
            await db.commit()
    
    # Get user info
    user_data = await get_user(uid)
    
    if user_data and user_data['first_name']:
        name = user_data['first_name']
    else:
        name = f"User {uid}"
    
    await update.message.reply_text(f"💰 Balance updated for {name}: ${amount}")

async def resetbal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resetbal command (owner only)"""
    # Owner only
    if update.effective_user.id not in OWNER_IDS:
        return
    
    # Check arguments
    if not context.args:
        await update.message.reply_text("Usage: /resetbal <user_id>")
        return
    
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return
    
    # Reset balance
    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance=0 WHERE user_id=?",
            (uid,)
        )
        await db.commit()
    
    # Get user info
    user_data = await get_user(uid)
    
    if user_data and user_data['first_name']:
        name = user_data['first_name']
    else:
        name = f"User {uid}"
    
    await update.message.reply_text(f"♻️ Balance reset for {name}")

async def ownercommands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ownercommands command (owner only)"""
    # Owner only
    if update.effective_user.id not in OWNER_IDS:
        return
    
    text = """👑 Owner Commands:

/broadcast - Send message to all users
/addgif <cmd> - Add GIF to command pool
/addpremium <uid> <days> - Grant premium
/removepremium <uid> - Remove premium
/setbal <uid> <amount> - Set user balance
/resetbal <uid> - Reset user balance
/ownercommands - Show this list"""
    
    await update.message.reply_text(text)
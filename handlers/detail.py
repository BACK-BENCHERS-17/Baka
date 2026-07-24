import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes
from config import DB_PATH

async def detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /detail command"""
    # Determine target user ID
    if context.args and context.args[0].isdigit():
        uid = int(context.args[0])
    elif update.message.reply_to_message and update.message.reply_to_message.from_user:
        uid = update.message.reply_to_message.from_user.id
    else:
        await update.message.reply_text("⚠️ Usage: /detail (reply) or /detail user_id")
        return
    
    # Fetch name history (simplified - you'd need to track this in your database)
    async with aiosqlite.connect(DB_PATH) as db:
        # In a real implementation, you'd have name_history and username_history tables
        # For now, we'll fetch from users table
        cursor = await db.execute(
            "SELECT first_name, username FROM users WHERE user_id=?",
            (uid,)
        )
        row = await cursor.fetchone()
        
        if not row:
            await update.message.reply_text("User not found in database.")
            return
        
        first_name, username = row
        
        text = "User's History\n________________________\n\nFirst Names:\n"
        if first_name:
            text += f"• {first_name}\n"
        
        text += "\n-----------\n\nUser Names:\n"
        if username:
            text += f"• @{username}\n"
        
        await update.message.reply_text(text)
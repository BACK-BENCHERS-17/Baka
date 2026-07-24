from telegram import Update
from telegram.ext import ContextTypes
from database import get_top_rich, is_premium
from utils.helpers import get_mention_html
from config import BOT_USERNAME

async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /toprich command"""
    # Get top users
    top_users = await get_top_rich(10)
    
    if not top_users:
        await update.message.reply_text("⚠️ No data available.")
        return
    
    # Build leaderboard
    text = "🏆 Top 10 Richest Users:\n\n"
    
    for i, (user_id, first_name, username, balance, premium_until) in enumerate(top_users, 1):
        # Check if premium
        premium = await is_premium(user_id)
        icon = "💓" if premium else "👤"
        
        # Get mention
        mention = get_mention_html(user_id, first_name or "User", username)
        
        text += f"{icon} {mention}: ${balance}\n"
    
    # Add footer
    text += "\n💓 = Premium • 👤 = Normal\n\n"
    text += "✅ Upgrade to premium : /pay"
    
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
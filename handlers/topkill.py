from telegram import Update
from telegram.ext import ContextTypes
from database import get_top_kill, is_premium
from utils.helpers import get_mention_html

async def topkill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /topkill command"""
    # Get top killers
    top_users = await get_top_kill(10)
    
    if not top_users:
        await update.message.reply_text("⚠️ No data available.")
        return
    
    # Build leaderboard
    text = "🏆 Top 10 Killers:\n\n"
    
    for i, (user_id, first_name, username, kills, premium_until) in enumerate(top_users, 1):
        # Check if premium
        premium = await is_premium(user_id)
        icon = "💓" if premium else "👤"
        
        # Get mention
        mention = get_mention_html(user_id, first_name or "User", username)
        
        text += f"{icon} {mention}: {kills} kills\n"
    
    # Add footer
    text += "\n💓 = Premium • 👤 = Normal\n\n"
    text += "✅ Upgrade to premium : /pay"
    
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
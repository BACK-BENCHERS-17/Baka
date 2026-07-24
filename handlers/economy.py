from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BOT_USERNAME

ECONOMY_GUIDE = """💰 <b>Baka Economy System Guide</b>

💬 <b>How it works:</b>
Manage your virtual money and items in the group! Use commands below to earn, gift, buy, or interact with others.

🔹 <b>Normal Users (👤)</b>:
• /daily — Receive $1000 daily reward
• /claim — Add Baka in group to claim
• /bal — Check your/your friend's balance (👤 prefix)
• /rob (reply) <code>amount</code> — Max $10k
• /kill (reply) — Reward $100-200
• /revive (reply or without reply) — Revive you or a friend
• /protect <code>1d</code> — Buy protection
• /give (reply) <code>amount</code> — Gift money (10% fee)
• /toprich — See top 10 richest users (👤 normal)
• /topkill — See top 10 killers (👤 normal)

• 👤 Normal users can rob and kill 200 users .

🔹 <b>Premium Users (💓)</b>:
• /pay — Become premium user
• /daily — Receive $2000 daily reward 
• /bal — Check your/your friend's balance (💓 prefix)
• /rob (reply) <code>amount</code> — Max $1 lakh
• /kill (reply) — Reward $200-400
• /revive (reply or without reply) — Revive you or a friend instantly
• /protect  <code>1d</code>|<code>2d</code>|<code>3d</code> — Buy protection (avoid robbery)
• /give (reply) <code>amount</code> — Gift money (5% fee)
• /toprich — See top 10 richest users (💓 premium highlight)
• /topkill — See top 10 killers (💓 premium highlight)
• /check — Check any user's protection (💓 premium only)

• /report — Report something to the Owner (💓 premium only)

• 💓 Premium users can rob and kill 400 users 

• 💓 Premium users robbing tax 5% and 👤 normal users robbing tax 10%

🎁 <b>Item & Gifting</b>
• Earn money by killing others
• Gift money with fee (premium users pay less tax)
• Buy protection to avoid robbery
• Top rankings for richest and killers with premium highlight"""

async def economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /economy command"""
    chat = update.effective_chat
    user = update.effective_user
    
    # In DM: send full guide
    if chat.type == "private":
        await update.message.reply_text(ECONOMY_GUIDE, parse_mode="HTML")
        return
    
    # In group: send to DM and show redirect
    try:
        # Try to send to DM
        await context.bot.send_message(
            chat_id=user.id,
            text=ECONOMY_GUIDE,
            parse_mode="HTML"
        )
        
        # Success: show redirect in group
        keyboard = [[InlineKeyboardButton("📩 Open In DM", url=f"https://t.me/{BOT_USERNAME}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📩 I sent you the economy guide in DM!\nClick the button below to open it.",
            reply_markup=reply_markup
        )
        
    except Exception:
        # User blocked bot or other error
        await update.message.reply_text(
            "📩 I tried to send you the economy guide in DM, but I couldn't. "
            "Please make sure you've started a chat with me first!"
        )
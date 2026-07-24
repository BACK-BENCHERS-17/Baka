from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PAYMENT_LINK

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pay command"""
    # DM only
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ This command works in DM only.")
        return
    
    text = """💓 Baka Premium Access Link

👇 Important Note :

1. You must enter your Telegram ID (Numeric ID) on the payment page.
It's not necessary to provide real phone number on payment page

2. Upon successful payment, you will receive automatic premium access.

3. You can check your Telegram ID using this command : /id 
4. Check all premium features using : /economy 

Thank you! 💓

Here is your payment link: https://rzp.io/rzp/kairo08"""
    
    keyboard = [[InlineKeyboardButton("Pay Now 💳", url=PAYMENT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)
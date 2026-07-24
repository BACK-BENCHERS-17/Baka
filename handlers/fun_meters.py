import random
from telegram import Update
from telegram.ext import ContextTypes
from utils.permissions import is_baka_bot
from config import BOT_USERNAME

async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /brain command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("Reply to someone !")
        return
    
    target = update.message.reply_to_message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        await update.message.reply_text(f"IQ level of 𝐁ᴀᴋᴀ 💗 is ∞ 😎")
        return
    
    percent = random.randint(40, 140)
    await update.message.reply_text(f"IQ level of {target.first_name} is {percent}% 😎")

async def look(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /look command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("Reply to someone !")
        return
    
    target = update.message.reply_to_message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        await update.message.reply_text(f"𝐁ᴀᴋᴀ 💗 ki look rating: ∞ 😁")
        return
    
    percent = random.randint(30, 100)
    await update.message.reply_text(f"{target.first_name} ki look rating: {percent}% 😍")

async def stupid_meter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stupid_meter command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("Reply to someone !")
        return
    
    target = update.message.reply_to_message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        await update.message.reply_text(f"Hmm 🤔 Stupid meter scanning...\nResult for 𝐁ᴀᴋᴀ 💗: 0% 😵‍💫 stupid detected")
        return
    
    percent = random.randint(0, 100)
    await update.message.reply_text(
        f"Hmm 🤔 Stupid meter scanning...\n"
        f"Result for {target.first_name} : {percent}% 😵‍💫 stupid detected"
    )

async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /love command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("Reply to someone !")
        return
    
    user_a = update.message.reply_to_message.from_user
    user_b = update.message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(user_a):
        await update.message.reply_text(
            f"💕 Love meter report 💕\n"
            f"{user_b.first_name} ❤️ 𝐁ᴀᴋᴀ 💗\n"
            f"Love compatibility: 78% ❤️"
        )
        return
    
    percent = random.randint(50, 100)
    await update.message.reply_text(
        f"💕 Love meter report 💕\n"
        f"{user_a.first_name} ❤️ {user_b.first_name}\n"
        f"Love compatibility: {percent}% ❤️"
    )

async def crush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /crush command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("Reply to someone to check their crush 😁")
        return
    
    target = update.message.reply_to_message.from_user
    
    # Special case: Baka bot
    if is_baka_bot(target):
        await update.message.reply_text(f"💘 Baka's crush is Khushi\nCrush level: ∞ ❤️")
        return
    
    # Try to get random group member (simplified)
    percent = random.randint(40, 90)
    await update.message.reply_text(
        f"💘 {target.first_name}'s secret crush is someone 👀\n"
        f"Crush level: {percent}% ❤️"
    )
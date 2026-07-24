import random
import time
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import ensure_group, get_couples_cooldown, set_couples_cooldown, get_random_media
from config import COUPLES_COOLDOWN, BOT_USERNAME
from utils.permissions import is_bot, is_baka_bot

async def couples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /couples command"""
    chat = update.effective_chat
    
    # Group only
    if chat.type == "private":
        await update.message.reply_text("🚫 You can use this command in groups only !")
        return
    
    # Check cooldown
    last_couple = await get_couples_cooldown(chat.id)
    now = int(time.time())
    
    if last_couple and (now - last_couple) < COUPLES_COOLDOWN:
        await update.message.reply_text("💔 A couple has been declared recently! Try after 5 mins 🙂")
        return
    
    # Get group members
    try:
        # Try to get chat members
        members = []
        async for member in context.bot.get_chat_members(chat.id):
            if not member.user.is_bot and member.user.id != context.bot.id:
                members.append(member.user)
        
        if len(members) < 2:
            await update.message.reply_text("2 members are required atleast!")
            return
        
    except Exception:
        await update.message.reply_text("⚠️ Could not fetch group members.")
        return
    
    # Select two random members
    selected = random.sample(members, 2)
    user1, user2 = selected[0], selected[1]
    
    # Special case: If Baka is selected, pair with Khushi
    if is_baka_bot(user1) or is_baka_bot(user2):
        # For simplicity, we'll just use the two selected users
        # In production, you'd want to fetch a specific user (Khushi) from your config
        pass
    
    # Send GIF
    gif_file_id = await get_random_media("couples", "gif")
    if gif_file_id:
        try:
            await update.message.reply_animation(gif_file_id)
        except Exception:
            pass  # Skip if GIF fails
    
    # Send text
    text = f"""💖 Today's Cute Couple 💖

{user1.first_name} 💞 {user2.first_name}

Love is in the air 💘

~ From Shizu with love 💋"""
    
    await update.message.reply_text(text)
    
    # Update cooldown
    await set_couples_cooldown(chat.id, now)
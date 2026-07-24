from telegram import Update
from telegram.ext import ContextTypes
from handlers.admin import (
    warn, unwarn, mute, unmute, ban, unban, kick,
    promote, demote, pin, unpin, delete
)

DOT_MAP = {
    ".warn": warn,
    ".unwarn": unwarn,
    ".mute": mute,
    ".unmute": unmute,
    ".ban": ban,
    ".unban": unban,
    ".kick": kick,
    ".promote": promote,
    ".demote": demote,
    ".pin": pin,
    ".unpin": unpin,
    ".d": delete,
}

async def dot_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route dot commands to appropriate handlers"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    if not text:
        return
    
    # Get first word (command)
    parts = text.split()
    if not parts:
        return
    
    cmd = parts[0]
    if cmd in DOT_MAP:
        await DOT_MAP[cmd](update, context)
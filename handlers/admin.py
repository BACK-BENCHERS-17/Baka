import time
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from database import ensure_user
from utils.permissions import is_owner, is_admin
from config import OWNER_IDS

# Warn tracking (in-memory for simplicity)
WARN_DB = {}

def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    if not duration_str:
        return -1
    
    duration_str = duration_str.lower()
    
    if duration_str == "0":
        return 0
    
    multipliers = {
        'm': 60,        # minutes
        'h': 3600,      # hours
        'd': 86400,     # days
        'w': 604800,    # weeks
    }
    
    try:
        num = int(duration_str[:-1])
        unit = duration_str[-1]
        
        if unit in multipliers:
            return int(time.time()) + (num * multipliers[unit])
        else:
            return -1
    except ValueError:
        return -1

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .warn command"""
    chat = update.effective_chat
    admin = update.effective_user
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    # Check permissions
    if not await is_admin(chat, admin.id, context.bot):
        return
    
    # Owner immunity
    if is_owner(target.id):
        await update.message.reply_text("😂 Try warning yourself.")
        return
    
    # Track warns
    key = f"{chat.id}:{target.id}"
    current = WARN_DB.get(key, 0) + 1
    WARN_DB[key] = current
    
    if current >= 3:
        # Ban user
        try:
            await chat.ban_member(target.id)
            WARN_DB.pop(key, None)
            await update.message.reply_text(f"🚫 {target.first_name} banned (3 warnings).")
        except Exception:
            await update.message.reply_text("⚠️ Failed to ban user.")
    else:
        await update.message.reply_text(f"⚠️ Warned {target.first_name} ({current}/3).")

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .unwarn command"""
    chat = update.effective_chat
    
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    key = f"{chat.id}:{target.id}"
    
    if key in WARN_DB:
        WARN_DB[key] = max(0, WARN_DB[key] - 1)
        if WARN_DB[key] == 0:
            WARN_DB.pop(key, None)
    
    await update.message.reply_text("✅ Warnings cleared.")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .mute command"""
    chat = update.effective_chat
    admin = update.effective_user
    
    # Group only
    if chat.type == "private":
        from utils.permissions import GROUP_ONLY_MSG
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return
    
    # Check reply
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    # Check permissions
    if not await is_admin(chat, admin.id, context.bot):
        return
    
    # Owner immunity
    if is_owner(target.id):
        return
    
    # Check duration
    if not context.args:
        await update.message.reply_text("Usage: .mute 10m / 2h / 1d")
        return
    
    until = parse_duration(context.args[0])
    if until == -1:
        await update.message.reply_text("❌ Invalid time format.")
        return
    
    try:
        await chat.restrict_member(
            target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until
        )
        await update.message.reply_text(f"🔇 {target.first_name} muted for {context.args[0]}.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to mute user.")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .unmute command"""
    chat = update.effective_chat
    
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        await chat.restrict_member(
            target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text("🔊 Unmuted.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to unmute user.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .ban command"""
    chat = update.effective_chat
    
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    # Owner immunity
    if is_owner(target.id):
        return
    
    try:
        await chat.ban_member(target.id)
        await update.message.reply_text("🚫 Banned.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to ban user.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .unban command"""
    chat = update.effective_chat
    
    if not context.args:
        return
    
    try:
        uid = int(context.args[0])
        await chat.unban_member(uid)
        await update.message.reply_text("✅ Unbanned.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to unban user.")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .kick command"""
    chat = update.effective_chat
    
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    # Owner immunity
    if is_owner(target.id):
        return
    
    try:
        await chat.ban_member(target.id)
        await chat.unban_member(target.id)
        await update.message.reply_text("👢 Kicked.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to kick user.")

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .promote command"""
    chat = update.effective_chat
    
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        await chat.promote_member(
            target.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_promote_members=False
        )
        await update.message.reply_text("⬆️ Promoted.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to promote user.")

async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .demote command"""
    chat = update.effective_chat
    
    if not update.message.reply_to_message:
        return
    
    target = update.message.reply_to_message.from_user
    
    try:
        await chat.promote_member(
            target.id,
            can_manage_chat=False,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        await update.message.reply_text("⬇️ Demoted.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to demote user.")

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .pin command"""
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.pin()
            await update.message.reply_text("📌 Pinned.")
        except Exception:
            await update.message.reply_text("⚠️ Failed to pin message.")

async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .unpin command"""
    try:
        await update.effective_chat.unpin_all_messages()
        await update.message.reply_text("📍 Unpinned.")
    except Exception:
        await update.message.reply_text("⚠️ Failed to unpin messages.")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .d command"""
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
        except Exception:
            pass
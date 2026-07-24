from config import OWNER_IDS, BOT_USERNAME

# Styled group-only message shown whenever a group command is used in DM
GROUP_ONLY_MSG = (
    "🏘️ <b>Gʀᴏᴜᴘ Oɴʟʏ Cᴏᴍᴍᴀɴᴅ!</b>\n\n"
    "❌ Yᴇ ᴄᴏᴍᴍᴀɴᴅ ꜱɪʀꜰ <b>ɢʀᴏᴜᴘꜱ</b> ᴍᴇɪɴ ᴋᴀᴀᴍ ᴋᴀʀᴛᴀ ʜᴀɪ.\n\n"
    "👥 Mᴜᴊʜᴇ ᴀᴘɴᴇ ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴀᴅᴅ ᴋᴀʀᴏ ᴀᴜʀ ᴠᴀʜᴀɴ ᴘʟᴀʏ ᴋᴀʀᴏ! 🎮"
)

async def send_group_only(update) -> bool:
    """Send a styled group-only error and return True if in private chat."""
    if update.effective_chat.type == "private":
        await update.message.reply_text(GROUP_ONLY_MSG, parse_mode="HTML")
        return True
    return False
from database import get_economy_status

async def is_economy_enabled(chat_id: int) -> bool:
    """Check if economy is enabled in group"""
    return await get_economy_status(chat_id)

def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    return user_id in OWNER_IDS

async def is_admin(chat, user_id, bot):
    """Check if user is admin in chat"""
    try:
        member = await bot.get_chat_member(chat.id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

def is_bot(user) -> bool:
    """Check if user is a bot"""
    return user.is_bot if user else False

def is_baka_bot(user) -> bool:
    """Check if user is Baka bot"""
    return user.username == BOT_USERNAME if user and user.username else False

def can_target_user(target_user, command_user=None):
    """
    Check if a user can be targeted by economy/fun commands
    Returns (can_target: bool, message: str)
    """
    if not target_user:
        return False, "User not found"
    
    if is_bot(target_user):
        if is_baka_bot(target_user):
            # Baka bot special case handled by each command
            return True, ""
        return False, "🤖 You cannot target a bot!"
    
    if is_owner(target_user.id):
        return False, "😂 Nice try on me, better luck next time!"
    
    return True, ""

async def is_user_alive(user_data) -> bool:
    """Check if user is alive (helper function)"""
    return user_data and user_data.get('status') != 'dead'
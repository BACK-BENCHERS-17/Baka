from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = """🛡️ <b>Admin Commands (.prefix only):</b>

<b>.warn</b> <code>[reply]</code> — Warn a user (<b>3 = ban</b>)
<b>.unwarn</b> <code>[reply]</code> — Remove <b>1 warning</b>
<b>.mute</b> <code>[reply]/[user id] [time]</code> — Mute temporarily/permanently
<b>.unmute</b> <code>[reply]/[user id]</code> — Unmute the user
<b>.ban</b> <code>[reply]/[user id]</code> — Ban user
<b>.unban</b> <code>[reply]/[user id]</code> — Unban user
<b>.kick</b> <code>[reply]/[user id]</code> — Kick from group
<b>.promote</b> <code>[reply]/[user id] 1/2/3</code> — Promote replied user to admin
<b>.demote</b> <code>[reply]/[user id]</code> — Demote admin
<b>.title</b> <code>[reply]/[user id] [tag]</code> — Set custom title
<b>.pin</b> <code>[reply]</code> — Pin a message
<b>.unpin</b> — Unpin the current message
<b>.d</b> — Delete a message
<b>.help</b> — Show this help"""

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")
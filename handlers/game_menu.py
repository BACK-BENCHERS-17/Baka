from telegram import Update
from telegram.ext import ContextTypes

GAME_MENU = """🎮 <b>Bᴀᴋᴀ Mɪɴɪ Gᴀᴍᴇs</b> 🎮

━━━━━━━━━━━━━━━━━━━━

💣 <b>Bomb Game</b>
/bomb &lt;amount&gt; — Sᴛᴀʀᴛ
/join &lt;amount&gt; — Jᴏɪɴ
/pass — Pᴀss ʙᴏᴍʙ
/leaders — Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ
<i>Last player alive wins the pot!</i>

━━━━━━━━━━━━━━━━━━━━

🃏 <b>Card Game</b>
/card &lt;amount&gt; — Sᴛᴀʀᴛ
/bet &lt;amount&gt; — Jᴏɪɴ
/flip A/B/C/D — Pʟᴀʏ ᴀ ᴄᴀʀᴅ
<i>4 secret cards each • Same sum for all • 4 rounds • Highest card wins round!</i>

━━━━━━━━━━━━━━━━━━━━

🎭 <b>Bluff Game</b>
/bluff &lt;amount&gt; — Sᴛᴀʀᴛ
/enter — Jᴏɪɴ
/drop &lt;value&gt; — Pʟᴀʏ ʏᴏᴜʀ ᴄᴀʀᴅ (ᴄᴀɴ ʟɪᴇ!)
/judge — Cᴀʟʟ ᴛʜᴇ ʙʟᴜꜰꜰ!
<i>3 lives each • Last one standing wins!</i>

━━━━━━━━━━━━━━━━━━━━

💻 <b>Hack Game</b>
/hack &lt;amount&gt; — Sᴛᴀʀᴛ
/register — Jᴏɪɴ
/guess &lt;4-digit-code&gt; — Tʀʏ ᴛᴏ ᴄʀᴀᴄᴋ ɪᴛ!
/end — Cᴀɴᴄᴇʟ ɢᴀᴍᴇ
<i>🎯 Bull = right digit right pos • 🐮 Cow = right digit wrong pos</i>

━━━━━━━━━━━━━━━━━━━━

🎰 <b>Roulette</b>
/roulette &lt;amount&gt; — Sᴛᴀʀᴛ
/join &lt;amount&gt; — Jᴏɪɴ
/bid &lt;amount&gt; — Pʟᴀᴄᴇ ʙɪᴅ ᴇᴀᴄʜ ʀᴏᴜɴᴅ
<i>Lowest bidder eliminated each round • Last player wins!</i>

━━━━━━━━━━━━━━━━━━━━

✍️ <b>Word Game</b>
/wordgame — Sᴛᴀʀᴛ
/enter — Jᴏɪɴ
<i>Type letters to guess the hidden word!</i>

━━━━━━━━━━━━━━━━━━━━

🏆 /leaders — Gᴀᴍᴇ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ
📊 /rank — Yᴏᴜʀ Gᴀᴍᴇ Rᴀɴᴋ
"""


async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /game command — show all mini games"""
    await update.message.reply_text(GAME_MENU, parse_mode="HTML")

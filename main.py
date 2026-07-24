import logging
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN
from database import init_db
from ai.chat_handler import handle_ai_chat

# Start
from handlers.start import start, start_callback

# Basic
from handlers.help import help_cmd
from handlers.pay import pay
from handlers.id import id_cmd

# Economy
from handlers.economy import economy
from handlers.bal import bal, balance
from handlers.daily import daily
from handlers.rob import rob
from handlers.give import give
from handlers.kill import kill
from handlers.protect import protect
from handlers.claim import claim
from handlers.revive import revive
from handlers.items import items, item
from handlers.gift import gift
from handlers.toprich import toprich
from handlers.topkill import topkill
from handlers.check import check

# Games
from handlers.bomb_game import bomb, join, pass_bomb, myrank, leaders
from handlers.word_game import wordgame, enter, word_listener, word_button

# Fun
from handlers.couples import couples
from handlers.actions import kiss, hug, slap, punch, bite
from handlers.fun_meters import brain, look, stupid_meter, love, crush
from handlers.fun_commands import truth, dare, puzzle, music

# Media / broadcast
from handlers.media import addgif, sticker_reply_handler
from handlers.broadcast import broadcast_start, broadcast_callback
from handlers.own import own

# Owner / admin
from handlers.owner import addpremium, removepremium, setbal, resetbal, ownercommands
from handlers.admin_dot import dot_router
from handlers.admin import (
    warn, unwarn, mute, unmute, ban, unban,
    kick, promote, demote, pin, unpin, delete
)

# Admin commands (open/close economy)
from handlers.admin_commands import open_economy, close_economy

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    asyncio.get_event_loop().run_until_complete(init_db())

    app = Application.builder().token(BOT_TOKEN).build()

    # Silent tracking
    app.add_handler(MessageHandler(filters.ALL, _track_users), group=-10)

    # Dot admin
    app.add_handler(MessageHandler(filters.Regex(r"^\."), dot_router), group=-9)

    # Word listener
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, word_listener),
        group=-8
    )

    # Sticker / GIF replies
    app.add_handler(
        MessageHandler(
            (filters.Sticker.ALL | filters.ANIMATION) & filters.REPLY,
            sticker_reply_handler
        ),
        group=-7
    )

    # Start + Talk To Baka callback
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_callback, pattern="^talk_baka$"))

    # Admin moderation
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))
    app.add_handler(CommandHandler("d", delete))

    # Economy toggle commands
    app.add_handler(CommandHandler("open", open_economy))
    app.add_handler(CommandHandler("close", close_economy))

    # Owner
    app.add_handler(CommandHandler("addpremium", addpremium))
    app.add_handler(CommandHandler("removepremium", removepremium))
    app.add_handler(CommandHandler("ownercommands", ownercommands))
    app.add_handler(CommandHandler("setbal", setbal))
    app.add_handler(CommandHandler("resetbal", resetbal))

    # Economy
    app.add_handler(CommandHandler("bal", bal))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("economy", economy))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("rob", rob))
    app.add_handler(CommandHandler("give", give))
    app.add_handler(CommandHandler("revive", revive))
    app.add_handler(CommandHandler("protect", protect))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("toprich", toprich))
    app.add_handler(CommandHandler("topkill", topkill))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("items", items))
    app.add_handler(CommandHandler("item", item))
    app.add_handler(CommandHandler("gift", gift))

    # Bomb game
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("pass", pass_bomb))
    app.add_handler(CommandHandler("myrank", myrank))
    app.add_handler(CommandHandler("leaders", leaders))

    # Word game
    app.add_handler(CommandHandler("wordgame", wordgame))
    app.add_handler(CommandHandler("enter", enter))
    app.add_handler(CallbackQueryHandler(word_button, pattern="^word:"))

    # Fun / couples
    app.add_handler(CommandHandler("couples", couples))
    app.add_handler(CommandHandler("crush", crush))
    app.add_handler(CommandHandler("love", love))
    app.add_handler(CommandHandler("look", look))
    app.add_handler(CommandHandler("brain", brain))
    app.add_handler(CommandHandler("stupid_meter", stupid_meter))
    app.add_handler(CommandHandler("kiss", kiss))
    app.add_handler(CommandHandler("hug", hug))
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("punch", punch))
    app.add_handler(CommandHandler("bite", bite))

    # Fun commands
    app.add_handler(CommandHandler("truth", truth))
    app.add_handler(CommandHandler("dare", dare))
    app.add_handler(CommandHandler("puzzle", puzzle))
    app.add_handler(CommandHandler("music", music))

    # Media
    app.add_handler(CommandHandler("addgif", addgif))
    app.add_handler(CommandHandler("own", own))

    # Broadcast
    app.add_handler(CommandHandler("broadcast", broadcast_start))
    app.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^bc_"))

    # Other
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("pay", pay))

    # AI chat last
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat),
        group=10
    )

    app.add_error_handler(error_handler)

    logger.info("Bot started")
    app.run_polling()


async def _track_users(update, context):
    from database import ensure_user, ensure_group
    try:
        if update.effective_user and not update.effective_user.is_bot:
            await ensure_user(
                update.effective_user.id,
                update.effective_user.first_name,
                update.effective_user.username
            )
        if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
            await ensure_group(
                update.effective_chat.id,
                update.effective_chat.title
            )
    except Exception:
        pass


def error_handler(update, context):
    logger.error("Update error", exc_info=context.error)


if __name__ == "__main__":
    main()
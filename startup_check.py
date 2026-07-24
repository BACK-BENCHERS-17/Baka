import logging
from config import BOT_TOKEN, GROQ_API_KEY
from telegram import Bot

logger = logging.getLogger(__name__)

async def startup_check():
    """Perform startup checks"""
    logger.info("Performing startup checks...")
    
    # Check bot token
    try:
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        logger.info(f"Bot authenticated as @{me.username}")
    except Exception as e:
        logger.error(f"Failed to authenticate bot: {e}")
        raise
    
    # Check Groq API key (simplified check)
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        logger.warning("Groq API key not configured or using placeholder")
    
    logger.info("Startup checks completed successfully")
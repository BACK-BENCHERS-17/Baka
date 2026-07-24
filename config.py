import os

# Bot Credentials
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = "Ghop_BakaBot"

# Groq AI
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
AI_MODEL = "llama-3.1-8b-instant"

# Owner
OWNER_IDS = {7378164883}

# AI Settings
MAX_MEMORY_MESSAGES = 5
MEMORY_EXPIRY_SECONDS = 900  # 15 minutes
AI_RATE_LIMIT_SECONDS = 1

# Economy Config
DAILY_NORMAL = 1000
DAILY_PREMIUM = 2000
ROB_MAX_NORMAL = 10000
ROB_MAX_PREMIUM = 100000
KILL_REWARD_NORMAL = (100, 200)
KILL_REWARD_PREMIUM = (200, 400)
GIVE_TAX_NORMAL = 0.10
GIVE_TAX_PREMIUM = 0.05
PROTECT_COST = 500  # Free protection
CLAIM_MIN_MEMBERS = 500
CLAIM_PER_MEMBER = 10
REVIVE_COST = 500
DAILY_KILL_LIMIT_NORMAL = 200
DAILY_KILL_LIMIT_PREMIUM = 400
DAILY_ROB_LIMIT_NORMAL = 200
DAILY_ROB_LIMIT_PREMIUM = 400

# Items & Prices
ITEMS = {
    "rose": ("🌹 Rose", 500),
    "chocolate": ("🍫 Chocolate", 800),
    "ring": ("💍 Ring", 2000),
    "teddy": ("🧸 Teddy Bear", 1500),
    "pizza": ("🍕 Pizza", 600),
    "surprise": ("🎁 Surprise Box", 2500),
    "puppy": ("🐶 Puppy", 3000),
    "cake": ("🎂 Cake", 1000),
    "letter": ("💌 Love Letter", 400),
    "cat": ("🐱 Cat", 2500),
}

# Games
BOMB_JOIN_WINDOW = 120  # 2 minutes
BOMB_BLAST_RANGE = (10, 30)  # seconds
WORD_GAME_JOIN_WINDOW = 120  # 2 minutes
WORD_LENGTH = 16

# Couples
COUPLES_COOLDOWN = 300  # 5 minutes

# URLs
PAYMENT_LINK = "https://t.me/xorib"
OWNER_PROFILE = "https://t.me/xorib"  # Replace with actual
FRIENDS_GROUP = "https://t.me/BotXCore"  # Replace with actual
GAMES_GROUP = "https://t.me/BotXCorr"  # Replace with actual

# Database
DB_PATH = "baka.db"

# Premium Notification (seconds)
PREMIUM_NOTIFY_24H = 86400
PREMIUM_NOTIFY_1H = 3600

# Timezone
TIMEZONE = "Asia/Kolkata"

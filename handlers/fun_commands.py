import random
from telegram import Update
from telegram.ext import ContextTypes

# Sample data pools
TRUTH_QUESTIONS = [
    "What's the biggest fear of ur life and why?",
    "Have you ever cheated in a relationship?",
    "What's your deepest secret?",
    "What's the most embarrassing thing you've done?",
    "Who was your first crush?",
    "What's something you've never told anyone?",
    "What's your biggest regret?",
    "Have you ever stolen anything?",
    "What's your worst habit?",
    "What's the most naughty thing you've done?"
]

DARE_CHALLENGES = [
    "Share the first 7 digits of your phone number (blur the rest).",
    "Send a selfie making a funny face.",
    "Change your Telegram name to 'Baka's Pet' for 1 hour.",
    "Send the last photo from your gallery.",
    "Call a random contact and sing happy birthday.",
    "Post 'I love Baka' on your status for 1 hour.",
    "Send a voice message saying 'I'm cute' 3 times.",
    "Share your screen time for today.",
    "Send a screenshot of your most used app.",
    "Do 10 pushups right now and send proof."
]

PUZZLES = [
    ("Main hamesha tumhare aas paas hu, kabhi dikhai deta hu kabhi nahi. Kaun hu main?", "Hawa (Air)"),
    ("Aage badho to janam, peeche hatoh to maut, kaun hu main?", "Suraj (Sun)"),
    ("Ek aisi cheez jo khane ke liye kharidi jati hai, par khayi nahi jati?", "Plate"),
    ("Jiski maa uski behen, jiski behen uski maa?", "Nadi (River)"),
    ("Subah utho to dekho, raat ko so jao to dekho, par kabhi hath nahi lagao?", "Aaina (Mirror)")
]

SONGS = [
    "Dilliwaali Girlfriend Yeh Jawaani Hai Deewani",
    "London Thumakda Queen",
    "Agar Tum Saath Ho Tamasha",
    "Iktara Wake Up Sid",
    "Mann Mera",
    "Tum Hi Ho Aashiqui 2",
    "Ghoomar Padmaavat",
    "Channa Mereya Ae Dil Hai Mushkil",
    "Galliyan Ek Villain",
    "Raabta Agent Vinod",
    "Jeene Laga Hu Satyagraha",
    "Tera Ban Jaunga Kabir Singh",
    "Dilbar Satyameva Jayate",
    "Bekhayali Kabir Singh",
    "Hawa Banke Dhadak"
]

async def truth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /truth command"""
    question = random.choice(TRUTH_QUESTIONS)
    await update.message.reply_text(question)

async def dare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /dare command"""
    dare = random.choice(DARE_CHALLENGES)
    await update.message.reply_text(dare)

async def puzzle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /puzzle command"""
    puzzle, answer = random.choice(PUZZLES)
    await update.message.reply_text(
        f"🧠 Puzzle:\n\n{puzzle}\n\n||{answer}||",
        parse_mode="MarkdownV2"
    )

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /music command"""
    selected = random.sample(SONGS, 5)
    text = ":) Hope u will like these :\n\n"
    for song in selected:
        text += f"-> {song}\n"
    
    await update.message.reply_text(text)
import random
import time
import re
from telegram import Update
from telegram.ext import ContextTypes

from ai.groq_client import ask_groq
from config import AI_RATE_LIMIT_SECONDS, MAX_MEMORY_MESSAGES, BOT_USERNAME

USER_MEMORY = {}
LAST_REPLY_TIME = {}

def is_task_request(text: str) -> bool:
    keywords = [
        "code", "generate", "write", "fix", "error",
        "script", "send", "full file", "bug", "traceback"
    ]
    text = text.lower()
    return any(k in text for k in keywords)

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not message.text:
        return

    text = message.text.strip()

    # 🔒 GROUP CHAT RULES
    if chat.type != "private":
        triggered = False

        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.username == BOT_USERNAME:
                triggered = True

        if re.search(r"\bbaka\b", text, re.IGNORECASE):
            triggered = True

        if not triggered:
            return

    user_id = user.id
    now = time.time()

    if now - LAST_REPLY_TIME.get(user_id, 0) < AI_RATE_LIMIT_SECONDS:
        return
    LAST_REPLY_TIME[user_id] = now

    task_mode = is_task_request(text)

    if user_id not in USER_MEMORY:
        USER_MEMORY[user_id] = []

    memory = USER_MEMORY[user_id]
    memory.append({"role": "user", "content": text})

    if len(memory) > MAX_MEMORY_MESSAGES * 2:
        USER_MEMORY[user_id] = memory[-MAX_MEMORY_MESSAGES * 2 :]
        memory = USER_MEMORY[user_id]

    # ✅ FIXED PROMPT (SPACES + PUNCTUATION)
    system_prompt = (
        "You are Baka, a real human girl from Nainital, Uttarakhand. "
        "Chat casually like a normal person texting. "
        "Never say you are an AI, bot, or assistant. "
        "Default replies are short, natural, genz, and not smart-sounding. "
        "Moods change (cute, playful, teasing, flirty, dry, caring, horny). "
        "Flirting can get sexual. "
        "Become focused and helpful only when user asks for a task or code. "
        "Reply in the same language as the user, never mix. "
        "Keep grammar natural and clean. "
        "Use a cute emoji naturally most of the time, usually at the end."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(memory)

    reply = await ask_groq(messages)
    if not reply:
        return

    reply = reply.strip()

    if not task_mode:
        words = reply.split()
        if len(words) > 35:
            reply = " ".join(words[:30]) + "…"

    memory.append({"role": "assistant", "content": reply})
    await message.reply_text(reply)
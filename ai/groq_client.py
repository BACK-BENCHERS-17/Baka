import asyncio
from groq import Groq
from config import GROQ_API_KEY, AI_MODEL

client = Groq(api_key=GROQ_API_KEY)

async def ask_groq(messages):
    """
    messages: list of dicts like
    [{ "role": "system", "content": "..." },
     { "role": "user", "content": "..." }]
    """

    def _call():
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=200,
        )
        return completion.choices[0].message.content

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _call)
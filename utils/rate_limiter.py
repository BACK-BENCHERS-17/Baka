import time
from collections import defaultdict

# Per-user rate limiting for AI
_last_ai_reply = defaultdict(float)

def check_ai_rate_limit(user_id: int) -> bool:
    """Check if user can get AI response (1 second cooldown)"""
    current_time = time.time()
    last_time = _last_ai_reply.get(user_id, 0)
    
    if current_time - last_time < 1:
        return False
    
    _last_ai_reply[user_id] = current_time
    return True
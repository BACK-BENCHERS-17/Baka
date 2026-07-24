import time
from collections import deque
from config import MAX_MEMORY_MESSAGES, MEMORY_EXPIRY_SECONDS

# user_id -> deque[(role, text, timestamp)]
_MEMORY = {}

def _cleanup(uid: int):
    """Cleanup expired memory for user"""
    now = time.time()
    dq = _MEMORY.get(uid)
    if not dq:
        return

    # Expire by inactivity
    if now - dq[-1][2] > MEMORY_EXPIRY_SECONDS:
        _MEMORY.pop(uid, None)

def add_message(uid: int, role: str, text: str):
    """Add message to user's memory"""
    _cleanup(uid)
    
    dq = _MEMORY.setdefault(uid, deque(maxlen=MAX_MEMORY_MESSAGES))
    dq.append((role, text, time.time()))

def get_context(uid: int):
    """Get conversation context for user"""
    _cleanup(uid)
    dq = _MEMORY.get(uid)
    if not dq:
        return []
    
    return [{"role": r, "content": t} for r, t, _ in dq]
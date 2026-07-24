import aiosqlite
import time
from config import (
    DB_PATH,
    DAILY_ROB_LIMIT_NORMAL,
    DAILY_ROB_LIMIT_PREMIUM,
    DAILY_KILL_LIMIT_NORMAL,
    DAILY_KILL_LIMIT_PREMIUM
)

async def init_db():
    """Initialize all database tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Core tables
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                balance INTEGER DEFAULT 0,
                kills INTEGER DEFAULT 0,
                status TEXT DEFAULT 'alive',
                died_at INTEGER DEFAULT 0,
                last_daily_claim DATE,
                premium_until INTEGER DEFAULT 0,
                notified_24h INTEGER DEFAULT 0,
                notified_1h INTEGER DEFAULT 0,
                created_at INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                title TEXT,
                created_at INTEGER
            )
        """)

        # Items & inventory
        await db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                user_id INTEGER,
                item_name TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_name)
            )
        """)

        # Media storage
        await db.execute("""
            CREATE TABLE IF NOT EXISTS media_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                media_type TEXT,
                file_id TEXT,
                added_by INTEGER,
                added_at INTEGER
            )
        """)

        # Economy settings
        await db.execute("""
            CREATE TABLE IF NOT EXISTS economy_settings (
                group_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1
            )
        """)

        # Claims
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claim_rewards (
                group_id INTEGER PRIMARY KEY,
                claimed_by INTEGER,
                claimed_at INTEGER
            )
        """)

        # Games stats
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bomb_stats (
                user_id INTEGER PRIMARY KEY,
                bomb_wins INTEGER DEFAULT 0,
                bomb_total_won INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS bomb_games (
                group_id INTEGER PRIMARY KEY,
                entry_fee INTEGER,
                started_at INTEGER,
                players TEXT DEFAULT '[]',
                current_holder INTEGER,
                round INTEGER DEFAULT 1
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS wordgame_stats (
                user_id INTEGER PRIMARY KEY,
                wins INTEGER DEFAULT 0,
                total_won INTEGER DEFAULT 0
            )
        """)

        # Daily limits
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_limits (
                user_id INTEGER,
                type TEXT,
                date TEXT,
                count INTEGER,
                PRIMARY KEY (user_id, type, date)
            )
        """)

        # Couples cooldown
        await db.execute("""
            CREATE TABLE IF NOT EXISTS couples_cooldown (
                group_id INTEGER PRIMARY KEY,
                last_couple_ts INTEGER
            )
        """)

        # Protection
        await db.execute("""
            CREATE TABLE IF NOT EXISTS protection (
                user_id INTEGER PRIMARY KEY,
                expires_at INTEGER
            )
        """)

        # Indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_balance ON users(balance)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_kills ON users(kills)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_premium ON users(premium_until)")
        
        await db.commit()

async def ensure_user(user_id: int, first_name: str = "", username: str = ""):
    """Ensure user exists in database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, first_name, username, created_at) 
            VALUES (?, ?, ?, ?)
        """, (user_id, first_name, username, int(time.time())))
        
        if first_name or username:
            await db.execute("""
                UPDATE users SET first_name=COALESCE(?, first_name), username=COALESCE(?, username)
                WHERE user_id=?
            """, (first_name if first_name else None, username if username else None, user_id))
        
        await db.commit()

async def ensure_group(group_id: int, title: str = ""):
    """Ensure group exists in database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO groups (group_id, title, created_at) 
            VALUES (?, ?, ?)
        """, (group_id, title, int(time.time())))
        
        if title:
            await db.execute("UPDATE groups SET title=? WHERE group_id=?", (title, group_id))
        
        await db.commit()

async def get_user(user_id: int):
    """Get user data with auto-revive after 6 hours"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name, balance, kills, status, 
                   died_at, last_daily_claim, premium_until 
            FROM users WHERE user_id=?
        """, (user_id,))
        row = await cursor.fetchone()
        if row:
            # Auto-revive after 6 hours (21600 seconds)
            died_at = row[5] or 0
            current_time = int(time.time())
            
            if row[4] == 'dead' and died_at > 0 and (current_time - died_at) > 21600:
                # Auto-revive the user
                await db.execute("""
                    UPDATE users SET status='alive', died_at=0 WHERE user_id=?
                """, (user_id,))
                await db.commit()
                
                # Return with alive status
                return {
                    'user_id': row[0],
                    'first_name': row[1],
                    'balance': row[2],
                    'kills': row[3],
                    'status': 'alive',  # Updated to alive
                    'died_at': 0,
                    'last_daily_claim': row[6],
                    'premium_until': row[7]
                }
            
            # Return as is (either alive or recently dead)
            return {
                'user_id': row[0],
                'first_name': row[1],
                'balance': row[2],
                'kills': row[3],
                'status': row[4],
                'died_at': died_at,
                'last_daily_claim': row[6],
                'premium_until': row[7]
            }
        return None

async def update_balance(user_id: int, amount: int):
    """Update user balance"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def is_premium(user_id: int):
    """Check if user is premium"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if not row or not row[0]:
            return False
        if row[0] < int(time.time()):
            # Premium expired
            await db.execute("UPDATE users SET premium_until=0 WHERE user_id=?", (user_id,))
            await db.commit()
            return False
        return True

async def add_kill(user_id: int):
    """Increment user's kill count"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET kills=kills+1 WHERE user_id=?", (user_id,))
        await db.commit()

async def set_status(user_id: int, status: str):
    """Set user status (alive/dead) with timestamp"""
    current_time = int(time.time()) if status == 'dead' else 0
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET status=?, died_at=? WHERE user_id=?
        """, (status, current_time, user_id))
        await db.commit()

async def get_global_rank(user_id: int):
    """Get user's global rank by balance"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get user's balance
        cursor = await db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return 0
        
        # Count users with higher balance
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE balance > ?", (row[0],))
        rank = (await cursor.fetchone())[0] + 1
        return rank

async def get_total_users():
    """Get total number of users"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        return (await cursor.fetchone())[0]

async def check_daily_limit(user_id, limit_type, premium):
    from datetime import date
    today = date.today().isoformat()

    # Choose limit based on command type
    if limit_type == "kill":
        max_limit = DAILY_KILL_LIMIT_PREMIUM if premium else DAILY_KILL_LIMIT_NORMAL
    else:
        max_limit = DAILY_ROB_LIMIT_PREMIUM if premium else DAILY_ROB_LIMIT_NORMAL

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT count FROM daily_limits
            WHERE user_id=? AND type=? AND date=?
            """,
            (user_id, limit_type, today)
        )
        row = await cursor.fetchone()

        # Limit reached
        if row and row[0] >= max_limit:
            return False

        # Insert or increment
        await db.execute(
            """
            INSERT INTO daily_limits (user_id, type, date, count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(user_id, type, date)
            DO UPDATE SET count = count + 1
            """,
            (user_id, limit_type, today)
        )
        await db.commit()
        return True

async def get_user_items(user_id: int):
    """Get user's inventory"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT item_name, quantity FROM items WHERE user_id=?", (user_id,))
        return await cursor.fetchall()

async def add_item(user_id: int, item_name: str, quantity: int = 1):
    """Add item to user's inventory"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO items (user_id, item_name, quantity) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_name) DO UPDATE SET quantity=quantity+?
        """, (user_id, item_name, quantity, quantity))
        await db.commit()

async def get_random_media(command: str, media_type: str):
    """Get random media from pool"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT file_id FROM media_pool 
            WHERE command=? AND media_type=? 
            ORDER BY RANDOM() LIMIT 1
        """, (command, media_type))
        row = await cursor.fetchone()
        return row[0] if row else None

async def add_media(command: str, media_type: str, file_id: str, added_by: int):
    """Add media to pool"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO media_pool (command, media_type, file_id, added_by, added_at)
            VALUES (?, ?, ?, ?, ?)
        """, (command, media_type, file_id, added_by, int(time.time())))
        await db.commit()

async def is_group_claimed(group_id: int):
    """Check if group was already claimed"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT claimed_by FROM claim_rewards WHERE group_id=?", (group_id,))
        return await cursor.fetchone() is not None

async def mark_group_claimed(group_id: int, user_id: int):
    """Mark group as claimed"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO claim_rewards (group_id, claimed_by, claimed_at)
            VALUES (?, ?, ?)
        """, (group_id, user_id, int(time.time())))
        await db.commit()

async def get_economy_status(group_id: int):
    """Check if economy is enabled in group"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT enabled FROM economy_settings WHERE group_id=?", (group_id,))
        row = await cursor.fetchone()
        return row[0] if row else 1  # Default enabled

async def set_economy_status(group_id: int, enabled: bool):
    """Enable/disable economy in group"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO economy_settings (group_id, enabled)
            VALUES (?, ?)
        """, (group_id, 1 if enabled else 0))
        await db.commit()

async def get_protection_expiry(user_id: int):
    """Get user's protection expiry"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT expires_at FROM protection WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def set_protection_expiry(user_id: int, expires_at: int):
    """Set user's protection expiry"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO protection (user_id, expires_at)
            VALUES (?, ?)
        """, (user_id, expires_at))
        await db.commit()

async def get_couples_cooldown(group_id: int):
    """Get last couples timestamp for group"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT last_couple_ts FROM couples_cooldown WHERE group_id=?", (group_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def set_couples_cooldown(group_id: int, timestamp: int):
    """Set couples cooldown for group"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO couples_cooldown (group_id, last_couple_ts)
            VALUES (?, ?)
        """, (group_id, timestamp))
        await db.commit()

async def get_bomb_stats(user_id: int):
    """Get bomb game stats for user"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT bomb_wins, bomb_total_won FROM bomb_stats WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return {'wins': row[0], 'total_won': row[1]}
        return None

async def update_bomb_stats(user_id: int, reward: int):
    """Update bomb game stats"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO bomb_stats (user_id, bomb_wins, bomb_total_won)
            VALUES (?, 1, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            bomb_wins=bomb_wins+1, bomb_total_won=bomb_total_won+?
        """, (user_id, reward, reward))
        await db.commit()

async def get_bomb_rank(user_id: int):
    """Get bomb game rank"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get user's total won
        cursor = await db.execute("SELECT bomb_total_won FROM bomb_stats WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return 0
        
        # Count users with higher total won
        cursor = await db.execute("SELECT COUNT(*) FROM bomb_stats WHERE bomb_total_won > ?", (row[0],))
        rank = (await cursor.fetchone())[0] + 1
        
        # Total players
        cursor = await db.execute("SELECT COUNT(*) FROM bomb_stats")
        total = (await cursor.fetchone())[0]
        
        return rank, total

async def get_top_rich(limit: int = 10):
    """Get top richest users"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name, username, balance, premium_until 
            FROM users 
            WHERE balance > 0 
            ORDER BY balance DESC 
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()

async def get_top_kill(limit: int = 10):
    """Get top killers"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name, username, kills, premium_until 
            FROM users 
            WHERE kills > 0 
            ORDER BY kills DESC 
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()

async def get_top_bomb(limit: int = 10):
    """Get top bomb winners"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT bs.user_id, u.first_name, u.username, bs.bomb_total_won
            FROM bomb_stats bs
            LEFT JOIN users u ON bs.user_id = u.user_id
            ORDER BY bs.bomb_total_won DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()

async def add_premium(user_id: int, days: int):
    """Add premium to user"""
    current_time = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        # Get current premium expiry
        cursor = await db.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        
        if row and row[0]:
            # Extend from max(now, current_expiry)
            current_expiry = max(current_time, row[0])
            new_expiry = current_expiry + (days * 86400)
        else:
            # Start from now
            new_expiry = current_time + (days * 86400)
        
        await db.execute("UPDATE users SET premium_until=?, notified_24h=0, notified_1h=0 WHERE user_id=?", 
                        (new_expiry, user_id))
        await db.commit()
        return new_expiry

async def remove_premium(user_id: int):
    """Remove premium from user"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET premium_until=0 WHERE user_id=?", (user_id,))
        await db.commit()

async def get_all_users():
    """Get all user IDs"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def get_all_groups():
    """Get all group IDs"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT group_id FROM groups")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def get_premium_expiring_soon():
    """Get users with premium expiring soon"""
    current_time = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        # 24h notification
        cursor = await db.execute("""
            SELECT user_id, premium_until 
            FROM users 
            WHERE premium_until > ? 
            AND premium_until <= ? 
            AND notified_24h = 0
        """, (current_time, current_time + 86400))
        expiring_24h = await cursor.fetchall()
        
        # 1h notification
        cursor = await db.execute("""
            SELECT user_id, premium_until 
            FROM users 
            WHERE premium_until > ? 
            AND premium_until <= ? 
            AND notified_1h = 0
        """, (current_time, current_time + 3600))
        expiring_1h = await cursor.fetchall()
        
        # Expired
        cursor = await db.execute("""
            SELECT user_id 
            FROM users 
            WHERE premium_until > 0 
            AND premium_until <= ?
        """, (current_time,))
        expired = await cursor.fetchall()
        
        return expiring_24h, expiring_1h, expired

async def mark_notified_24h(user_id: int):
    """Mark 24h notification sent"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET notified_24h=1 WHERE user_id=?", (user_id,))
        await db.commit()

async def mark_notified_1h(user_id: int):
    """Mark 1h notification sent"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET notified_1h=1 WHERE user_id=?", (user_id,))
        await db.commit()
"""
TeleTools - Database Module
SQLite database untuk menyimpan semua data bot.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH
        self._create_tables()

    def _get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _create_tables(self):
        """Buat semua tabel yang dibutuhkan"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Tabel settings per grup
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                antispam_enabled INTEGER DEFAULT 0,
                welcome_enabled INTEGER DEFAULT 1,
                welcome_message TEXT DEFAULT NULL,
                autoreply_enabled INTEGER DEFAULT 0,
                autoreply_message TEXT DEFAULT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabel member yang di-scrape
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_bot INTEGER DEFAULT 0,
                status TEXT DEFAULT 'member',
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, user_id)
            )
        """)

        # Tabel scheduled posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                creator_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                is_sent INTEGER DEFAULT 0,
                is_cancelled INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabel cross-post channels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crosspost_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_title TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(owner_id, channel_id)
            )
        """)

        # Tabel analytics - message tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message_type TEXT DEFAULT 'text',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabel analytics - member joins/leaves
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabel spam tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spam_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message_text TEXT,
                reason TEXT,
                action_taken TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabel auto-reply cooldown tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autoreply_cooldown (
                user_id INTEGER PRIMARY KEY,
                last_reply_at REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    # ============ GROUP SETTINGS ============

    def get_settings(self, chat_id: int) -> dict:
        """Ambil settings untuk sebuah grup"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM group_settings WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)

        # Return default settings
        return {
            "chat_id": chat_id,
            "antispam_enabled": 0,
            "welcome_enabled": 1,
            "welcome_message": None,
            "autoreply_enabled": 0,
            "autoreply_message": None,
        }

    def update_setting(self, chat_id: int, key: str, value):
        """Update satu setting untuk grup"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Upsert
        cursor.execute("""
            INSERT INTO group_settings (chat_id, {key})
            VALUES (?, ?)
            ON CONFLICT(chat_id)
            DO UPDATE SET {key} = ?, updated_at = CURRENT_TIMESTAMP
        """.format(key=key), (chat_id, value, value))

        conn.commit()
        conn.close()

    # ============ MEMBERS ============

    def save_member(self, chat_id: int, user_id: int, username: str,
                    first_name: str, last_name: str, is_bot: bool, status: str):
        """Simpan data member"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO members (chat_id, user_id, username, first_name, last_name, is_bot, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(chat_id, user_id)
            DO UPDATE SET
                username = ?,
                first_name = ?,
                last_name = ?,
                is_bot = ?,
                status = ?,
                scraped_at = CURRENT_TIMESTAMP
        """, (chat_id, user_id, username, first_name, last_name, int(is_bot), status,
              username, first_name, last_name, int(is_bot), status))

        conn.commit()
        conn.close()

    def get_members(self, chat_id: int) -> list:
        """Ambil semua member dari sebuah grup"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE chat_id = ? ORDER BY scraped_at DESC", (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_member_count(self, chat_id: int) -> int:
        """Hitung jumlah member yang tersimpan"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM members WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        conn.close()
        return result["count"]

    # ============ SCHEDULED POSTS ============

    def add_scheduled_post(self, chat_id: int, creator_id: int,
                           message_text: str, scheduled_time: str) -> int:
        """Tambah jadwal posting baru"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO scheduled_posts (chat_id, creator_id, message_text, scheduled_time)
            VALUES (?, ?, ?, ?)
        """, (chat_id, creator_id, message_text, scheduled_time))

        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return post_id

    def get_pending_posts(self, chat_id: int = None) -> list:
        """Ambil semua posting yang belum terkirim"""
        conn = self._get_conn()
        cursor = conn.cursor()

        if chat_id:
            cursor.execute("""
                SELECT * FROM scheduled_posts
                WHERE chat_id = ? AND is_sent = 0 AND is_cancelled = 0
                ORDER BY scheduled_time ASC
            """, (chat_id,))
        else:
            cursor.execute("""
                SELECT * FROM scheduled_posts
                WHERE is_sent = 0 AND is_cancelled = 0
                ORDER BY scheduled_time ASC
            """)

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_post_sent(self, post_id: int):
        """Tandai posting sudah terkirim"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE scheduled_posts SET is_sent = 1 WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()

    def cancel_post(self, post_id: int, creator_id: int) -> bool:
        """Batalkan jadwal posting"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scheduled_posts SET is_cancelled = 1
            WHERE id = ? AND creator_id = ? AND is_sent = 0
        """, (post_id, creator_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    # ============ CROSS-POST CHANNELS ============

    def add_crosspost_channel(self, owner_id: int, channel_id: int, channel_title: str = None) -> bool:
        """Tambah channel untuk cross-post"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO crosspost_channels (owner_id, channel_id, channel_title)
                VALUES (?, ?, ?)
            """, (owner_id, channel_id, channel_title))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def remove_crosspost_channel(self, owner_id: int, channel_id: int) -> bool:
        """Hapus channel dari cross-post"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM crosspost_channels WHERE owner_id = ? AND channel_id = ?
        """, (owner_id, channel_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def get_crosspost_channels(self, owner_id: int) -> list:
        """Ambil daftar channel untuk cross-post"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM crosspost_channels WHERE owner_id = ? ORDER BY added_at DESC
        """, (owner_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ============ ANALYTICS ============

    def log_message(self, chat_id: int, user_id: int, message_type: str = "text"):
        """Log pesan untuk analytics"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO message_analytics (chat_id, user_id, message_type)
            VALUES (?, ?, ?)
        """, (chat_id, user_id, message_type))
        conn.commit()
        conn.close()

    def log_member_event(self, chat_id: int, user_id: int, event_type: str):
        """Log event member (join/leave)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO member_events (chat_id, user_id, event_type)
            VALUES (?, ?, ?)
        """, (chat_id, user_id, event_type))
        conn.commit()
        conn.close()

    def get_message_stats(self, chat_id: int, days: int = 1) -> dict:
        """Ambil statistik pesan"""
        conn = self._get_conn()
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).isoformat()

        # Total messages
        cursor.execute("""
            SELECT COUNT(*) as total FROM message_analytics
            WHERE chat_id = ? AND timestamp >= ?
        """, (chat_id, since))
        total = cursor.fetchone()["total"]

        # Unique users
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as unique_users FROM message_analytics
            WHERE chat_id = ? AND timestamp >= ?
        """, (chat_id, since))
        unique_users = cursor.fetchone()["unique_users"]

        # Message types breakdown
        cursor.execute("""
            SELECT message_type, COUNT(*) as count FROM message_analytics
            WHERE chat_id = ? AND timestamp >= ?
            GROUP BY message_type
        """, (chat_id, since))
        types = {row["message_type"]: row["count"] for row in cursor.fetchall()}

        # Joins/Leaves
        cursor.execute("""
            SELECT event_type, COUNT(*) as count FROM member_events
            WHERE chat_id = ? AND timestamp >= ?
            GROUP BY event_type
        """, (chat_id, since))
        events = {row["event_type"]: row["count"] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_messages": total,
            "unique_users": unique_users,
            "message_types": types,
            "joins": events.get("join", 0),
            "leaves": events.get("leave", 0),
            "period_days": days,
        }

    def get_top_users(self, chat_id: int, days: int = 7, limit: int = 10) -> list:
        """Ambil user paling aktif"""
        conn = self._get_conn()
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT user_id, COUNT(*) as message_count
            FROM message_analytics
            WHERE chat_id = ? AND timestamp >= ?
            GROUP BY user_id
            ORDER BY message_count DESC
            LIMIT ?
        """, (chat_id, since, limit))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ============ SPAM ============

    def log_spam(self, chat_id: int, user_id: int, message_text: str,
                 reason: str, action_taken: str):
        """Log spam yang terdeteksi"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO spam_log (chat_id, user_id, message_text, reason, action_taken)
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, user_id, message_text, reason, action_taken))
        conn.commit()
        conn.close()

    def get_user_message_count_recent(self, chat_id: int, user_id: int, seconds: int = 60) -> int:
        """Hitung pesan user dalam X detik terakhir (untuk flood detection)"""
        conn = self._get_conn()
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(seconds=seconds)).isoformat()

        cursor.execute("""
            SELECT COUNT(*) as count FROM message_analytics
            WHERE chat_id = ? AND user_id = ? AND timestamp >= ?
        """, (chat_id, user_id, since))

        result = cursor.fetchone()["count"]
        conn.close()
        return result

    # ============ AUTO-REPLY COOLDOWN ============

    def check_autoreply_cooldown(self, user_id: int, cooldown_seconds: int) -> bool:
        """Cek apakah masih dalam cooldown. Return True jika bisa reply."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT last_reply_at FROM autoreply_cooldown WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row is None:
            conn.close()
            return True

        elapsed = time.time() - row["last_reply_at"]
        conn.close()
        return elapsed >= cooldown_seconds

    def set_autoreply_cooldown(self, user_id: int):
        """Set timestamp cooldown auto-reply"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO autoreply_cooldown (user_id, last_reply_at)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET last_reply_at = ?
        """, (user_id, time.time(), time.time()))
        conn.commit()
        conn.close()

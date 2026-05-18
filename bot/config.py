"""
TeleTools - Configuration
Simpan semua konfigurasi bot di sini.
"""

import os

# Telegram Bot Token (dari @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Telegram API credentials (dari https://my.telegram.org)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH_HERE")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "teletools.db")

# Anti-Spam Settings
SPAM_KEYWORDS = [
    "join now", "free money", "click here", "earn money",
    "bitcoin free", "giveaway", "promo code", "invest now",
    "hubungi kami", "wa.me", "bit.ly", "t.me/joinchat"
]
SPAM_MAX_MESSAGES_PER_MINUTE = 5  # Max pesan per menit per user
SPAM_MAX_LINKS_PER_MESSAGE = 3   # Max link per pesan
SPAM_ACTION = "mute"  # "mute", "kick", "ban", "delete"
SPAM_MUTE_DURATION = 60 * 60     # 1 jam dalam detik

# Welcome Settings
WELCOME_MESSAGE = """
🎉 Selamat datang di grup, {mention}!

Silakan baca rules dan jangan sungkan bertanya.
Semoga betah di sini! 🙌
"""

# Auto-Reply Settings
AUTO_REPLY_ENABLED = True
AUTO_REPLY_MESSAGE = "Halo! Saya sedang sibuk, akan balas nanti. 🙏"
AUTO_REPLY_COOLDOWN = 300  # 5 menit cooldown per user

# Auto-Poster Settings
POSTER_TIMEZONE = "Asia/Jakarta"

# Analytics Settings
ANALYTICS_TRACK_MESSAGES = True
ANALYTICS_TRACK_JOINS = True
ANALYTICS_TRACK_LEAVES = True

# Admin User IDs (Telegram user ID)
ADMIN_IDS = [
    # Tambahkan user ID admin di sini
    # Contoh: 123456789,
]

# Logging
LOG_LEVEL = "INFO"

"""
TeleTools - Configuration
Semua konfigurasi diambil dari file .env
"""

import os
from pathlib import Path

# Load .env file jika ada
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

# ===========================================
# 🔑 WAJIB
# ===========================================

# Telegram Bot Token (dari @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Telegram API credentials (dari https://my.telegram.org)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Admin User IDs
_admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_str.split(",") if x.strip().isdigit()]

# ===========================================
# 💾 DATABASE
# ===========================================

DATABASE_PATH = os.getenv("DATABASE_PATH", "teletools.db")

# ===========================================
# 🛡 ANTI-SPAM
# ===========================================

SPAM_KEYWORDS = [
    "join now", "free money", "click here", "earn money",
    "bitcoin free", "giveaway", "promo code", "invest now",
    "hubungi kami", "wa.me", "bit.ly", "t.me/joinchat"
]
SPAM_MAX_MESSAGES_PER_MINUTE = int(os.getenv("SPAM_MAX_MESSAGES", "5"))
SPAM_MAX_LINKS_PER_MESSAGE = int(os.getenv("SPAM_MAX_LINKS", "3"))
SPAM_ACTION = os.getenv("SPAM_ACTION", "mute")
SPAM_MUTE_DURATION = int(os.getenv("SPAM_MUTE_DURATION", "3600"))

# ===========================================
# 👋 WELCOME
# ===========================================

WELCOME_MESSAGE = """
🎉 Selamat datang di grup, {mention}!

Silakan baca rules dan jangan sungkan bertanya.
Semoga betah di sini! 🙌
"""

# ===========================================
# 💬 AUTO-REPLY
# ===========================================

AUTO_REPLY_ENABLED = True
AUTO_REPLY_MESSAGE = "Halo! Saya sedang sibuk, akan balas nanti. 🙏"
AUTO_REPLY_COOLDOWN = 300  # 5 menit cooldown per user

# ===========================================
# 🔐 CAPTCHA
# ===========================================

CAPTCHA_TYPE = os.getenv("CAPTCHA_TYPE", "math")
CAPTCHA_TIMEOUT = int(os.getenv("CAPTCHA_TIMEOUT", "120"))

# ===========================================
# 🔒 FORCED JOIN
# ===========================================

FORCEJOIN_ENABLED = False

# ===========================================
# ⏰ AUTO-POSTER
# ===========================================

POSTER_TIMEZONE = os.getenv("POSTER_TIMEZONE", "Asia/Jakarta")

# ===========================================
# 📊 ANALYTICS
# ===========================================

ANALYTICS_TRACK_MESSAGES = True
ANALYTICS_TRACK_JOINS = True
ANALYTICS_TRACK_LEAVES = True

# ===========================================
# 📝 LOGGING
# ===========================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

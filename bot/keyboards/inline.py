"""
TeleTools - Inline Keyboards
Menu dan tombol interaktif untuk bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard():
    """Keyboard utama di /start"""
    keyboard = [
        [
            InlineKeyboardButton("🛡 Anti-Spam", callback_data="menu_antispam"),
            InlineKeyboardButton("👋 Welcome", callback_data="menu_welcome"),
        ],
        [
            InlineKeyboardButton("📋 Scraper", callback_data="menu_scraper"),
            InlineKeyboardButton("💬 Auto-Reply", callback_data="menu_autoreply"),
        ],
        [
            InlineKeyboardButton("📮 Auto-Poster", callback_data="menu_autoposter"),
            InlineKeyboardButton("📡 Cross-Post", callback_data="menu_crosspost"),
        ],
        [
            InlineKeyboardButton("📊 Analytics", callback_data="menu_analytics"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def antispam_keyboard(enabled: bool):
    """Keyboard pengaturan anti-spam"""
    status = "✅ ON" if enabled else "❌ OFF"
    keyboard = [
        [
            InlineKeyboardButton(f"Status: {status}", callback_data="antispam_toggle"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="menu_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_keyboard(action: str):
    """Keyboard konfirmasi"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ Tidak", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def export_keyboard():
    """Keyboard pilihan export format"""
    keyboard = [
        [
            InlineKeyboardButton("📄 CSV", callback_data="export_csv"),
            InlineKeyboardButton("📋 JSON", callback_data="export_json"),
            InlineKeyboardButton("📝 TXT", callback_data="export_txt"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

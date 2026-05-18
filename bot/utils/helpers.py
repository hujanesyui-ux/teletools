"""
TeleTools - Helper Utilities
Fungsi-fungsi helper yang dipakai di seluruh bot.
"""

import re
from datetime import datetime


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def truncate(text: str, max_length: int = 100) -> str:
    """Potong teks jika terlalu panjang"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_number(num: int) -> str:
    """Format angka dengan separator (1000 -> 1,000)"""
    return f"{num:,}"


def time_ago(timestamp: str) -> str:
    """Konversi timestamp ke format 'X waktu lalu'"""
    try:
        dt = datetime.fromisoformat(timestamp)
        diff = datetime.now() - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "Baru saja"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} menit lalu"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} jam lalu"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days} hari lalu"
        else:
            return dt.strftime("%d %b %Y")
    except Exception:
        return timestamp


def is_valid_url(text: str) -> bool:
    """Cek apakah teks adalah URL yang valid"""
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(text))


def parse_duration(text: str) -> int:
    """Parse durasi dari teks (misal: '5m', '2h', '1d') ke detik"""
    match = re.match(r'^(\d+)([smhd])$', text.lower())
    if not match:
        return 0

    value = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }

    return value * multipliers.get(unit, 0)


def mention_html(user_id: int, name: str) -> str:
    """Buat HTML mention link untuk user"""
    return f'<a href="tg://user?id={user_id}">{escape_html(name)}</a>'


def progress_bar(current: int, total: int, length: int = 10) -> str:
    """Buat progress bar visual"""
    if total == 0:
        return "░" * length

    filled = int(length * current / total)
    empty = length - filled
    return "▓" * filled + "░" * empty

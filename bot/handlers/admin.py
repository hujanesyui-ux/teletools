"""
TeleTools - Admin Decorator
Pembatasan akses hanya untuk admin.
"""

from functools import wraps
from telegram import Update
from config import ADMIN_IDS


def admin_only(func):
    """Decorator untuk membatasi command hanya untuk admin"""
    @wraps(func)
    async def wrapper(self, update: Update, context, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        # Cek apakah user adalah admin bot (dari config)
        if user.id in ADMIN_IDS:
            return await func(self, update, context, *args, **kwargs)

        # Cek apakah user adalah admin grup
        if chat.type in ["group", "supergroup"]:
            member = await chat.get_member(user.id)
            if member.status in ["administrator", "creator"]:
                return await func(self, update, context, *args, **kwargs)

        await update.message.reply_html(
            "⛔ Kamu tidak memiliki akses untuk perintah ini.\n"
            "Hanya admin yang bisa menggunakan fitur ini."
        )
        return None

    return wrapper

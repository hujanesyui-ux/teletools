"""
TeleTools - Auto-Reply Handler
Balas pesan otomatis di akun pribadi/DM bot.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import admin_only
from config import AUTO_REPLY_MESSAGE, AUTO_REPLY_COOLDOWN

logger = logging.getLogger(__name__)


class AutoReplyHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /autoreply command"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        args = context.args

        if not args:
            settings = self.db.get_settings(chat_id)
            status = "✅ Aktif" if settings["autoreply_enabled"] else "❌ Nonaktif"
            current_msg = settings["autoreply_message"] or AUTO_REPLY_MESSAGE
            text = (
                f"💬 <b>Auto-Reply Settings</b>\n\n"
                f"Status: {status}\n"
                f"Cooldown: {AUTO_REPLY_COOLDOWN // 60} menit per user\n\n"
                f"Pesan saat ini:\n"
                f"<blockquote>{current_msg}</blockquote>\n\n"
                f"Gunakan:\n"
                f"/autoreply on - Aktifkan\n"
                f"/autoreply off - Nonaktifkan\n"
                f"/setreply [teks] - Atur pesan"
            )
            await update.message.reply_html(text)
            return

        action = args[0].lower()

        if action == "on":
            self.db.update_setting(chat_id, "autoreply_enabled", 1)
            await update.message.reply_html("💬 Auto-reply <b>diaktifkan</b>! ✅")
        elif action == "off":
            self.db.update_setting(chat_id, "autoreply_enabled", 0)
            await update.message.reply_html("💬 Auto-reply <b>dinonaktifkan</b>. ❌")
        else:
            await update.message.reply_html(
                "⚠️ Penggunaan: /autoreply [on|off]\n"
                "Untuk atur pesan: /setreply [teks]"
            )

    @admin_only
    async def set_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /setreply command"""
        chat_id = update.effective_chat.id

        if not context.args:
            await update.message.reply_html(
                "⚠️ Penggunaan: /setreply [teks]\n\n"
                "Contoh:\n"
                "<code>/setreply Halo! Saya sedang offline, akan balas segera.</code>"
            )
            return

        new_message = update.message.text.split(None, 1)[1]
        self.db.update_setting(chat_id, "autoreply_message", new_message)

        await update.message.reply_html(
            f"✅ Auto-reply message berhasil diupdate!\n\n"
            f"Preview:\n<blockquote>{new_message}</blockquote>"
        )

    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pesan private & kirim auto-reply"""
        if not update.message or not update.effective_user:
            return

        user_id = update.effective_user.id

        # Gunakan chat_id 0 untuk settings global auto-reply
        # atau bisa di-set per user/admin
        settings = self.db.get_settings(0)  # Global settings

        if not settings["autoreply_enabled"]:
            return

        # Cek cooldown supaya tidak spam reply
        can_reply = self.db.check_autoreply_cooldown(user_id, AUTO_REPLY_COOLDOWN)
        if not can_reply:
            return

        # Kirim auto-reply
        reply_message = settings["autoreply_message"] or AUTO_REPLY_MESSAGE

        try:
            await update.message.reply_html(reply_message)
            self.db.set_autoreply_cooldown(user_id)
            logger.info(f"Auto-reply sent to user {user_id}")
        except Exception as e:
            logger.error(f"Gagal kirim auto-reply: {e}")

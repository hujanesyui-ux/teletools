"""
TeleTools - Welcome Handler
Sambut member baru secara otomatis.
"""

import logging
from telegram import Update, ChatMemberUpdated
from telegram.ext import ContextTypes

from handlers.admin import admin_only
from config import WELCOME_MESSAGE

logger = logging.getLogger(__name__)


class WelcomeHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /welcome command"""
        chat_id = update.effective_chat.id
        args = context.args

        if not args:
            settings = self.db.get_settings(chat_id)
            status = "✅ Aktif" if settings["welcome_enabled"] else "❌ Nonaktif"
            current_msg = settings["welcome_message"] or WELCOME_MESSAGE
            text = (
                f"👋 <b>Welcome Settings</b>\n\n"
                f"Status: {status}\n\n"
                f"Pesan saat ini:\n"
                f"<blockquote>{current_msg}</blockquote>\n\n"
                f"Variabel yang tersedia:\n"
                f"<code>{{mention}}</code> - Mention user\n"
                f"<code>{{name}}</code> - Nama user\n"
                f"<code>{{username}}</code> - Username\n"
                f"<code>{{chat_title}}</code> - Nama grup\n"
                f"<code>{{member_count}}</code> - Jumlah member\n\n"
                f"Gunakan:\n"
                f"/welcome on - Aktifkan\n"
                f"/welcome off - Nonaktifkan\n"
                f"/setwelcome [teks] - Atur pesan"
            )
            await update.message.reply_html(text)
            return

        action = args[0].lower()

        if action == "on":
            self.db.update_setting(chat_id, "welcome_enabled", 1)
            await update.message.reply_html("👋 Welcome message <b>diaktifkan</b>! ✅")
        elif action == "off":
            self.db.update_setting(chat_id, "welcome_enabled", 0)
            await update.message.reply_html("👋 Welcome message <b>dinonaktifkan</b>. ❌")
        else:
            await update.message.reply_html(
                "⚠️ Penggunaan: /welcome [on|off]\n"
                "Untuk atur pesan: /setwelcome [teks]"
            )

    @admin_only
    async def set_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /setwelcome command"""
        chat_id = update.effective_chat.id

        if not context.args:
            await update.message.reply_html(
                "⚠️ Penggunaan: /setwelcome [teks]\n\n"
                "Contoh:\n"
                "<code>/setwelcome Halo {mention}! Selamat datang di {chat_title}!</code>\n\n"
                "Variabel:\n"
                "<code>{mention}</code> - Mention user\n"
                "<code>{name}</code> - Nama depan\n"
                "<code>{username}</code> - Username\n"
                "<code>{chat_title}</code> - Nama grup\n"
                "<code>{member_count}</code> - Jumlah member"
            )
            return

        # Ambil teks setelah command
        new_message = update.message.text.split(None, 1)[1]
        self.db.update_setting(chat_id, "welcome_message", new_message)

        await update.message.reply_html(
            f"✅ Welcome message berhasil diupdate!\n\n"
            f"Preview:\n<blockquote>{new_message}</blockquote>"
        )

    async def greet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sambut member baru yang join"""
        # Cek apakah ini event member baru join
        result = self._extract_status_change(update.chat_member)
        if result is None:
            return

        was_member, is_member = result

        # Hanya proses jika user baru join
        if not was_member and is_member:
            chat = update.effective_chat
            new_member = update.chat_member.new_chat_member.user

            # Cek apakah welcome aktif
            settings = self.db.get_settings(chat.id)
            if not settings["welcome_enabled"]:
                return

            # Ambil pesan welcome
            welcome_text = settings["welcome_message"] or WELCOME_MESSAGE

            # Get member count
            try:
                member_count = await chat.get_member_count()
            except Exception:
                member_count = "?"

            # Format pesan
            formatted_message = welcome_text.format(
                mention=new_member.mention_html(),
                name=new_member.first_name or "User",
                username=f"@{new_member.username}" if new_member.username else "No username",
                chat_title=chat.title or "Grup",
                member_count=member_count,
            )

            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=formatted_message,
                    parse_mode="HTML",
                )
                logger.info(f"Welcome sent for {new_member.id} in {chat.id}")
            except Exception as e:
                logger.error(f"Gagal kirim welcome: {e}")

    def _extract_status_change(self, chat_member_update: ChatMemberUpdated):
        """Extract apakah user baru join atau leave"""
        status_change = chat_member_update.difference().get("status")

        if status_change is None:
            return None

        old_status, new_status = status_change

        was_member = old_status in [
            "member", "administrator", "creator", "restricted"
        ]
        is_member = new_status in [
            "member", "administrator", "creator", "restricted"
        ]

        return was_member, is_member

"""
TeleTools - Anti-Spam Handler
Filter spam otomatis di grup.
"""

import re
import logging
from datetime import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from handlers.admin import admin_only
from config import (
    SPAM_KEYWORDS,
    SPAM_MAX_MESSAGES_PER_MINUTE,
    SPAM_MAX_LINKS_PER_MESSAGE,
    SPAM_ACTION,
    SPAM_MUTE_DURATION,
)

logger = logging.getLogger(__name__)

# Regex untuk mendeteksi link
URL_REGEX = re.compile(
    r'(https?://\S+|www\.\S+|t\.me/\S+|bit\.ly/\S+|wa\.me/\S+)', re.IGNORECASE
)

# Regex untuk forward dari channel
FORWARD_PATTERN = re.compile(r'(join|subscribe|channel|grup|group)', re.IGNORECASE)


class AntiSpamHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /antispam command"""
        chat_id = update.effective_chat.id
        args = context.args

        if not args:
            settings = self.db.get_settings(chat_id)
            status = "✅ Aktif" if settings["antispam_enabled"] else "❌ Nonaktif"
            text = (
                f"🛡 <b>Anti-Spam Settings</b>\n\n"
                f"Status: {status}\n"
                f"Max pesan/menit: {SPAM_MAX_MESSAGES_PER_MINUTE}\n"
                f"Max link/pesan: {SPAM_MAX_LINKS_PER_MESSAGE}\n"
                f"Aksi: {SPAM_ACTION}\n\n"
                f"Gunakan:\n"
                f"/antispam on - Aktifkan\n"
                f"/antispam off - Nonaktifkan"
            )
            await update.message.reply_html(text)
            return

        action = args[0].lower()

        if action == "on":
            self.db.update_setting(chat_id, "antispam_enabled", 1)
            await update.message.reply_html("🛡 Anti-spam <b>diaktifkan</b>! ✅")
        elif action == "off":
            self.db.update_setting(chat_id, "antispam_enabled", 0)
            await update.message.reply_html("🛡 Anti-spam <b>dinonaktifkan</b>. ❌")
        elif action == "settings":
            settings = self.db.get_settings(chat_id)
            status = "✅ Aktif" if settings["antispam_enabled"] else "❌ Nonaktif"
            text = (
                f"🛡 <b>Anti-Spam Settings</b>\n\n"
                f"Status: {status}\n"
                f"Keywords terblokir: {len(SPAM_KEYWORDS)}\n"
                f"Max pesan/menit: {SPAM_MAX_MESSAGES_PER_MINUTE}\n"
                f"Max link/pesan: {SPAM_MAX_LINKS_PER_MESSAGE}\n"
                f"Aksi spam: <code>{SPAM_ACTION}</code>\n"
                f"Durasi mute: {SPAM_MUTE_DURATION // 60} menit"
            )
            await update.message.reply_html(text)
        else:
            await update.message.reply_html(
                "⚠️ Penggunaan: /antispam [on|off|settings]"
            )

    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cek setiap pesan untuk spam"""
        if not update.message or not update.message.text:
            return

        chat_id = update.effective_chat.id
        user = update.effective_user
        message = update.message

        # Cek apakah anti-spam aktif
        settings = self.db.get_settings(chat_id)
        if not settings["antispam_enabled"]:
            return

        # Skip admin/creator
        try:
            member = await update.effective_chat.get_member(user.id)
            if member.status in ["administrator", "creator"]:
                return
        except Exception:
            pass

        # Jalankan semua pengecekan spam
        spam_reason = await self._detect_spam(chat_id, user.id, message.text)

        if spam_reason:
            await self._take_action(update, context, spam_reason)

    async def _detect_spam(self, chat_id: int, user_id: int, text: str) -> str:
        """Deteksi spam, return reason jika spam, None jika bukan"""

        # 1. Cek keyword spam
        text_lower = text.lower()
        for keyword in SPAM_KEYWORDS:
            if keyword.lower() in text_lower:
                return f"Keyword terdeteksi: '{keyword}'"

        # 2. Cek terlalu banyak link
        links = URL_REGEX.findall(text)
        if len(links) > SPAM_MAX_LINKS_PER_MESSAGE:
            return f"Terlalu banyak link ({len(links)} links)"

        # 3. Cek flood (terlalu banyak pesan dalam waktu singkat)
        recent_count = self.db.get_user_message_count_recent(chat_id, user_id, seconds=60)
        if recent_count >= SPAM_MAX_MESSAGES_PER_MINUTE:
            return f"Flood detected ({recent_count} pesan/menit)"

        # 4. Cek pesan terlalu panjang (biasanya copy-paste spam)
        if len(text) > 4000:
            return "Pesan terlalu panjang (kemungkinan spam)"

        # 5. Cek karakter berulang (misal: "aaaaaaa" atau "!!!!!!")
        if self._has_repetitive_chars(text):
            return "Karakter berulang berlebihan"

        # 6. Cek forward spam (mengandung keyword promosi)
        if links and FORWARD_PATTERN.search(text):
            return "Promosi channel/grup terdeteksi"

        return None

    def _has_repetitive_chars(self, text: str) -> bool:
        """Deteksi karakter yang berulang berlebihan"""
        if len(text) < 10:
            return False

        # Cek apakah ada karakter yang berulang > 10 kali berturut-turut
        repeat_pattern = re.compile(r'(.)\1{9,}')
        return bool(repeat_pattern.search(text))

    async def _take_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
        """Ambil tindakan terhadap spam"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        message = update.message

        # Log spam
        self.db.log_spam(
            chat_id=chat_id,
            user_id=user.id,
            message_text=message.text[:500],  # Max 500 char
            reason=reason,
            action_taken=SPAM_ACTION,
        )

        # Hapus pesan spam
        try:
            await message.delete()
        except Exception as e:
            logger.error(f"Gagal hapus pesan: {e}")

        # Ambil tindakan sesuai config
        try:
            if SPAM_ACTION == "mute":
                await self._mute_user(update, context)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🛡 <b>Spam terdeteksi!</b>\n"
                         f"User: {user.mention_html()}\n"
                         f"Alasan: {reason}\n"
                         f"Aksi: Mute {SPAM_MUTE_DURATION // 60} menit",
                    parse_mode="HTML",
                )

            elif SPAM_ACTION == "kick":
                await update.effective_chat.ban_member(user.id)
                await update.effective_chat.unban_member(user.id)  # Unban supaya bisa join lagi
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🛡 <b>Spam terdeteksi!</b>\n"
                         f"User: {user.mention_html()}\n"
                         f"Alasan: {reason}\n"
                         f"Aksi: Kicked",
                    parse_mode="HTML",
                )

            elif SPAM_ACTION == "ban":
                await update.effective_chat.ban_member(user.id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🛡 <b>Spam terdeteksi!</b>\n"
                         f"User: {user.mention_html()}\n"
                         f"Alasan: {reason}\n"
                         f"Aksi: Banned",
                    parse_mode="HTML",
                )

            elif SPAM_ACTION == "delete":
                # Pesan sudah dihapus di atas
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🛡 Pesan spam dari {user.mention_html()} dihapus.\n"
                         f"Alasan: {reason}",
                    parse_mode="HTML",
                )

        except Exception as e:
            logger.error(f"Gagal mengambil tindakan anti-spam: {e}")

    async def _mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mute user untuk durasi tertentu"""
        from datetime import timedelta

        until_date = datetime.now() + timedelta(seconds=SPAM_MUTE_DURATION)
        permissions = ChatPermissions(can_send_messages=False)

        await update.effective_chat.restrict_member(
            user_id=update.effective_user.id,
            permissions=permissions,
            until_date=until_date,
        )

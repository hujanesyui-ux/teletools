"""
TeleTools - Settings Handler
Full settings management langsung dari Telegram.
Admin bisa atur semua fitur tanpa edit file config.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

from handlers.admin import admin_only

logger = logging.getLogger(__name__)

# Conversation states
WAITING_INPUT = 1


class SettingsHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /settings - Menu utama pengaturan"""
        chat_id = update.effective_chat.id
        settings = self.db.get_settings(chat_id)

        # Status tiap fitur
        antispam_status = "✅" if settings["antispam_enabled"] else "❌"
        welcome_status = "✅" if settings["welcome_enabled"] else "❌"
        autoreply_status = "✅" if settings["autoreply_enabled"] else "❌"

        text = (
            "⚙️ <b>SETTINGS - TeleTools Bot</b>\n\n"
            "Klik tombol di bawah untuk mengatur fitur:\n\n"
            f"🛡 Anti-Spam: {antispam_status}\n"
            f"👋 Welcome: {welcome_status}\n"
            f"💬 Auto-Reply: {autoreply_status}\n"
            f"📮 Auto-Poster: ✅\n"
            f"📡 Cross-Post: ✅\n"
            f"📊 Analytics: ✅\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(f"🛡 Anti-Spam {antispam_status}", callback_data="set_antispam"),
                InlineKeyboardButton(f"👋 Welcome {welcome_status}", callback_data="set_welcome"),
            ],
            [
                InlineKeyboardButton(f"💬 Auto-Reply {autoreply_status}", callback_data="set_autoreply"),
                InlineKeyboardButton("📮 Auto-Poster", callback_data="set_autoposter"),
            ],
            [
                InlineKeyboardButton("📡 Cross-Post", callback_data="set_crosspost"),
                InlineKeyboardButton("📊 Analytics", callback_data="set_analytics"),
            ],
            [
                InlineKeyboardButton("🔑 Spam Keywords", callback_data="set_spam_keywords"),
                InlineKeyboardButton("⚡ Spam Action", callback_data="set_spam_action"),
            ],
            [
                InlineKeyboardButton("📝 Lihat Semua Config", callback_data="set_viewall"),
            ],
        ]

        await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle semua callback dari settings menu"""
        query = update.callback_query
        await query.answer()

        data = query.data
        chat_id = update.effective_chat.id
        settings = self.db.get_settings(chat_id)

        if data == "set_antispam":
            await self._antispam_menu(query, settings)
        elif data == "set_welcome":
            await self._welcome_menu(query, settings)
        elif data == "set_autoreply":
            await self._autoreply_menu(query, settings)
        elif data == "set_autoposter":
            await self._autoposter_menu(query)
        elif data == "set_crosspost":
            await self._crosspost_menu(query)
        elif data == "set_analytics":
            await self._analytics_menu(query)
        elif data == "set_spam_keywords":
            await self._spam_keywords_menu(query)
        elif data == "set_spam_action":
            await self._spam_action_menu(query, settings)
        elif data == "set_viewall":
            await self._view_all_config(query, settings)

        # Toggle actions
        elif data == "toggle_antispam":
            new_val = 0 if settings["antispam_enabled"] else 1
            self.db.update_setting(chat_id, "antispam_enabled", new_val)
            status = "✅ Aktif" if new_val else "❌ Nonaktif"
            await query.message.reply_html(f"🛡 Anti-Spam sekarang: <b>{status}</b>")
        elif data == "toggle_welcome":
            new_val = 0 if settings["welcome_enabled"] else 1
            self.db.update_setting(chat_id, "welcome_enabled", new_val)
            status = "✅ Aktif" if new_val else "❌ Nonaktif"
            await query.message.reply_html(f"👋 Welcome sekarang: <b>{status}</b>")
        elif data == "toggle_autoreply":
            new_val = 0 if settings["autoreply_enabled"] else 1
            self.db.update_setting(chat_id, "autoreply_enabled", new_val)
            status = "✅ Aktif" if new_val else "❌ Nonaktif"
            await query.message.reply_html(f"💬 Auto-Reply sekarang: <b>{status}</b>")

        # Spam action choices
        elif data.startswith("action_"):
            action = data.replace("action_", "")
            self.db.update_setting(chat_id, "spam_action", action)
            await query.message.reply_html(f"⚡ Spam action diubah ke: <b>{action}</b>")

        elif data == "set_back":
            # Kembali ke menu utama
            await query.message.reply_html("Gunakan /settings untuk kembali ke menu utama.")

    async def _antispam_menu(self, query, settings):
        """Menu pengaturan anti-spam"""
        status = "✅ Aktif" if settings["antispam_enabled"] else "❌ Nonaktif"
        toggle_text = "❌ Nonaktifkan" if settings["antispam_enabled"] else "✅ Aktifkan"

        text = (
            f"🛡 <b>Anti-Spam Settings</b>\n\n"
            f"Status: {status}\n\n"
            f"<b>Pengaturan saat ini:</b>\n"
            f"• Max pesan/menit: 5\n"
            f"• Max link/pesan: 3\n"
            f"• Action: mute\n"
            f"• Mute durasi: 60 menit\n\n"
            f"<b>Command tersedia:</b>\n"
            f"/antispam on/off - Toggle\n"
            f"/antispam settings - Lihat detail"
        )

        keyboard = [
            [InlineKeyboardButton(toggle_text, callback_data="toggle_antispam")],
            [InlineKeyboardButton("⚡ Ubah Action", callback_data="set_spam_action")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _welcome_menu(self, query, settings):
        """Menu pengaturan welcome"""
        status = "✅ Aktif" if settings["welcome_enabled"] else "❌ Nonaktif"
        toggle_text = "❌ Nonaktifkan" if settings["welcome_enabled"] else "✅ Aktifkan"
        current_msg = settings["welcome_message"] or "(Default message)"

        text = (
            f"👋 <b>Welcome Settings</b>\n\n"
            f"Status: {status}\n\n"
            f"<b>Pesan saat ini:</b>\n"
            f"<blockquote>{current_msg[:200]}</blockquote>\n\n"
            f"<b>Command:</b>\n"
            f"/welcome on/off - Toggle\n"
            f"/setwelcome [teks] - Atur pesan\n\n"
            f"<b>Variabel:</b>\n"
            f"{{mention}} {{name}} {{username}}\n"
            f"{{chat_title}} {{member_count}}"
        )

        keyboard = [
            [InlineKeyboardButton(toggle_text, callback_data="toggle_welcome")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _autoreply_menu(self, query, settings):
        """Menu pengaturan auto-reply"""
        status = "✅ Aktif" if settings["autoreply_enabled"] else "❌ Nonaktif"
        toggle_text = "❌ Nonaktifkan" if settings["autoreply_enabled"] else "✅ Aktifkan"
        current_msg = settings["autoreply_message"] or "(Default message)"

        text = (
            f"💬 <b>Auto-Reply Settings</b>\n\n"
            f"Status: {status}\n"
            f"Cooldown: 5 menit per user\n\n"
            f"<b>Pesan saat ini:</b>\n"
            f"<blockquote>{current_msg[:200]}</blockquote>\n\n"
            f"<b>Command:</b>\n"
            f"/autoreply on/off - Toggle\n"
            f"/setreply [teks] - Atur pesan"
        )

        keyboard = [
            [InlineKeyboardButton(toggle_text, callback_data="toggle_autoreply")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _autoposter_menu(self, query):
        """Menu auto-poster"""
        text = (
            "📮 <b>Auto-Poster Settings</b>\n\n"
            "Timezone: Asia/Jakarta\n\n"
            "<b>Command tersedia:</b>\n"
            "/schedule [tanggal] [jam] [pesan] - Jadwalkan\n"
            "/listschedule - Lihat jadwal\n"
            "/cancelschedule [id] - Batalkan\n\n"
            "<b>Contoh:</b>\n"
            "<code>/schedule 2025-01-01 08:00 Happy New Year!</code>"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _crosspost_menu(self, query):
        """Menu cross-post"""
        text = (
            "📡 <b>Cross-Post Settings</b>\n\n"
            "<b>Command tersedia:</b>\n"
            "/addchannel [id] - Tambah channel\n"
            "/removechannel [id] - Hapus channel\n"
            "/channels - Lihat daftar\n"
            "/crosspost [pesan] - Post ke semua\n\n"
            "<b>Catatan:</b>\n"
            "Bot harus jadi admin di channel target!"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _analytics_menu(self, query):
        """Menu analytics"""
        text = (
            "📊 <b>Analytics Settings</b>\n\n"
            "Tracking: ✅ Aktif (selalu on)\n\n"
            "<b>Yang di-track:</b>\n"
            "• Jumlah pesan per user\n"
            "• Tipe pesan (text/photo/video/dll)\n"
            "• Member join & leave\n"
            "• Engagement rate\n\n"
            "<b>Command:</b>\n"
            "/stats - Statistik hari ini\n"
            "/stats week - Minggu ini\n"
            "/stats month - Bulan ini\n"
            "/topusers - User paling aktif"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _spam_keywords_menu(self, query):
        """Menu kelola spam keywords"""
        from config import SPAM_KEYWORDS

        keywords_text = ", ".join([f"<code>{k}</code>" for k in SPAM_KEYWORDS[:15]])

        text = (
            "🔑 <b>Spam Keywords</b>\n\n"
            f"<b>Keywords saat ini ({len(SPAM_KEYWORDS)}):</b>\n"
            f"{keywords_text}\n"
            f"{'...' if len(SPAM_KEYWORDS) > 15 else ''}\n\n"
            "<b>Command:</b>\n"
            "/addkeyword [kata] - Tambah keyword\n"
            "/removekeyword [kata] - Hapus keyword\n"
            "/listkeywords - Lihat semua\n\n"
            "<i>Keywords disimpan di config.py</i>"
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _spam_action_menu(self, query, settings):
        """Menu pilih spam action"""
        text = (
            "⚡ <b>Pilih Aksi Anti-Spam</b>\n\n"
            "Apa yang dilakukan bot saat mendeteksi spam?\n\n"
            "• <b>delete</b> - Hapus pesan saja\n"
            "• <b>mute</b> - Hapus + mute 1 jam\n"
            "• <b>kick</b> - Hapus + kick (bisa join lagi)\n"
            "• <b>ban</b> - Hapus + ban permanen\n"
        )

        keyboard = [
            [
                InlineKeyboardButton("🗑 Delete", callback_data="action_delete"),
                InlineKeyboardButton("🔇 Mute", callback_data="action_mute"),
            ],
            [
                InlineKeyboardButton("👢 Kick", callback_data="action_kick"),
                InlineKeyboardButton("🚫 Ban", callback_data="action_ban"),
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="set_back")],
        ]

        await query.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _view_all_config(self, query, settings):
        """Tampilkan semua config"""
        from config import (
            SPAM_KEYWORDS, SPAM_MAX_MESSAGES_PER_MINUTE,
            SPAM_MAX_LINKS_PER_MESSAGE, SPAM_ACTION, SPAM_MUTE_DURATION,
            AUTO_REPLY_COOLDOWN, POSTER_TIMEZONE
        )

        antispam = "✅" if settings["antispam_enabled"] else "❌"
        welcome = "✅" if settings["welcome_enabled"] else "❌"
        autoreply = "✅" if settings["autoreply_enabled"] else "❌"

        text = (
            "📝 <b>FULL CONFIGURATION</b>\n\n"
            "<b>━━ Status Fitur ━━</b>\n"
            f"🛡 Anti-Spam: {antispam}\n"
            f"👋 Welcome: {welcome}\n"
            f"💬 Auto-Reply: {autoreply}\n"
            f"📮 Auto-Poster: ✅\n"
            f"📡 Cross-Post: ✅\n"
            f"📊 Analytics: ✅\n\n"
            "<b>━━ Anti-Spam Config ━━</b>\n"
            f"Max pesan/menit: {SPAM_MAX_MESSAGES_PER_MINUTE}\n"
            f"Max link/pesan: {SPAM_MAX_LINKS_PER_MESSAGE}\n"
            f"Action: {SPAM_ACTION}\n"
            f"Mute durasi: {SPAM_MUTE_DURATION // 60} menit\n"
            f"Keywords: {len(SPAM_KEYWORDS)} kata\n\n"
            "<b>━━ Auto-Reply Config ━━</b>\n"
            f"Cooldown: {AUTO_REPLY_COOLDOWN // 60} menit\n\n"
            "<b>━━ Auto-Poster Config ━━</b>\n"
            f"Timezone: {POSTER_TIMEZONE}\n\n"
            "<b>━━ Tips ━━</b>\n"
            "Semua fitur bisa di-toggle on/off dari menu.\n"
            "Gunakan /settings kapan saja untuk kembali."
        )

        await query.message.reply_html(text)

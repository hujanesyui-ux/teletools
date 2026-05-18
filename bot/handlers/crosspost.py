"""
TeleTools - Cross-Post Handler
Post ke banyak channel sekaligus.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import admin_only

logger = logging.getLogger(__name__)


class CrossPostHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def add_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tambah channel untuk cross-post
        Format: /addchannel -1001234567890 atau /addchannel @channelname
        """
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_html(
                "⚠️ <b>Penggunaan:</b>\n"
                "<code>/addchannel [channel_id]</code>\n\n"
                "<b>Contoh:</b>\n"
                "<code>/addchannel -1001234567890</code>\n\n"
                "<b>Cara dapat channel ID:</b>\n"
                "1. Forward pesan dari channel ke @userinfobot\n"
                "2. Atau gunakan @RawDataBot\n\n"
                "⚠️ Pastikan bot sudah jadi admin di channel tersebut!"
            )
            return

        try:
            channel_id = int(context.args[0])
        except ValueError:
            await update.message.reply_html("⚠️ Channel ID harus berupa angka!")
            return

        # Coba dapatkan info channel
        channel_title = None
        try:
            chat = await context.bot.get_chat(channel_id)
            channel_title = chat.title
        except Exception as e:
            await update.message.reply_html(
                f"⚠️ Tidak bisa mengakses channel <code>{channel_id}</code>.\n"
                f"Pastikan bot sudah jadi admin di channel tersebut!\n\n"
                f"Error: {str(e)}"
            )
            return

        # Simpan ke database
        success = self.db.add_crosspost_channel(user_id, channel_id, channel_title)

        if success:
            await update.message.reply_html(
                f"✅ Channel berhasil ditambahkan!\n\n"
                f"📡 <b>{channel_title}</b>\n"
                f"🆔 <code>{channel_id}</code>"
            )
        else:
            await update.message.reply_html("⚠️ Channel sudah ada di daftar.")

    @admin_only
    async def remove_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hapus channel dari daftar cross-post"""
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_html("⚠️ Penggunaan: /removechannel [channel_id]")
            return

        try:
            channel_id = int(context.args[0])
        except ValueError:
            await update.message.reply_html("⚠️ Channel ID harus berupa angka!")
            return

        success = self.db.remove_crosspost_channel(user_id, channel_id)

        if success:
            await update.message.reply_html(f"✅ Channel <code>{channel_id}</code> dihapus dari daftar.")
        else:
            await update.message.reply_html(f"❌ Channel <code>{channel_id}</code> tidak ditemukan di daftar.")

    @admin_only
    async def list_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat daftar channel cross-post"""
        user_id = update.effective_user.id
        channels = self.db.get_crosspost_channels(user_id)

        if not channels:
            await update.message.reply_html(
                "📡 Belum ada channel terdaftar.\n"
                "Gunakan /addchannel [channel_id] untuk menambahkan."
            )
            return

        text = "📡 <b>Daftar Channel Cross-Post:</b>\n\n"

        for i, ch in enumerate(channels, 1):
            title = ch["channel_title"] or "Unknown"
            text += f"{i}. <b>{title}</b>\n   🆔 <code>{ch['channel_id']}</code>\n\n"

        text += f"Total: {len(channels)} channel\n"
        text += "Gunakan /removechannel [id] untuk menghapus."
        await update.message.reply_html(text)

    @admin_only
    async def post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Post pesan ke semua channel sekaligus
        Format: /crosspost Ini pesan yang akan di-post ke semua channel
        """
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_html(
                "⚠️ <b>Penggunaan:</b>\n"
                "<code>/crosspost [pesan]</code>\n\n"
                "<b>Contoh:</b>\n"
                "<code>/crosspost Halo semua! Ini pengumuman penting.</code>\n\n"
                "Pesan akan dikirim ke semua channel yang terdaftar."
            )
            return

        message_text = update.message.text.split(None, 1)[1]
        channels = self.db.get_crosspost_channels(user_id)

        if not channels:
            await update.message.reply_html(
                "⚠️ Belum ada channel terdaftar!\n"
                "Gunakan /addchannel [channel_id] untuk menambahkan."
            )
            return

        # Kirim ke semua channel
        success_count = 0
        fail_count = 0
        results = []

        for ch in channels:
            try:
                await context.bot.send_message(
                    chat_id=ch["channel_id"],
                    text=message_text,
                    parse_mode="HTML",
                )
                success_count += 1
                results.append(f"✅ {ch['channel_title'] or ch['channel_id']}")
            except Exception as e:
                fail_count += 1
                results.append(f"❌ {ch['channel_title'] or ch['channel_id']}: {str(e)[:50]}")
                logger.error(f"Crosspost gagal ke {ch['channel_id']}: {e}")

        # Laporan
        results_text = "\n".join(results)
        await update.message.reply_html(
            f"📡 <b>Cross-Post Selesai!</b>\n\n"
            f"✅ Berhasil: {success_count}\n"
            f"❌ Gagal: {fail_count}\n\n"
            f"<b>Detail:</b>\n{results_text}"
        )

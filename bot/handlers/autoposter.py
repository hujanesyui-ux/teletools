"""
TeleTools - Auto-Poster Handler
Jadwalkan & posting otomatis ke channel/grup.
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import admin_only
from config import POSTER_TIMEZONE

logger = logging.getLogger(__name__)


class AutoPosterHandler:
    def __init__(self, db, app=None):
        self.db = db
        self.app = app
        self._setup_scheduler()

    def _setup_scheduler(self):
        """Setup APScheduler untuk posting terjadwal"""
        try:
            import asyncio
            from apscheduler.schedulers.asyncio import AsyncIOScheduler

            # Fix untuk Python 3.10+: buat event loop jika belum ada
            try:
                asyncio.get_event_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            self.scheduler = AsyncIOScheduler(timezone=POSTER_TIMEZONE)
            # Jangan start di sini, akan di-start saat bot running
            logger.info("Auto-poster scheduler initialized")
        except ImportError:
            self.scheduler = None
            logger.warning("APScheduler not installed, auto-poster disabled")

    @admin_only
    async def schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Jadwalkan posting baru
        Format: /schedule 2024-12-25 10:00 Selamat Natal!
        """
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        if not context.args or len(context.args) < 3:
            await update.message.reply_html(
                "⚠️ <b>Penggunaan:</b>\n"
                "<code>/schedule [tanggal] [jam] [pesan]</code>\n\n"
                "<b>Contoh:</b>\n"
                "<code>/schedule 2025-01-01 08:00 Selamat Tahun Baru! 🎉</code>\n"
                "<code>/schedule 2025-06-15 12:30 Promo hari ini!</code>\n\n"
                f"<b>Timezone:</b> {POSTER_TIMEZONE}"
            )
            return

        # Parse arguments
        date_str = context.args[0]
        time_str = context.args[1]
        message_text = " ".join(context.args[2:])

        # Validasi format tanggal & waktu
        try:
            scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            await update.message.reply_html(
                "⚠️ Format tanggal/waktu salah!\n"
                "Gunakan format: <code>YYYY-MM-DD HH:MM</code>\n"
                "Contoh: <code>2025-06-15 14:30</code>"
            )
            return

        # Cek apakah waktu di masa depan
        if scheduled_time <= datetime.now():
            await update.message.reply_html("⚠️ Waktu harus di masa depan!")
            return

        # Simpan ke database
        post_id = self.db.add_scheduled_post(
            chat_id=chat_id,
            creator_id=user_id,
            message_text=message_text,
            scheduled_time=scheduled_time.isoformat(),
        )

        # Schedule dengan APScheduler
        if self.scheduler:
            self.scheduler.add_job(
                self._send_scheduled_post,
                trigger="date",
                run_date=scheduled_time,
                args=[post_id, chat_id, message_text],
                id=f"post_{post_id}",
                replace_existing=True,
            )

        await update.message.reply_html(
            f"✅ <b>Posting dijadwalkan!</b>\n\n"
            f"🆔 ID: <code>{post_id}</code>\n"
            f"📅 Waktu: <code>{scheduled_time.strftime('%d %b %Y, %H:%M')}</code>\n"
            f"💬 Pesan:\n<blockquote>{message_text}</blockquote>\n\n"
            f"Gunakan /cancelschedule {post_id} untuk membatalkan."
        )

    @admin_only
    async def list_schedules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat daftar posting terjadwal"""
        chat_id = update.effective_chat.id
        posts = self.db.get_pending_posts(chat_id)

        if not posts:
            await update.message.reply_html("📮 Tidak ada jadwal posting aktif.")
            return

        text = "📮 <b>Jadwal Posting Aktif:</b>\n\n"

        for post in posts:
            scheduled = datetime.fromisoformat(post["scheduled_time"])
            text += (
                f"🆔 <code>{post['id']}</code> | "
                f"📅 {scheduled.strftime('%d %b %Y, %H:%M')}\n"
                f"💬 {post['message_text'][:50]}{'...' if len(post['message_text']) > 50 else ''}\n\n"
            )

        text += "Gunakan /cancelschedule [id] untuk membatalkan."
        await update.message.reply_html(text)

    @admin_only
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Batalkan jadwal posting"""
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_html("⚠️ Penggunaan: /cancelschedule [id]")
            return

        try:
            post_id = int(context.args[0])
        except ValueError:
            await update.message.reply_html("⚠️ ID harus berupa angka!")
            return

        success = self.db.cancel_post(post_id, user_id)

        if success:
            # Remove dari scheduler juga
            if self.scheduler:
                try:
                    self.scheduler.remove_job(f"post_{post_id}")
                except Exception:
                    pass

            await update.message.reply_html(f"✅ Jadwal posting #{post_id} dibatalkan.")
        else:
            await update.message.reply_html(
                f"❌ Gagal membatalkan posting #{post_id}.\n"
                f"Pastikan ID benar dan kamu yang membuat jadwal."
            )

    async def _send_scheduled_post(self, post_id: int, chat_id: int, message_text: str):
        """Kirim posting terjadwal"""
        try:
            if self.app:
                await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode="HTML",
                )
            self.db.mark_post_sent(post_id)
            logger.info(f"Scheduled post {post_id} sent to {chat_id}")
        except Exception as e:
            logger.error(f"Gagal kirim scheduled post {post_id}: {e}")

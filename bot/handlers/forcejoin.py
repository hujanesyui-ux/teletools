"""
TeleTools - Forced Join Handler
User wajib join channel/grup tertentu sebelum bisa chat.
Mirip sistem "join 3 channel dulu baru bisa masuk".
"""

import logging
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.admin import admin_only

logger = logging.getLogger(__name__)


class ForceJoinHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /forcejoin command"""
        chat_id = update.effective_chat.id
        args = context.args

        if not args:
            settings = self.db.get_settings(chat_id)
            status = "✅ Aktif" if settings.get("forcejoin_enabled") else "❌ Nonaktif"
            channels = self.db.get_forcejoin_channels(chat_id)

            text = (
                f"🔒 <b>Forced Join Settings</b>\n\n"
                f"Status: {status}\n"
                f"Channel wajib join: {len(channels)}\n\n"
            )

            if channels:
                text += "<b>Daftar channel wajib:</b>\n"
                for i, ch in enumerate(channels, 1):
                    text += f"  {i}. <b>{ch['channel_title'] or 'Unknown'}</b>\n"
                    text += f"     🆔 <code>{ch['channel_id']}</code>\n"
                    if ch.get("invite_link"):
                        text += f"     🔗 {ch['invite_link']}\n"
                    text += "\n"

            text += (
                "<b>Cara kerja:</b>\n"
                "1. Member kirim pesan di grup\n"
                "2. Bot cek apakah sudah join semua channel\n"
                "3. Belum join → pesan dihapus + kirim reminder\n"
                "4. Sudah join semua → bisa chat normal\n\n"
                "<b>Command:</b>\n"
                "/forcejoin on - Aktifkan\n"
                "/forcejoin off - Nonaktifkan\n"
                "/addforcejoin [channel_id] [invite_link] - Tambah channel\n"
                "/removeforcejoin [channel_id] - Hapus channel\n"
                "/forcejoinlist - Lihat daftar channel"
            )
            await update.message.reply_html(text)
            return

        action = args[0].lower()

        if action == "on":
            channels = self.db.get_forcejoin_channels(chat_id)
            if not channels:
                await update.message.reply_html(
                    "⚠️ Belum ada channel yang ditambahkan!\n"
                    "Tambahkan dulu dengan:\n"
                    "<code>/addforcejoin [channel_id] [invite_link]</code>"
                )
                return
            self.db.update_setting(chat_id, "forcejoin_enabled", 1)
            await update.message.reply_html(
                f"🔒 Forced Join <b>diaktifkan</b>! ✅\n\n"
                f"Member harus join {len(channels)} channel sebelum bisa chat."
            )
        elif action == "off":
            self.db.update_setting(chat_id, "forcejoin_enabled", 0)
            await update.message.reply_html("🔒 Forced Join <b>dinonaktifkan</b>. ❌")
        else:
            await update.message.reply_html(
                "⚠️ Penggunaan: /forcejoin [on|off]\n"
                "Lihat /forcejoin untuk info lengkap."
            )

    @admin_only
    async def add_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tambah channel wajib join
        Format: /addforcejoin -1001234567890 https://t.me/channelname
        """
        chat_id = update.effective_chat.id
        args = context.args

        if not args or len(args) < 1:
            await update.message.reply_html(
                "⚠️ <b>Penggunaan:</b>\n"
                "<code>/addforcejoin [channel_id] [invite_link]</code>\n\n"
                "<b>Contoh:</b>\n"
                "<code>/addforcejoin -1001234567890 https://t.me/mychannel</code>\n\n"
                "<b>Catatan:</b>\n"
                "• Bot harus jadi admin di channel tersebut\n"
                "• Invite link supaya user bisa langsung klik join\n"
                "• Channel ID format: -100xxxxxxxxxx"
            )
            return

        try:
            channel_id = int(args[0])
        except ValueError:
            await update.message.reply_html("⚠️ Channel ID harus berupa angka!")
            return

        invite_link = args[1] if len(args) > 1 else None

        # Coba verifikasi channel
        channel_title = None
        try:
            chat_info = await context.bot.get_chat(channel_id)
            channel_title = chat_info.title

            # Cek bot adalah admin
            bot_member = await context.bot.get_chat_member(channel_id, context.bot.id)
            if bot_member.status not in ["administrator", "creator"]:
                await update.message.reply_html(
                    f"⚠️ Bot bukan admin di channel <b>{channel_title}</b>!\n"
                    f"Jadikan bot sebagai admin dulu."
                )
                return

        except Exception as e:
            await update.message.reply_html(
                f"⚠️ Tidak bisa mengakses channel <code>{channel_id}</code>.\n"
                f"Pastikan bot sudah jadi admin!\n\n"
                f"Error: {str(e)[:100]}"
            )
            return

        # Simpan ke database
        success = self.db.add_forcejoin_channel(
            chat_id=chat_id,
            channel_id=channel_id,
            channel_title=channel_title,
            invite_link=invite_link,
        )

        if success:
            total = len(self.db.get_forcejoin_channels(chat_id))
            await update.message.reply_html(
                f"✅ Channel berhasil ditambahkan!\n\n"
                f"📡 <b>{channel_title}</b>\n"
                f"🆔 <code>{channel_id}</code>\n"
                f"🔗 {invite_link or 'Tidak ada invite link'}\n\n"
                f"Total channel wajib: {total}"
            )
        else:
            await update.message.reply_html("⚠️ Channel sudah ada di daftar.")

    @admin_only
    async def remove_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hapus channel dari daftar forced join"""
        chat_id = update.effective_chat.id
        args = context.args

        if not args:
            await update.message.reply_html(
                "⚠️ Penggunaan: /removeforcejoin [channel_id]\n"
                "Gunakan /forcejoinlist untuk lihat daftar."
            )
            return

        try:
            channel_id = int(args[0])
        except ValueError:
            await update.message.reply_html("⚠️ Channel ID harus berupa angka!")
            return

        success = self.db.remove_forcejoin_channel(chat_id, channel_id)

        if success:
            await update.message.reply_html(f"✅ Channel <code>{channel_id}</code> dihapus dari daftar.")
        else:
            await update.message.reply_html(f"❌ Channel <code>{channel_id}</code> tidak ditemukan.")

    @admin_only
    async def list_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat semua channel forced join"""
        chat_id = update.effective_chat.id
        channels = self.db.get_forcejoin_channels(chat_id)

        if not channels:
            await update.message.reply_html(
                "🔒 Belum ada channel wajib join.\n"
                "Tambahkan dengan: /addforcejoin [channel_id] [invite_link]"
            )
            return

        text = "🔒 <b>Daftar Channel Wajib Join:</b>\n\n"

        for i, ch in enumerate(channels, 1):
            text += f"{i}. <b>{ch['channel_title'] or 'Unknown'}</b>\n"
            text += f"   🆔 <code>{ch['channel_id']}</code>\n"
            if ch.get("invite_link"):
                text += f"   🔗 {ch['invite_link']}\n"
            text += "\n"

        text += f"Total: {len(channels)} channel\n"
        text += "Gunakan /removeforcejoin [id] untuk menghapus."
        await update.message.reply_html(text)

    async def check_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cek setiap pesan - apakah user sudah join semua channel wajib"""
        if not update.message or not update.effective_user:
            return

        chat_id = update.effective_chat.id
        user = update.effective_user

        # Cek apakah forced join aktif
        settings = self.db.get_settings(chat_id)
        if not settings.get("forcejoin_enabled"):
            return

        # Skip admin
        try:
            member = await update.effective_chat.get_member(user.id)
            if member.status in ["administrator", "creator"]:
                return
        except Exception:
            pass

        # Ambil daftar channel wajib
        channels = self.db.get_forcejoin_channels(chat_id)
        if not channels:
            return

        # Cek membership di setiap channel
        not_joined = []
        for ch in channels:
            try:
                ch_member = await context.bot.get_chat_member(ch["channel_id"], user.id)
                if ch_member.status in ["left", "kicked"]:
                    not_joined.append(ch)
            except Exception:
                # Kalau error cek, anggap belum join
                not_joined.append(ch)

        # Kalau sudah join semua, lewat
        if not not_joined:
            return

        # Belum join semua → hapus pesan & kirim reminder
        try:
            await update.message.delete()
        except Exception:
            pass

        # Buat keyboard dengan link join
        keyboard = []
        for ch in not_joined:
            title = ch["channel_title"] or f"Channel {ch['channel_id']}"
            link = ch.get("invite_link") or f"https://t.me/c/{str(ch['channel_id'])[4:]}"
            keyboard.append([InlineKeyboardButton(f"📡 Join {title}", url=link)])

        # Tombol verifikasi setelah join
        keyboard.append([InlineKeyboardButton(
            "✅ Sudah Join Semua - Verifikasi",
            callback_data=f"forcejoin_verify_{user.id}"
        )])

        text = (
            f"🔒 <b>Akses Terbatas!</b>\n\n"
            f"{user.mention_html()}, kamu harus join channel berikut "
            f"sebelum bisa chat di grup ini:\n\n"
        )

        for i, ch in enumerate(not_joined, 1):
            title = ch["channel_title"] or "Channel"
            text += f"  {i}. ❌ <b>{title}</b>\n"

        text += (
            f"\nTotal belum join: {len(not_joined)}/{len(channels)}\n\n"
            f"Klik tombol di bawah untuk join, "
            f"lalu klik <b>\"Sudah Join Semua\"</b> untuk verifikasi."
        )

        # Kirim reminder (hapus otomatis setelah 30 detik)
        try:
            reminder_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

            # Auto-delete reminder setelah 60 detik
            context.job_queue.run_once(
                self._delete_reminder,
                when=60,
                data={"chat_id": chat_id, "message_id": reminder_msg.message_id},
                name=f"fj_reminder_{chat_id}_{reminder_msg.message_id}",
            )
        except Exception as e:
            logger.error(f"Gagal kirim forced join reminder: {e}")

    async def handle_verify_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tombol verifikasi setelah user join channel"""
        query = update.callback_query
        user = query.from_user
        chat_id = update.effective_chat.id
        data = query.data

        # Parse: forcejoin_verify_{user_id}
        parts = data.split("_")
        if len(parts) != 3:
            await query.answer("❌ Invalid")
            return

        target_user_id = int(parts[2])

        # Hanya user bersangkutan yang bisa verify
        if user.id != target_user_id:
            await query.answer("⚠️ Ini bukan untuk kamu!", show_alert=True)
            return

        # Cek ulang semua channel
        channels = self.db.get_forcejoin_channels(chat_id)
        not_joined = []

        for ch in channels:
            try:
                ch_member = await context.bot.get_chat_member(ch["channel_id"], user.id)
                if ch_member.status in ["left", "kicked"]:
                    not_joined.append(ch)
            except Exception:
                not_joined.append(ch)

        if not_joined:
            # Masih belum join semua
            names = ", ".join([ch["channel_title"] or "Channel" for ch in not_joined])
            await query.answer(
                f"❌ Kamu belum join: {names}",
                show_alert=True,
            )
            return

        # Sudah join semua! 🎉
        await query.answer("✅ Verifikasi berhasil! Kamu bisa chat sekarang.")

        try:
            await query.message.edit_text(
                f"✅ {user.mention_html()} sudah join semua channel!\n"
                f"Selamat, kamu sekarang bisa chat di grup ini. 🎉",
                parse_mode="HTML",
            )
        except Exception:
            pass

        logger.info(f"Force join verified: {user.id} in {chat_id}")

    async def _delete_reminder(self, context):
        """Auto-delete reminder message"""
        data = context.job.data
        try:
            await context.bot.delete_message(
                chat_id=data["chat_id"],
                message_id=data["message_id"],
            )
        except Exception:
            pass

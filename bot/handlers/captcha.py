"""
TeleTools - Captcha Verification Handler
Member baru harus selesaikan captcha sebelum bisa kirim pesan.
Mendukung: Math Captcha, Button Captcha
"""

import random
import logging
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.admin import admin_only
from config import CAPTCHA_TIMEOUT, CAPTCHA_TYPE

logger = logging.getLogger(__name__)


class CaptchaHandler:
    def __init__(self, db):
        self.db = db
        # Store pending captchas: {user_id: {chat_id, answer, message_id, timestamp}}
        self.pending = {}

    @admin_only
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /captcha command"""
        chat_id = update.effective_chat.id
        args = context.args

        if not args:
            settings = self.db.get_settings(chat_id)
            status = "✅ Aktif" if settings.get("captcha_enabled") else "❌ Nonaktif"
            text = (
                f"🔐 <b>Captcha Verification Settings</b>\n\n"
                f"Status: {status}\n"
                f"Tipe: {CAPTCHA_TYPE}\n"
                f"Timeout: {CAPTCHA_TIMEOUT} detik\n\n"
                f"<b>Cara kerja:</b>\n"
                f"1. Member baru join → langsung di-mute\n"
                f"2. Bot kirim captcha (soal/tombol)\n"
                f"3. Jawab benar → unmute, bisa chat\n"
                f"4. Timeout/salah → kick otomatis\n\n"
                f"<b>Command:</b>\n"
                f"/captcha on - Aktifkan\n"
                f"/captcha off - Nonaktifkan\n"
                f"/captcha type [math|button] - Ubah tipe"
            )
            await update.message.reply_html(text)
            return

        action = args[0].lower()

        if action == "on":
            self.db.update_setting(chat_id, "captcha_enabled", 1)
            await update.message.reply_html(
                "🔐 Captcha verification <b>diaktifkan</b>! ✅\n\n"
                "Member baru akan di-mute sampai menyelesaikan captcha."
            )
        elif action == "off":
            self.db.update_setting(chat_id, "captcha_enabled", 0)
            await update.message.reply_html("🔐 Captcha verification <b>dinonaktifkan</b>. ❌")
        elif action == "type":
            if len(args) < 2 or args[1].lower() not in ["math", "button"]:
                await update.message.reply_html(
                    "⚠️ Penggunaan: /captcha type [math|button]\n\n"
                    "• <b>math</b> - Soal matematika (2+3=?)\n"
                    "• <b>button</b> - Klik tombol yang benar"
                )
                return
            captcha_type = args[1].lower()
            self.db.update_setting(chat_id, "captcha_type", captcha_type)
            await update.message.reply_html(f"🔐 Tipe captcha diubah ke: <b>{captcha_type}</b>")
        else:
            await update.message.reply_html("⚠️ Penggunaan: /captcha [on|off|type]")

    async def on_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Triggered saat member baru join - kirim captcha"""
        result = self._extract_status_change(update.chat_member)
        if result is None:
            return

        was_member, is_member = result
        if not (not was_member and is_member):
            return  # Bukan member baru join

        chat = update.effective_chat
        new_member = update.chat_member.new_chat_member.user

        # Skip bot
        if new_member.is_bot:
            return

        # Cek apakah captcha aktif
        settings = self.db.get_settings(chat.id)
        if not settings.get("captcha_enabled"):
            return

        # Mute member baru
        try:
            await chat.restrict_member(
                user_id=new_member.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                ),
            )
        except Exception as e:
            logger.error(f"Gagal mute member baru: {e}")
            return

        # Kirim captcha
        captcha_type = settings.get("captcha_type") or CAPTCHA_TYPE

        if captcha_type == "math":
            await self._send_math_captcha(context, chat, new_member)
        else:
            await self._send_button_captcha(context, chat, new_member)

        # Set timeout job
        context.job_queue.run_once(
            self._captcha_timeout,
            when=CAPTCHA_TIMEOUT,
            data={"chat_id": chat.id, "user_id": new_member.id},
            name=f"captcha_{chat.id}_{new_member.id}",
        )

    async def _send_math_captcha(self, context, chat, user):
        """Kirim captcha matematika"""
        # Generate soal random
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        operator = random.choice(["+", "-", "x"])

        if operator == "+":
            answer = num1 + num2
        elif operator == "-":
            # Pastikan hasil positif
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
        else:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            answer = num1 * num2

        # Buat pilihan jawaban (1 benar, 3 salah)
        choices = [answer]
        while len(choices) < 4:
            fake = answer + random.randint(-5, 5)
            if fake != answer and fake >= 0 and fake not in choices:
                choices.append(fake)

        random.shuffle(choices)

        # Buat keyboard
        keyboard = []
        row = []
        for choice in choices:
            row.append(InlineKeyboardButton(
                str(choice),
                callback_data=f"captcha_{user.id}_{choice}_{answer}"
            ))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        text = (
            f"🔐 <b>Verifikasi Captcha</b>\n\n"
            f"Halo {user.mention_html()}!\n"
            f"Selesaikan soal berikut untuk bisa chat:\n\n"
            f"<b>{num1} {operator} {num2} = ?</b>\n\n"
            f"⏱ Waktu: {CAPTCHA_TIMEOUT} detik\n"
            f"❌ Salah/timeout = kick otomatis"
        )

        msg = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        # Simpan data captcha
        self.pending[f"{chat.id}_{user.id}"] = {
            "answer": answer,
            "message_id": msg.message_id,
            "timestamp": datetime.now(),
        }

    async def _send_button_captcha(self, context, chat, user):
        """Kirim captcha tombol (klik tombol yang benar)"""
        # Generate emoji set
        emojis = ["🍎", "🍊", "🍋", "🍇", "🍓", "🍑", "🥝", "🍒", "🫐", "🥭"]
        target = random.choice(emojis)

        # Buat pilihan (1 target + 5 random lain)
        choices = [target]
        available = [e for e in emojis if e != target]
        choices.extend(random.sample(available, 5))
        random.shuffle(choices)

        # Buat keyboard
        keyboard = []
        row = []
        for emoji in choices:
            is_correct = 1 if emoji == target else 0
            row.append(InlineKeyboardButton(
                emoji,
                callback_data=f"captcha_btn_{user.id}_{is_correct}"
            ))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        text = (
            f"🔐 <b>Verifikasi Captcha</b>\n\n"
            f"Halo {user.mention_html()}!\n"
            f"Klik emoji <b>{target}</b> untuk verifikasi:\n\n"
            f"⏱ Waktu: {CAPTCHA_TIMEOUT} detik\n"
            f"❌ Salah/timeout = kick otomatis"
        )

        msg = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        self.pending[f"{chat.id}_{user.id}"] = {
            "answer": target,
            "message_id": msg.message_id,
            "timestamp": datetime.now(),
        }

    async def handle_captcha_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle jawaban captcha dari callback button"""
        query = update.callback_query
        user = query.from_user
        chat_id = update.effective_chat.id
        data = query.data

        # Math captcha: captcha_{user_id}_{chosen}_{answer}
        if data.startswith("captcha_") and not data.startswith("captcha_btn_"):
            parts = data.split("_")
            if len(parts) != 4:
                await query.answer("❌ Invalid captcha")
                return

            target_user_id = int(parts[1])
            chosen = int(parts[2])
            correct_answer = int(parts[3])

            # Hanya user yang bersangkutan yang boleh jawab
            if user.id != target_user_id:
                await query.answer("⚠️ Ini bukan captcha kamu!", show_alert=True)
                return

            if chosen == correct_answer:
                await self._captcha_passed(context, chat_id, user, query.message)
            else:
                await self._captcha_failed(context, chat_id, user, query.message)

        # Button captcha: captcha_btn_{user_id}_{is_correct}
        elif data.startswith("captcha_btn_"):
            parts = data.split("_")
            if len(parts) != 4:
                await query.answer("❌ Invalid captcha")
                return

            target_user_id = int(parts[2])
            is_correct = int(parts[3])

            if user.id != target_user_id:
                await query.answer("⚠️ Ini bukan captcha kamu!", show_alert=True)
                return

            if is_correct:
                await self._captcha_passed(context, chat_id, user, query.message)
            else:
                await self._captcha_failed(context, chat_id, user, query.message)

        await query.answer()

    async def _captcha_passed(self, context, chat_id, user, message):
        """User berhasil menyelesaikan captcha"""
        # Unmute user
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
        except Exception as e:
            logger.error(f"Gagal unmute: {e}")

        # Hapus pesan captcha
        try:
            await message.edit_text(
                f"✅ {user.mention_html()} berhasil verifikasi!\n"
                f"Selamat datang di grup! 🎉",
                parse_mode="HTML",
            )
        except Exception:
            pass

        # Hapus dari pending
        key = f"{chat_id}_{user.id}"
        self.pending.pop(key, None)

        # Cancel timeout job
        jobs = context.job_queue.get_jobs_by_name(f"captcha_{chat_id}_{user.id}")
        for job in jobs:
            job.schedule_removal()

        logger.info(f"Captcha passed: {user.id} in {chat_id}")

    async def _captcha_failed(self, context, chat_id, user, message):
        """User gagal captcha - kick"""
        try:
            # Edit pesan
            await message.edit_text(
                f"❌ {user.mention_html()} gagal verifikasi.\n"
                f"User telah di-kick. Silakan join lagi dan coba lagi.",
                parse_mode="HTML",
            )
            # Kick user
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
            await context.bot.unban_chat_member(chat_id=chat_id, user_id=user.id)
        except Exception as e:
            logger.error(f"Gagal kick setelah captcha gagal: {e}")

        # Hapus dari pending
        key = f"{chat_id}_{user.id}"
        self.pending.pop(key, None)

        # Cancel timeout job
        jobs = context.job_queue.get_jobs_by_name(f"captcha_{chat_id}_{user.id}")
        for job in jobs:
            job.schedule_removal()

        logger.info(f"Captcha failed: {user.id} in {chat_id}")

    async def _captcha_timeout(self, context):
        """Timeout - user tidak jawab captcha"""
        data = context.job.data
        chat_id = data["chat_id"]
        user_id = data["user_id"]

        key = f"{chat_id}_{user_id}"
        pending_data = self.pending.pop(key, None)

        if pending_data is None:
            return  # Sudah di-handle

        # Hapus pesan captcha
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=pending_data["message_id"],
                text=f"⏱ Waktu habis! User telah di-kick karena tidak menyelesaikan captcha.",
            )
        except Exception:
            pass

        # Kick user
        try:
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        except Exception as e:
            logger.error(f"Gagal kick timeout captcha: {e}")

        logger.info(f"Captcha timeout: {user_id} in {chat_id}")

    def _extract_status_change(self, chat_member_update):
        """Extract apakah user baru join"""
        status_change = chat_member_update.difference().get("status")
        if status_change is None:
            return None
        old_status, new_status = status_change
        was_member = old_status in ["member", "administrator", "creator", "restricted"]
        is_member = new_status in ["member", "administrator", "creator", "restricted"]
        return was_member, is_member

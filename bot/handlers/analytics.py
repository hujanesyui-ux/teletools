"""
TeleTools - Analytics Handler
Statistik member, engagement, dan growth.
"""

import logging
from datetime import datetime
from telegram import Update, ChatMemberUpdated
from telegram.ext import ContextTypes

from handlers.admin import admin_only

logger = logging.getLogger(__name__)


class AnalyticsHandler:
    def __init__(self, db):
        self.db = db

    async def track_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track setiap pesan di grup untuk analytics"""
        if not update.message or not update.effective_user:
            return

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        # Tentukan tipe pesan
        if update.message.text:
            msg_type = "text"
        elif update.message.photo:
            msg_type = "photo"
        elif update.message.video:
            msg_type = "video"
        elif update.message.document:
            msg_type = "document"
        elif update.message.sticker:
            msg_type = "sticker"
        elif update.message.voice:
            msg_type = "voice"
        elif update.message.video_note:
            msg_type = "video_note"
        elif update.message.animation:
            msg_type = "animation"
        else:
            msg_type = "other"

        self.db.log_message(chat_id, user_id, msg_type)

    async def track_member_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track member join/leave"""
        result = self._extract_status_change(update.chat_member)
        if result is None:
            return

        was_member, is_member = result
        chat_id = update.effective_chat.id
        user_id = update.chat_member.new_chat_member.user.id

        if not was_member and is_member:
            self.db.log_member_event(chat_id, user_id, "join")
        elif was_member and not is_member:
            self.db.log_member_event(chat_id, user_id, "leave")

    @admin_only
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan statistik grup"""
        chat_id = update.effective_chat.id
        args = context.args

        # Tentukan periode
        if args and args[0].lower() == "week":
            days = 7
            period_name = "Minggu Ini"
        elif args and args[0].lower() == "month":
            days = 30
            period_name = "Bulan Ini"
        else:
            days = 1
            period_name = "Hari Ini"

        stats = self.db.get_message_stats(chat_id, days)

        # Hitung message types
        types_text = ""
        if stats["message_types"]:
            type_emojis = {
                "text": "💬",
                "photo": "🖼",
                "video": "🎬",
                "document": "📎",
                "sticker": "🎭",
                "voice": "🎤",
                "video_note": "🔵",
                "animation": "🎞",
                "other": "📦",
            }
            for msg_type, count in stats["message_types"].items():
                emoji = type_emojis.get(msg_type, "📦")
                types_text += f"  {emoji} {msg_type}: {count}\n"
        else:
            types_text = "  Belum ada data\n"

        # Get member count
        try:
            member_count = await update.effective_chat.get_member_count()
        except Exception:
            member_count = "?"

        # Net growth
        net_growth = stats["joins"] - stats["leaves"]
        growth_emoji = "📈" if net_growth > 0 else "📉" if net_growth < 0 else "➡️"

        text = (
            f"📊 <b>Statistik Grup - {period_name}</b>\n\n"
            f"👥 Total Member: {member_count}\n"
            f"💬 Total Pesan: {stats['total_messages']}\n"
            f"👤 User Aktif: {stats['unique_users']}\n\n"
            f"<b>📨 Tipe Pesan:</b>\n{types_text}\n"
            f"<b>👋 Member Activity:</b>\n"
            f"  ➡️ Join: +{stats['joins']}\n"
            f"  ⬅️ Leave: -{stats['leaves']}\n"
            f"  {growth_emoji} Net: {'+' if net_growth > 0 else ''}{net_growth}\n\n"
            f"<b>📈 Engagement Rate:</b>\n"
            f"  {self._calc_engagement(stats['unique_users'], member_count)}"
        )

        await update.message.reply_html(text)

    @admin_only
    async def top_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan top users paling aktif"""
        chat_id = update.effective_chat.id
        args = context.args

        days = 7  # Default: 7 hari
        if args:
            try:
                days = int(args[0])
            except ValueError:
                pass

        top = self.db.get_top_users(chat_id, days=days, limit=10)

        if not top:
            await update.message.reply_html(
                f"📊 Belum ada data aktivitas dalam {days} hari terakhir."
            )
            return

        text = f"🏆 <b>Top 10 User Paling Aktif</b>\n"
        text += f"<i>Periode: {days} hari terakhir</i>\n\n"

        medals = ["🥇", "🥈", "🥉"]

        for i, user_data in enumerate(top):
            # Try to get user info
            medal = medals[i] if i < 3 else f"{i+1}."
            try:
                member = await update.effective_chat.get_member(user_data["user_id"])
                name = member.user.first_name or "Unknown"
                username = f"@{member.user.username}" if member.user.username else ""
            except Exception:
                name = f"User {user_data['user_id']}"
                username = ""

            text += f"{medal} <b>{name}</b> {username}\n"
            text += f"    💬 {user_data['message_count']} pesan\n\n"

        await update.message.reply_html(text)

    def _calc_engagement(self, active_users, total_members) -> str:
        """Hitung engagement rate"""
        if isinstance(total_members, int) and total_members > 0:
            rate = (active_users / total_members) * 100
            if rate > 50:
                return f"{rate:.1f}% 🔥 Sangat aktif!"
            elif rate > 20:
                return f"{rate:.1f}% ✨ Cukup aktif"
            elif rate > 5:
                return f"{rate:.1f}% 😐 Kurang aktif"
            else:
                return f"{rate:.1f}% 😴 Sepi"
        return "N/A"

    def _extract_status_change(self, chat_member_update: ChatMemberUpdated):
        """Extract apakah user join atau leave"""
        status_change = chat_member_update.difference().get("status")
        if status_change is None:
            return None

        old_status, new_status = status_change
        was_member = old_status in ["member", "administrator", "creator", "restricted"]
        is_member = new_status in ["member", "administrator", "creator", "restricted"]
        return was_member, is_member

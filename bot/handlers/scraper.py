"""
TeleTools - Member Scraper Handler
Ambil daftar member dari grup.
"""

import csv
import json
import io
import logging
from telegram import Update
from telegram.ext import ContextTypes

from handlers.admin import admin_only

logger = logging.getLogger(__name__)


class ScraperHandler:
    def __init__(self, db):
        self.db = db

    @admin_only
    async def scrape(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scrape semua member dari grup"""
        chat = update.effective_chat

        if chat.type not in ["group", "supergroup"]:
            await update.message.reply_html(
                "⚠️ Command ini hanya bisa digunakan di grup!"
            )
            return

        # Kirim pesan loading
        msg = await update.message.reply_html("📋 Sedang scraping member... ⏳")

        try:
            count = 0
            # Gunakan get_chat_administrators dulu
            admins = await chat.get_administrators()

            for admin in admins:
                user = admin.user
                self.db.save_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_bot=user.is_bot,
                    status=admin.status,
                )
                count += 1

            # Update pesan
            total_in_db = self.db.get_member_count(chat.id)
            member_count = await chat.get_member_count()

            await msg.edit_text(
                f"📋 <b>Scraping Selesai!</b>\n\n"
                f"👥 Total member grup: {member_count}\n"
                f"✅ Admin ter-scrape: {count}\n"
                f"💾 Total di database: {total_in_db}\n\n"
                f"<i>Note: Bot API hanya bisa scrape admin/member yang terdeteksi. "
                f"Untuk scrape semua member, bot perlu Userbot (Telethon/Pyrogram).</i>\n\n"
                f"Gunakan /export csv atau /export json untuk download data.",
                parse_mode="HTML",
            )

            logger.info(f"Scraped {count} members from {chat.id}")

        except Exception as e:
            logger.error(f"Error scraping: {e}")
            await msg.edit_text(f"❌ Error saat scraping: {str(e)}")

    @admin_only
    async def export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export daftar member ke file"""
        chat = update.effective_chat
        args = context.args

        if not args:
            await update.message.reply_html(
                "⚠️ Penggunaan:\n"
                "/export csv - Export ke CSV\n"
                "/export json - Export ke JSON\n"
                "/export txt - Export ke TXT"
            )
            return

        format_type = args[0].lower()
        members = self.db.get_members(chat.id)

        if not members:
            await update.message.reply_html(
                "⚠️ Belum ada data member. Jalankan /scrape dulu!"
            )
            return

        try:
            if format_type == "csv":
                await self._export_csv(update, members, chat.title)
            elif format_type == "json":
                await self._export_json(update, members, chat.title)
            elif format_type == "txt":
                await self._export_txt(update, members, chat.title)
            else:
                await update.message.reply_html("⚠️ Format tidak didukung. Gunakan: csv, json, txt")

        except Exception as e:
            logger.error(f"Error export: {e}")
            await update.message.reply_html(f"❌ Error saat export: {str(e)}")

    async def _export_csv(self, update: Update, members: list, chat_title: str):
        """Export ke CSV"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["User ID", "Username", "First Name", "Last Name", "Is Bot", "Status", "Scraped At"])

        # Data
        for m in members:
            writer.writerow([
                m["user_id"],
                m["username"] or "",
                m["first_name"] or "",
                m["last_name"] or "",
                "Yes" if m["is_bot"] else "No",
                m["status"],
                m["scraped_at"],
            ])

        output.seek(0)
        filename = f"members_{chat_title or 'group'}.csv"

        await update.message.reply_document(
            document=io.BytesIO(output.getvalue().encode('utf-8')),
            filename=filename,
            caption=f"📋 Data member: {len(members)} orang",
        )

    async def _export_json(self, update: Update, members: list, chat_title: str):
        """Export ke JSON"""
        # Clean data
        export_data = []
        for m in members:
            export_data.append({
                "user_id": m["user_id"],
                "username": m["username"],
                "first_name": m["first_name"],
                "last_name": m["last_name"],
                "is_bot": bool(m["is_bot"]),
                "status": m["status"],
                "scraped_at": m["scraped_at"],
            })

        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        filename = f"members_{chat_title or 'group'}.json"

        await update.message.reply_document(
            document=io.BytesIO(json_str.encode('utf-8')),
            filename=filename,
            caption=f"📋 Data member: {len(members)} orang",
        )

    async def _export_txt(self, update: Update, members: list, chat_title: str):
        """Export ke TXT"""
        lines = [f"Member List - {chat_title or 'Group'}", "=" * 40, ""]

        for i, m in enumerate(members, 1):
            username = f"@{m['username']}" if m["username"] else "No username"
            name = f"{m['first_name'] or ''} {m['last_name'] or ''}".strip()
            lines.append(f"{i}. {name} | {username} | ID: {m['user_id']} | {m['status']}")

        lines.append(f"\nTotal: {len(members)} member")
        text = "\n".join(lines)
        filename = f"members_{chat_title or 'group'}.txt"

        await update.message.reply_document(
            document=io.BytesIO(text.encode('utf-8')),
            filename=filename,
            caption=f"📋 Data member: {len(members)} orang",
        )

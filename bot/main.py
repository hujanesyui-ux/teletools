"""
TeleTools - All-in-One Telegram Bot
Bot lengkap dengan fitur: Anti-Spam, Welcome, Member Scraper,
Auto-Reply, Auto-Poster, Cross-Post, dan Analytics.
"""

import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
)

from config import BOT_TOKEN, LOG_LEVEL, ADMIN_IDS
from database.db import Database
from handlers.admin import admin_only
from handlers.antispam import AntiSpamHandler
from handlers.welcome import WelcomeHandler
from handlers.scraper import ScraperHandler
from handlers.autoreply import AutoReplyHandler
from handlers.autoposter import AutoPosterHandler
from handlers.crosspost import CrossPostHandler
from handlers.analytics import AnalyticsHandler
from keyboards.inline import start_keyboard

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
)
logger = logging.getLogger(__name__)


# Initialize database
db = Database()


async def start(update: Update, context):
    """Handler untuk command /start"""
    user = update.effective_user
    text = (
        f"👋 Halo {user.mention_html()}!\n\n"
        f"Saya adalah <b>TeleTools Bot</b> 🤖\n"
        f"Bot all-in-one untuk manajemen grup Telegram.\n\n"
        f"<b>Fitur tersedia:</b>\n"
        f"🛡 Anti-Spam - Filter spam otomatis\n"
        f"👋 Welcome - Sambut member baru\n"
        f"📋 Scraper - Ambil daftar member\n"
        f"💬 Auto-Reply - Balas pesan otomatis\n"
        f"📮 Auto-Poster - Posting terjadwal\n"
        f"📡 Cross-Post - Post ke banyak channel\n"
        f"📊 Analytics - Statistik grup\n\n"
        f"Gunakan /help untuk melihat semua perintah."
    )
    await update.message.reply_html(text, reply_markup=start_keyboard())


async def help_command(update: Update, context):
    """Handler untuk command /help"""
    text = (
        "<b>📖 Daftar Perintah TeleTools</b>\n\n"
        "<b>🛡 Anti-Spam:</b>\n"
        "/antispam on - Aktifkan anti-spam\n"
        "/antispam off - Nonaktifkan anti-spam\n"
        "/antispam settings - Lihat pengaturan\n\n"
        "<b>👋 Welcome:</b>\n"
        "/welcome on - Aktifkan welcome message\n"
        "/welcome off - Nonaktifkan welcome message\n"
        "/setwelcome [teks] - Atur pesan welcome\n\n"
        "<b>📋 Member Scraper:</b>\n"
        "/scrape - Ambil daftar member grup ini\n"
        "/export csv - Export member ke CSV\n"
        "/export json - Export member ke JSON\n\n"
        "<b>💬 Auto-Reply:</b>\n"
        "/autoreply on - Aktifkan auto-reply\n"
        "/autoreply off - Nonaktifkan auto-reply\n"
        "/setreply [teks] - Atur pesan auto-reply\n\n"
        "<b>📮 Auto-Poster:</b>\n"
        "/schedule [waktu] [teks] - Jadwalkan posting\n"
        "/listschedule - Lihat jadwal posting\n"
        "/cancelschedule [id] - Batalkan jadwal\n\n"
        "<b>📡 Cross-Post:</b>\n"
        "/addchannel [channel_id] - Tambah channel\n"
        "/removechannel [channel_id] - Hapus channel\n"
        "/crosspost [teks] - Post ke semua channel\n"
        "/channels - Lihat daftar channel\n\n"
        "<b>📊 Analytics:</b>\n"
        "/stats - Statistik grup hari ini\n"
        "/stats week - Statistik minggu ini\n"
        "/stats month - Statistik bulan ini\n"
        "/topusers - User paling aktif\n"
    )
    await update.message.reply_html(text)


async def post_init(application):
    """Set bot commands setelah inisialisasi"""
    commands = [
        BotCommand("start", "Mulai bot"),
        BotCommand("help", "Lihat bantuan"),
        BotCommand("antispam", "Pengaturan anti-spam"),
        BotCommand("welcome", "Pengaturan welcome"),
        BotCommand("scrape", "Scrape member grup"),
        BotCommand("autoreply", "Pengaturan auto-reply"),
        BotCommand("schedule", "Jadwalkan posting"),
        BotCommand("crosspost", "Post ke banyak channel"),
        BotCommand("stats", "Statistik grup"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    """Main function untuk menjalankan bot"""
    logger.info("Starting TeleTools Bot...")

    # Build application
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Initialize handlers
    antispam = AntiSpamHandler(db)
    welcome = WelcomeHandler(db)
    scraper = ScraperHandler(db)
    autoreply = AutoReplyHandler(db)
    autoposter = AutoPosterHandler(db, app)
    crosspost = CrossPostHandler(db)
    analytics = AnalyticsHandler(db)

    # Basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Anti-Spam handlers
    app.add_handler(CommandHandler("antispam", antispam.command))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND,
        antispam.check_message
    ), group=1)

    # Welcome handlers
    app.add_handler(CommandHandler("welcome", welcome.command))
    app.add_handler(CommandHandler("setwelcome", welcome.set_message))
    app.add_handler(ChatMemberHandler(welcome.greet, ChatMemberHandler.CHAT_MEMBER))

    # Scraper handlers
    app.add_handler(CommandHandler("scrape", scraper.scrape))
    app.add_handler(CommandHandler("export", scraper.export))

    # Auto-Reply handlers
    app.add_handler(CommandHandler("autoreply", autoreply.command))
    app.add_handler(CommandHandler("setreply", autoreply.set_message))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
        autoreply.handle_private_message
    ), group=2)

    # Auto-Poster handlers
    app.add_handler(CommandHandler("schedule", autoposter.schedule))
    app.add_handler(CommandHandler("listschedule", autoposter.list_schedules))
    app.add_handler(CommandHandler("cancelschedule", autoposter.cancel))

    # Cross-Post handlers
    app.add_handler(CommandHandler("addchannel", crosspost.add_channel))
    app.add_handler(CommandHandler("removechannel", crosspost.remove_channel))
    app.add_handler(CommandHandler("crosspost", crosspost.post))
    app.add_handler(CommandHandler("channels", crosspost.list_channels))

    # Analytics handlers
    app.add_handler(CommandHandler("stats", analytics.stats))
    app.add_handler(CommandHandler("topusers", analytics.top_users))
    app.add_handler(MessageHandler(
        filters.ALL & filters.ChatType.GROUPS,
        analytics.track_message
    ), group=3)
    app.add_handler(ChatMemberHandler(analytics.track_member_change, ChatMemberHandler.CHAT_MEMBER), group=4)

    # Callback query handler (untuk inline buttons)
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Run bot
    logger.info("TeleTools Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


async def handle_callback(update: Update, context):
    """Handle semua callback query dari inline buttons"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu_antispam":
        await query.message.reply_html("🛡 Gunakan /antispam untuk pengaturan anti-spam")
    elif data == "menu_welcome":
        await query.message.reply_html("👋 Gunakan /welcome untuk pengaturan welcome")
    elif data == "menu_scraper":
        await query.message.reply_html("📋 Gunakan /scrape untuk scrape member")
    elif data == "menu_autoreply":
        await query.message.reply_html("💬 Gunakan /autoreply untuk pengaturan auto-reply")
    elif data == "menu_autoposter":
        await query.message.reply_html("📮 Gunakan /schedule untuk jadwalkan posting")
    elif data == "menu_crosspost":
        await query.message.reply_html("📡 Gunakan /crosspost untuk post ke banyak channel")
    elif data == "menu_analytics":
        await query.message.reply_html("📊 Gunakan /stats untuk lihat statistik")


if __name__ == "__main__":
    main()

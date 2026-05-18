# 🤖 TeleTools - All-in-One Telegram Bot

Bot Telegram lengkap dengan berbagai fitur manajemen grup, otomasi, dan analytics.

## ✨ Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 🛡 **Anti-Spam** | Filter spam otomatis di grup (keyword, flood, link) |
| 👋 **Welcome** | Sambut member baru secara otomatis |
| 📋 **Member Scraper** | Ambil daftar member dari grup, export ke CSV/JSON/TXT |
| 💬 **Auto-Reply** | Balas pesan otomatis di DM bot |
| 📮 **Auto-Poster** | Jadwalkan & posting otomatis ke channel/grup |
| 📡 **Cross-Post** | Post ke banyak channel sekaligus |
| 📊 **Analytics** | Statistik member, engagement, dan growth |

## 📋 Prasyarat

- Python 3.9+
- Bot Token dari [@BotFather](https://t.me/BotFather)
- (Opsional) API ID & Hash dari [my.telegram.org](https://my.telegram.org)

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/hujanesyui-ux/teletools.git
cd teletools
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi

Edit file `bot/config.py` atau set environment variables:

```bash
export BOT_TOKEN="your_bot_token_here"
export API_ID="your_api_id"
export API_HASH="your_api_hash"
```

Tambahkan User ID kamu ke `ADMIN_IDS` di `bot/config.py`:

```python
ADMIN_IDS = [
    123456789,  # Ganti dengan User ID kamu
]
```

### 4. Jalankan Bot

```bash
cd bot
python main.py
```

## 📖 Perintah

### 🛡 Anti-Spam
| Command | Fungsi |
|---------|--------|
| `/antispam on` | Aktifkan anti-spam |
| `/antispam off` | Nonaktifkan anti-spam |
| `/antispam settings` | Lihat pengaturan |

### 👋 Welcome
| Command | Fungsi |
|---------|--------|
| `/welcome on` | Aktifkan welcome message |
| `/welcome off` | Nonaktifkan welcome message |
| `/setwelcome [teks]` | Atur pesan welcome |

**Variabel yang tersedia:**
- `{mention}` - Mention user
- `{name}` - Nama user
- `{username}` - Username
- `{chat_title}` - Nama grup
- `{member_count}` - Jumlah member

### 📋 Member Scraper
| Command | Fungsi |
|---------|--------|
| `/scrape` | Scrape member dari grup |
| `/export csv` | Export ke CSV |
| `/export json` | Export ke JSON |
| `/export txt` | Export ke TXT |

### 💬 Auto-Reply
| Command | Fungsi |
|---------|--------|
| `/autoreply on` | Aktifkan auto-reply |
| `/autoreply off` | Nonaktifkan auto-reply |
| `/setreply [teks]` | Atur pesan auto-reply |

### 📮 Auto-Poster
| Command | Fungsi |
|---------|--------|
| `/schedule [tanggal] [jam] [pesan]` | Jadwalkan posting |
| `/listschedule` | Lihat jadwal aktif |
| `/cancelschedule [id]` | Batalkan jadwal |

**Contoh:** `/schedule 2025-01-01 08:00 Selamat Tahun Baru!`

### 📡 Cross-Post
| Command | Fungsi |
|---------|--------|
| `/addchannel [channel_id]` | Tambah channel |
| `/removechannel [channel_id]` | Hapus channel |
| `/crosspost [teks]` | Post ke semua channel |
| `/channels` | Lihat daftar channel |

### 📊 Analytics
| Command | Fungsi |
|---------|--------|
| `/stats` | Statistik hari ini |
| `/stats week` | Statistik minggu ini |
| `/stats month` | Statistik bulan ini |
| `/topusers` | Top 10 user paling aktif |

## 🏗 Struktur Project

```
teletools/
├── bot/
│   ├── main.py              # Entry point
│   ├── config.py            # Konfigurasi
│   ├── handlers/
│   │   ├── admin.py         # Admin decorator
│   │   ├── antispam.py      # Anti-spam filter
│   │   ├── welcome.py       # Welcome message
│   │   ├── scraper.py       # Member scraper
│   │   ├── autoreply.py     # Auto-reply
│   │   ├── autoposter.py    # Scheduled posting
│   │   ├── crosspost.py     # Cross-post ke channels
│   │   └── analytics.py     # Statistik & analytics
│   ├── database/
│   │   └── db.py            # SQLite database
│   ├── utils/
│   │   └── helpers.py       # Helper functions
│   └── keyboards/
│       └── inline.py        # Inline keyboards
├── requirements.txt
└── README.md
```

## ⚙️ Pengaturan Anti-Spam

Di `config.py`, kamu bisa mengatur:

```python
SPAM_KEYWORDS = ["join now", "free money", ...]  # Keyword spam
SPAM_MAX_MESSAGES_PER_MINUTE = 5                  # Max pesan/menit
SPAM_MAX_LINKS_PER_MESSAGE = 3                    # Max link/pesan
SPAM_ACTION = "mute"                              # mute/kick/ban/delete
SPAM_MUTE_DURATION = 3600                         # Durasi mute (detik)
```

## 🔒 Keamanan

- Hanya admin grup & user di `ADMIN_IDS` yang bisa menggunakan command
- Bot tidak menyimpan data sensitif
- Database SQLite lokal (tidak dikirim ke server lain)

## 📝 Catatan

- Bot perlu dijadikan **admin grup** untuk fitur anti-spam dan welcome
- Bot perlu dijadikan **admin channel** untuk fitur cross-post dan auto-poster
- Untuk scraping member lengkap, diperlukan Userbot (Telethon/Pyrogram)

## 📄 License

MIT License - Bebas digunakan dan dimodifikasi.

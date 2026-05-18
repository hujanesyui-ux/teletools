# 📘 TUTORIAL LENGKAP - TeleTools Bot

## Blueprint & Panduan Lengkap Penggunaan

---

## 📋 DAFTAR ISI

1. [Persiapan Awal](#-1-persiapan-awal)
2. [Instalasi](#-2-instalasi)
3. [Konfigurasi Bot](#-3-konfigurasi-bot)
4. [Menjalankan Bot](#-4-menjalankan-bot)
5. [Fitur Anti-Spam](#-5-fitur-anti-spam)
6. [Fitur Welcome](#-6-fitur-welcome)
7. [Fitur Member Scraper](#-7-fitur-member-scraper)
8. [Fitur Auto-Reply](#-8-fitur-auto-reply)
9. [Fitur Auto-Poster](#-9-fitur-auto-poster)
10. [Fitur Cross-Post](#-10-fitur-cross-post)
11. [Fitur Analytics](#-11-fitur-analytics)
12. [Menu Settings](#-12-menu-settings)
13. [Tips & Trik](#-13-tips--trik)
14. [Troubleshooting](#-14-troubleshooting)
15. [FAQ](#-15-faq)

---

## 🔧 1. PERSIAPAN AWAL

### Yang Dibutuhkan:

| No | Kebutuhan | Cara Dapat |
|----|-----------|------------|
| 1 | Python 3.9+ | [python.org/downloads](https://www.python.org/downloads/) |
| 2 | Bot Token | Dari @BotFather di Telegram |
| 3 | User ID | Dari @userinfobot di Telegram |
| 4 | PC/Laptop/VPS | Windows/Linux/Mac |

### Langkah 1: Install Python

1. Download Python dari https://www.python.org/downloads/
2. **PENTING:** Saat install, centang ✅ **"Add Python to PATH"**
3. Klik Install Now
4. Tunggu selesai

### Langkah 2: Buat Bot di Telegram

1. Buka Telegram, cari **@BotFather**
2. Ketik `/newbot`
3. Masukkan nama bot (contoh: `TeleTools Bot`)
4. Masukkan username bot (contoh: `myteletools_bot`)
5. BotFather akan kasih **BOT TOKEN** → Simpan ini!

```
Contoh token: 7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Langkah 3: Dapat User ID

1. Buka Telegram, cari **@userinfobot**
2. Ketik `/start`
3. Catat angka **User ID** kamu

```
Contoh user ID: 123456789
```

---

## 💻 2. INSTALASI

### Cara Otomatis (Windows):

```
1. Download/clone repository ini
2. Klik 2x file "install.bat"
3. Tunggu sampai selesai
4. Selesai!
```

### Cara Manual:

```bash
# 1. Clone repository
git clone https://github.com/hujanesyui-ux/teletools.git
cd teletools

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Struktur Folder Setelah Install:

```
teletools/
├── venv/                    ← Virtual environment (auto-generated)
├── bot/
│   ├── main.py              ← File utama bot
│   ├── config.py            ← ⚠️ EDIT FILE INI
│   ├── handlers/            ← Semua fitur bot
│   ├── database/            ← Database SQLite
│   ├── utils/               ← Helper functions
│   └── keyboards/           ← Tombol inline
├── install.bat              ← Installer otomatis
├── start.bat                ← Jalankan bot
├── requirements.txt         ← Daftar library
└── README.md                ← Dokumentasi singkat
```

---

## ⚙️ 3. KONFIGURASI BOT

### Edit file `bot/config.py`:

Buka file `bot/config.py` dengan Notepad/VS Code, lalu ubah:

```python
# 1. Masukkan Bot Token dari BotFather
BOT_TOKEN = "7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 2. Masukkan User ID kamu (bisa lebih dari 1)
ADMIN_IDS = [
    123456789,      # User ID kamu
    987654321,      # User ID admin lain (opsional)
]
```

### Konfigurasi Anti-Spam (Opsional):

```python
# Kata-kata yang dianggap spam
SPAM_KEYWORDS = [
    "join now", "free money", "click here",
    "hubungi kami", "wa.me", "bit.ly",
    # Tambah keyword spam lainnya di sini
]

# Batas pesan per menit (lebih dari ini = spam)
SPAM_MAX_MESSAGES_PER_MINUTE = 5

# Batas link per pesan
SPAM_MAX_LINKS_PER_MESSAGE = 3

# Aksi saat spam terdeteksi: "mute", "kick", "ban", "delete"
SPAM_ACTION = "mute"

# Durasi mute (dalam detik). 3600 = 1 jam
SPAM_MUTE_DURATION = 3600
```

### Konfigurasi Timezone (Opsional):

```python
# Untuk auto-poster, sesuaikan timezone
POSTER_TIMEZONE = "Asia/Jakarta"  # WIB
# POSTER_TIMEZONE = "Asia/Makassar"  # WITA
# POSTER_TIMEZONE = "Asia/Jayapura"  # WIT
```

---

## ▶️ 4. MENJALANKAN BOT

### Cara Otomatis (Windows):

```
Klik 2x file "start.bat"
```

### Cara Manual:

```bash
# Aktifkan venv dulu
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Jalankan bot
cd bot
python main.py
```

### Kalau Berhasil:

```
2025-01-01 08:00:00 - __main__ - INFO - Starting TeleTools Bot...
2025-01-01 08:00:01 - __main__ - INFO - TeleTools Bot is running!
```

### Setup Bot di Grup:

1. Buka grup Telegram kamu
2. Klik nama grup → Edit → Administrators
3. Tambahkan bot kamu sebagai **Admin**
4. Beri izin: Delete Messages, Ban Users, Invite Users

---

## 🛡 5. FITUR ANTI-SPAM

### Cara Kerja:

Bot otomatis mendeteksi spam berdasarkan:
- ⚡ **Keyword spam** (kata-kata terlarang)
- 🔗 **Terlalu banyak link** dalam 1 pesan
- 💬 **Flood** (kirim pesan terlalu cepat)
- 📝 **Pesan terlalu panjang** (copy-paste spam)
- 🔁 **Karakter berulang** (aaaaaa, !!!!!!!)
- 📢 **Promosi channel/grup** lain

### Command:

| Command | Fungsi |
|---------|--------|
| `/antispam` | Lihat status & pengaturan |
| `/antispam on` | Aktifkan anti-spam |
| `/antispam off` | Nonaktifkan anti-spam |
| `/antispam settings` | Lihat detail pengaturan |

### Contoh Penggunaan:

```
Admin: /antispam on
Bot: 🛡 Anti-spam diaktifkan! ✅

-- Spammer masuk --
Spammer: JOIN NOW FREE MONEY bit.ly/scam
Bot: 🛡 Spam terdeteksi!
     User: @spammer
     Alasan: Keyword terdeteksi: 'free money'
     Aksi: Mute 60 menit
```

### Aksi yang Tersedia:

| Aksi | Penjelasan |
|------|------------|
| `delete` | Hapus pesan spam saja |
| `mute` | Hapus + mute user (tidak bisa kirim pesan) |
| `kick` | Hapus + kick user (bisa join lagi) |
| `ban` | Hapus + ban permanen |

---

## 👋 6. FITUR WELCOME

### Cara Kerja:

Setiap ada member baru join grup, bot otomatis kirim pesan sambutan.

### Command:

| Command | Fungsi |
|---------|--------|
| `/welcome` | Lihat status & pesan saat ini |
| `/welcome on` | Aktifkan welcome message |
| `/welcome off` | Nonaktifkan welcome message |
| `/setwelcome [teks]` | Atur pesan custom |

### Variabel yang Bisa Dipakai:

| Variabel | Hasil |
|----------|-------|
| `{mention}` | Mention user (klik = buka profil) |
| `{name}` | Nama depan user |
| `{username}` | @username |
| `{chat_title}` | Nama grup |
| `{member_count}` | Jumlah member |

### Contoh:

```
/setwelcome Halo {mention}! 🎉

Selamat datang di {chat_title}!
Kamu adalah member ke-{member_count}.

Silakan baca rules dan perkenalkan diri ya! 👋
```

### Hasil:

```
Halo @JohnDoe! 🎉

Selamat datang di Komunitas Developer!
Kamu adalah member ke-1234.

Silakan baca rules dan perkenalkan diri ya! 👋
```

---

## 📋 7. FITUR MEMBER SCRAPER

### Cara Kerja:

Bot mengambil daftar member dari grup dan menyimpannya ke database.
Bisa di-export ke file CSV, JSON, atau TXT.

### Command:

| Command | Fungsi |
|---------|--------|
| `/scrape` | Mulai scraping member |
| `/export csv` | Download file CSV |
| `/export json` | Download file JSON |
| `/export txt` | Download file TXT |

### Contoh Penggunaan:

```
Admin: /scrape
Bot: 📋 Sedang scraping member... ⏳

Bot: 📋 Scraping Selesai!
     👥 Total member grup: 1500
     ✅ Admin ter-scrape: 8
     💾 Total di database: 8

Admin: /export csv
Bot: 📋 Data member: 8 orang
     [File: members_NamaGrup.csv]
```

### Format Export:

**CSV:**
```csv
User ID,Username,First Name,Last Name,Is Bot,Status,Scraped At
123456789,johndoe,John,Doe,No,administrator,2025-01-01 08:00:00
```

**JSON:**
```json
[
  {
    "user_id": 123456789,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "is_bot": false,
    "status": "administrator"
  }
]
```

### ⚠️ Catatan Penting:

Bot API hanya bisa scrape **admin** dan member yang pernah kirim pesan.
Untuk scrape **semua** member, diperlukan Userbot (Telethon/Pyrogram).

---

## 💬 8. FITUR AUTO-REPLY

### Cara Kerja:

Bot otomatis membalas pesan private (DM) yang masuk.
Berguna saat kamu offline/sibuk.

### Command:

| Command | Fungsi |
|---------|--------|
| `/autoreply` | Lihat status & pesan |
| `/autoreply on` | Aktifkan auto-reply |
| `/autoreply off` | Nonaktifkan auto-reply |
| `/setreply [teks]` | Atur pesan balasan |

### Contoh:

```
Admin: /autoreply on
Bot: 💬 Auto-reply diaktifkan! ✅

Admin: /setreply Halo! Saya sedang offline.
       Akan saya balas dalam 1-2 jam ya. 🙏
       Untuk urgent, hubungi @admin2
Bot: ✅ Auto-reply message berhasil diupdate!
```

### Fitur:

- **Cooldown**: Tidak spam reply (default 5 menit per user)
- **Custom message**: Bisa diatur sesuka hati
- **Hanya DM**: Tidak reply di grup

---

## 📮 9. FITUR AUTO-POSTER

### Cara Kerja:

Jadwalkan posting otomatis ke channel/grup di waktu tertentu.
Bot akan kirim pesan di waktu yang sudah ditentukan.

### Command:

| Command | Fungsi |
|---------|--------|
| `/schedule [tanggal] [jam] [pesan]` | Jadwalkan posting |
| `/listschedule` | Lihat semua jadwal |
| `/cancelschedule [id]` | Batalkan jadwal |

### Format Waktu:

```
/schedule YYYY-MM-DD HH:MM [pesan]
```

### Contoh:

```
Admin: /schedule 2025-06-15 08:00 Selamat pagi semua! 🌅
       Jangan lupa meeting jam 10:00 ya.

Bot: ✅ Posting dijadwalkan!
     🆔 ID: 1
     📅 Waktu: 15 Jun 2025, 08:00
     💬 Pesan: Selamat pagi semua! 🌅...

Admin: /listschedule
Bot: 📮 Jadwal Posting Aktif:
     🆔 1 | 📅 15 Jun 2025, 08:00
     💬 Selamat pagi semua! 🌅 Jangan lupa...

Admin: /cancelschedule 1
Bot: ✅ Jadwal posting #1 dibatalkan.
```

### Tips:

- Bisa jadwalkan banyak posting sekaligus
- Timezone mengikuti setting di config (default: Asia/Jakarta)
- Bot harus tetap running supaya posting terkirim

---

## 📡 10. FITUR CROSS-POST

### Cara Kerja:

Kirim 1 pesan, otomatis ter-post ke banyak channel sekaligus.
Cocok untuk yang punya banyak channel.

### Command:

| Command | Fungsi |
|---------|--------|
| `/addchannel [channel_id]` | Tambah channel |
| `/removechannel [channel_id]` | Hapus channel |
| `/channels` | Lihat daftar channel |
| `/crosspost [pesan]` | Post ke semua channel |

### Cara Dapat Channel ID:

1. Forward pesan dari channel ke **@userinfobot**
2. Atau gunakan **@RawDataBot**
3. Channel ID biasanya format: `-1001234567890`

### Contoh:

```
Admin: /addchannel -1001234567890
Bot: ✅ Channel berhasil ditambahkan!
     📡 Channel Gaming
     🆔 -1001234567890

Admin: /addchannel -1009876543210
Bot: ✅ Channel berhasil ditambahkan!
     📡 Channel Tutorial
     🆔 -1009876543210

Admin: /channels
Bot: 📡 Daftar Channel Cross-Post:
     1. Channel Gaming
        🆔 -1001234567890
     2. Channel Tutorial
        🆔 -1009876543210
     Total: 2 channel

Admin: /crosspost 🔥 Update terbaru! Cek link di bio.
Bot: 📡 Cross-Post Selesai!
     ✅ Berhasil: 2
     ❌ Gagal: 0
```

### ⚠️ Syarat:

- Bot harus jadi **admin** di semua channel target
- Bot perlu izin "Post Messages"

---

## 📊 11. FITUR ANALYTICS

### Cara Kerja:

Bot otomatis tracking semua aktivitas di grup:
- Jumlah pesan per user
- Tipe pesan (text, photo, video, dll)
- Member join & leave
- Engagement rate

### Command:

| Command | Fungsi |
|---------|--------|
| `/stats` | Statistik hari ini |
| `/stats week` | Statistik 7 hari |
| `/stats month` | Statistik 30 hari |
| `/topusers` | 10 user paling aktif |
| `/topusers [hari]` | Top users dalam X hari |

### Contoh Output /stats:

```
📊 Statistik Grup - Hari Ini

👥 Total Member: 1500
💬 Total Pesan: 342
👤 User Aktif: 45

📨 Tipe Pesan:
  💬 text: 250
  🖼 photo: 52
  🎬 video: 20
  🎭 sticker: 15
  📎 document: 5

👋 Member Activity:
  ➡️ Join: +12
  ⬅️ Leave: -3
  📈 Net: +9

📈 Engagement Rate:
  3.0% 😐 Kurang aktif
```

### Contoh Output /topusers:

```
🏆 Top 10 User Paling Aktif
Periode: 7 hari terakhir

🥇 John Doe @johndoe
    💬 156 pesan

🥈 Jane Smith @janesmith
    💬 98 pesan

🥉 Alex @alex123
    💬 67 pesan

4. Mike @mike_dev
    💬 45 pesan

...
```

---

## ⚙️ 12. MENU SETTINGS

### Cara Akses:

Ketik `/settings` di chat → Muncul menu lengkap dengan tombol.

### Tampilan Menu:

```
⚙️ SETTINGS - TeleTools Bot

Klik tombol di bawah untuk mengatur fitur:

🛡 Anti-Spam: ✅
👋 Welcome: ✅
💬 Auto-Reply: ❌
📮 Auto-Poster: ✅
📡 Cross-Post: ✅
📊 Analytics: ✅

[🛡 Anti-Spam ✅] [👋 Welcome ✅]
[💬 Auto-Reply ❌] [📮 Auto-Poster]
[📡 Cross-Post]    [📊 Analytics]
[🔑 Spam Keywords] [⚡ Spam Action]
[📝 Lihat Semua Config]
```

### Yang Bisa Dilakukan:

| Tombol | Fungsi |
|--------|--------|
| Toggle fitur | Klik untuk on/off |
| Spam Action | Pilih: delete/mute/kick/ban |
| Spam Keywords | Lihat daftar keyword |
| View Config | Lihat semua pengaturan |

### Semua Bisa Diatur Tanpa Edit File!

---

## 💡 13. TIPS & TRIK

### Anti-Spam:

```
✅ Tambah keyword spesifik untuk komunitas kamu
✅ Mulai dengan "mute" sebelum pakai "ban"
✅ Adjust max messages/menit sesuai aktivitas grup
❌ Jangan set terlalu ketat (member normal bisa kena)
```

### Welcome:

```
✅ Buat pesan singkat & informatif
✅ Sertakan link rules
✅ Pakai {mention} supaya personal
❌ Jangan terlalu panjang (member malas baca)
```

### Auto-Poster:

```
✅ Jadwalkan di jam prime time (8-10 pagi, 7-9 malam)
✅ Variasikan konten
✅ Pastikan bot tetap running 24/7 (gunakan VPS)
❌ Jangan spam posting terlalu sering
```

### Cross-Post:

```
✅ Gunakan untuk pengumuman penting
✅ Kelompokkan channel berdasarkan topik
❌ Jangan crosspost terlalu sering (subscriber bisa annoyed)
```

### Analytics:

```
✅ Cek stats mingguan untuk monitor growth
✅ Reward top users supaya makin aktif
✅ Perhatikan engagement rate
```

---

## 🔧 14. TROUBLESHOOTING

### Bot Tidak Jalan

| Masalah | Solusi |
|---------|--------|
| "Python tidak ditemukan" | Install Python & centang "Add to PATH" |
| "Module not found" | Jalankan `pip install -r requirements.txt` |
| "Invalid token" | Cek token di config.py, pastikan benar |
| Bot tidak response | Pastikan bot sudah jadi admin di grup |

### Anti-Spam Tidak Bekerja

```
1. Pastikan /antispam on sudah dijalankan
2. Bot harus jadi admin dengan izin "Delete Messages"
3. Admin grup tidak akan kena anti-spam (by design)
```

### Welcome Tidak Muncul

```
1. Pastikan /welcome on sudah dijalankan
2. Bot perlu izin khusus: di BotFather, set /setjoinrequest
3. Atau pastikan "Chat Member Updates" diaktifkan
4. Cek: bot harus admin dengan izin invite users
```

### Scheduled Post Tidak Terkirim

```
1. Bot harus tetap running (jangan ditutup)
2. Pastikan waktu di masa depan
3. Cek timezone di config.py
4. Pastikan APScheduler terinstall: pip install APScheduler
```

### Cross-Post Gagal

```
1. Bot harus admin di channel target
2. Bot perlu izin "Post Messages"
3. Cek channel ID benar (format: -100xxxxxxxxxx)
4. Pastikan bot tidak di-ban dari channel
```

### Database Error

```
1. Hapus file teletools.db (data akan reset)
2. Jalankan ulang bot (database akan dibuat otomatis)
```

---

## ❓ 15. FAQ

### Q: Apakah bot ini gratis?
**A:** Ya, 100% gratis dan open source.

### Q: Bisa jalan 24/7?
**A:** Bisa, tapi butuh VPS (server). Rekomendasi:
- Oracle Cloud Free Tier (gratis selamanya)
- DigitalOcean ($4-6/bulan)
- Contabo VPS (murah)

### Q: Aman tidak?
**A:** Ya. Bot hanya menyimpan data di database lokal (SQLite).
Tidak ada data yang dikirim ke server lain.

### Q: Bisa multi-grup?
**A:** Ya! Bot bisa dipakai di banyak grup sekaligus.
Setiap grup punya settings sendiri-sendiri.

### Q: Kalau bot mati, data hilang?
**A:** Tidak. Data tersimpan di file `teletools.db`.
Selama file itu ada, data aman.

### Q: Bisa dipakai di channel?
**A:** Ya, untuk fitur:
- Auto-Poster (jadwal posting ke channel)
- Cross-Post (post ke banyak channel)
- Analytics (tracking member join/leave)

### Q: Bagaimana deploy ke VPS Linux?

```bash
# 1. SSH ke VPS
ssh root@ip_vps

# 2. Install Python
apt update && apt install python3 python3-pip python3-venv

# 3. Clone & setup
git clone https://github.com/hujanesyui-ux/teletools.git
cd teletools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Edit config
nano bot/config.py
# Masukkan token & admin IDs

# 5. Jalankan dengan screen (supaya tetap jalan)
screen -S teletools
cd bot
python3 main.py
# Tekan Ctrl+A lalu D untuk detach
```

### Q: Bisa tambah fitur sendiri?

**A:** Tentu! Strukturnya modular:
1. Buat file baru di `bot/handlers/nama_fitur.py`
2. Buat class handler
3. Register di `bot/main.py`
4. Done!

---

## 📞 SUPPORT

- GitHub Issues: https://github.com/hujanesyui-ux/teletools/issues
- Telegram: Hubungi developer

---

## 📝 CHANGELOG

### v1.0.0 (Initial Release)
- ✅ Anti-Spam (keyword, flood, link detection)
- ✅ Welcome Message (custom + variabel)
- ✅ Member Scraper (export CSV/JSON/TXT)
- ✅ Auto-Reply (DM dengan cooldown)
- ✅ Auto-Poster (scheduled posting)
- ✅ Cross-Post (multi-channel)
- ✅ Analytics (stats, engagement, top users)
- ✅ Full Settings Menu (/settings)
- ✅ install.bat & start.bat

---

*Made with ❤️ by TeleTools Team*

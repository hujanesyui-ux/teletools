@echo off
title TeleTools Bot - Running
color 0B

echo ==========================================
echo    TeleTools - All-in-One Telegram Bot
echo ==========================================
echo.

:: Cek venv ada
if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment belum dibuat!
    echo [!] Jalankan install.bat terlebih dahulu.
    echo.
    pause
    exit /b
)

:: Aktifkan venv
call venv\Scripts\activate.bat

:: Cek token sudah diset (dari .env atau config.py)
python -c "import sys; sys.path.insert(0,'bot'); from config import BOT_TOKEN; assert BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE', 'Token belum diset'" 2>nul
if %errorlevel% neq 0 (
    echo [!] BOT_TOKEN belum diatur!
    echo [!] Buat file .env di folder ini dan isi:
    echo [!]   BOT_TOKEN=token_dari_botfather
    echo [!]   ADMIN_IDS=user_id_kamu
    echo [!] Atau edit bot\config.py langsung.
    echo.
    pause
    exit /b
)

echo [*] Menjalankan TeleTools Bot...
echo [*] Tekan Ctrl+C untuk menghentikan bot.
echo.
echo ==========================================
echo.

:: Jalankan bot
cd bot
python main.py

:: Kalau bot berhenti
echo.
echo [!] Bot berhenti.
pause

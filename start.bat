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

:: Cek token sudah diset
python -c "from bot.config import BOT_TOKEN; assert BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE', 'Token belum diset'" 2>nul
if %errorlevel% neq 0 (
    echo [!] BOT_TOKEN belum diatur!
    echo [!] Edit bot\config.py dan masukkan token dari @BotFather
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
python -m bot.main

:: Kalau bot berhenti
echo.
echo [!] Bot berhenti.
pause

@echo off
title TeleTools - Installer
color 0A

echo ==========================================
echo    TeleTools - All-in-One Telegram Bot
echo    Installer
echo ==========================================
echo.

:: Cek Python terinstall
echo [*] Mengecek Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python tidak ditemukan!
    echo [!] Download Python di: https://www.python.org/downloads/
    echo [!] Pastikan centang "Add Python to PATH" saat install.
    echo.
    pause
    exit /b
)

python --version
echo [OK] Python ditemukan!
echo.

:: Buat virtual environment
echo [*] Membuat virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment dibuat!
) else (
    echo [OK] Virtual environment sudah ada.
)
echo.

:: Aktifkan venv
echo [*] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat
echo.

:: Install dependencies
echo [*] Menginstall dependencies...
echo.
pip install --upgrade pip
pip install -r requirements.txt
echo.

:: Cek config
echo ==========================================
echo    INSTALASI SELESAI!
echo ==========================================
echo.
echo [!] LANGKAH SELANJUTNYA:
echo.
echo 1. Edit bot\config.py
echo    - Masukkan BOT_TOKEN dari @BotFather
echo    - Masukkan User ID kamu di ADMIN_IDS
echo.
echo 2. Jalankan bot dengan: start.bat
echo.
echo ==========================================
echo.
pause

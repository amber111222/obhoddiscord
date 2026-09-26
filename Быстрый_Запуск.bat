@echo off
chcp 65001 > nul
title Discord Bypass Pro - Выбор режима запуска

:: Check Administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Требуются права Администратора!
    echo Запуск от имени Администратора...
    powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

:menu
cls
echo ===============================================================================
echo                🛡️ DISCORD BYPASS PRO — ВЫБОР РЕЖИМА И ПРЕСЕТА
echo ===============================================================================
echo  [1] 🚀 Запустить GUI Приложение (Графический интерфейс 16:9 + Автоподбор)
echo  [2] ⚡ Запустить консольный обход: general (ALT) [Самый стабильный Discord]
echo  [3] 🎙️ Запустить консольный обход: general (ALT2) [Multisplit для Голоса]
echo  [4] 🌐 Запустить консольный обход: general (FAKE TLS AUTO) [Обход по TLS]
echo  [5] 🛠️ Запустить ZAPRET SERVICE MANAGER (Управление службой Windows)
echo  [6] ❌ Остановить все процессы обхода (winws / WinDivert)
echo  [0] Выход
echo ===============================================================================
set /p choice="Выберите пункт [0-6]: "

if "%choice%"=="1" goto run_gui
if "%choice%"=="2" goto run_alt
if "%choice%"=="3" goto run_alt2
if "%choice%"=="4" goto run_fake
if "%choice%"=="5" goto run_service
if "%choice%"=="6" goto stop_all
if "%choice%"=="0" exit /b
goto menu

:run_gui
echo Запуск GUI приложения...
start "" "%~dp0DiscordBypass.exe"
exit /b

:run_alt
echo Запуск пресета general (ALT)...
call "%~dp0zapret\general (ALT).bat"
goto menu

:run_alt2
echo Запуск пресета general (ALT2)...
call "%~dp0zapret\general (ALT2).bat"
goto menu

:run_fake
echo Запуск пресета general (FAKE TLS AUTO)...
call "%~dp0zapret\general (FAKE TLS AUTO).bat"
goto menu

:run_service
echo Открытие Zapret Service Manager...
call "%~dp0zapret\service.bat"
goto menu

:stop_all
echo Остановка процессов...
taskkill /F /IM winws.exe >nul 2>&1
net stop WinDivert >nul 2>&1
sc delete WinDivert >nul 2>&1
echo [OK] Все процессы и драйверы остановлены.
timeout /t 2 >nul
goto menu

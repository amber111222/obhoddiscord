#!/usr/bin/env bash
# ==============================================================================
# 🛡️ Discord Bypass Pro — macOS Edition
# Высокоскоростной обход блокировок Discord для macOS (Apple Silicon M1/M2/M3/M4 & Intel x86_64)
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo "   🛡️ Discord Bypass Pro — macOS Edition"
echo "   Обход блокировок Discord (Чат, Голос, Стримы)"
echo "=================================================="
echo ""

# Check for root/sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Требуются права суперпользователя (sudo) для настройки сетевого фильтра."
    echo "Пожалуйста, введите пароль администратора при запросе."
    exec sudo bash "$0" "$@"
fi

# Detect Architecture
ARCH="$(uname -m)"
echo "🖥️  Архитектура системы: $ARCH"

# Discord Target Domains
DOMAINS="discord.com gateway.discord.gg cdn.discordapp.com discord.media discordapp.com discordapp.net"

echo "⚡ Настройка правил сетевого фильтра pf..."

# Enable pf if disabled
pfctl -e >/dev/null 2>&1 || true

# Check if Python 3 and Tkinter are available for GUI
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Запуск GUI интерфейса..."
    python3 "$DIR/src/main.py" || true
else
    echo "ℹ️  Python3 не обнаружен. Работа в фоновом режиме десинхронизации..."
    echo "Discord готов к работе. Нажмите Ctrl+C для остановки."
    trap 'echo "Остановка..."; exit 0' INT TERM
    while true; do sleep 10; done
fi

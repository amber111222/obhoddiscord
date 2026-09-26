<div align="center">

# 🛡️ Discord Bypass Pro (Zapret Edition)
### Высокоскоростной обход блокировки Discord для Windows 10/11, Windows 7/8.1 и macOS

[![Latest Release](https://img.shields.io/github/v/release/amber111222/obhoddiscord?color=23A55A&label=Релиз%20v1.0&style=for-the-badge)](https://github.com/amber111222/obhoddiscord/releases/latest)
[![OS Support](https://img.shields.io/badge/ОС-Windows%2010%2F11%20%7C%20macOS-5865F2?style=for-the-badge)](https://github.com/amber111222/obhoddiscord)
[![Discord Voice](https://img.shields.io/badge/Discord-Voice%20%26%20RTC%20Fixed-57F287?style=for-the-badge)](https://github.com/amber111222/obhoddiscord)
[![Zapret Core](https://img.shields.io/badge/Zapret%20Core-v1.10.3-EB459E?style=for-the-badge)](https://github.com/bol-van/zapret)
[![Downloads](https://img.shields.io/github/downloads/amber111222/obhoddiscord/total?color=FEE75C&style=for-the-badge)](https://github.com/amber111222/obhoddiscord/releases)

<br/>

**Полное восстановление работы Discord в России:** текстовые чаты, голосовые каналы WebRTC (RTC Connecting), демонстрация экрана, видеозвонки и вложения. Автоматический подбор лучшего сервера и пресета прямо при запуске!

[📥 **СКАЧАТЬ DISCORDBYPASS.EXE (v1.0)**](https://github.com/amber111222/obhoddiscord/releases/download/v1.0/DiscordBypass.exe) • [💬 Инструкция по запуску](#-инструкция-по-запуску) • [🍎 Версия для macOS](#-macos)

</div>

---

## ⚡ БЫСТРЫЙ СТАРТ (Без сборки!)

Вам **не нужно ничего компилировать или устанавливать Python**! Готовая программа уже собрана:

* 🪟 **Для Windows 10/11 (x64):** [👉 **Скачать DiscordBypass.exe**](https://github.com/amber111222/obhoddiscord/releases/download/v1.0/DiscordBypass.exe) *(Автономный GUI 16:9 со встроенным бенчмарком)*
* 🛠️ **Для Windows (все версии / мульти-меню):** запустите [`Быстрый_Запуск.bat`](Быстрый_Запуск.bat) от имени Администратора.
* 🍎 **Для macOS (Apple Silicon M1-M4 & Intel):** запустите [`macos_start.sh`](macos_start.sh).

---

## 🖥️ Поддерживаемые версии ОС

| Операционная система | Статус | Способ запуска | Особенности |
| :--- | :---: | :--- | :--- |
| **Windows 11 (x64)** | ✅ Полная поддержка | `DiscordBypass.exe` или `Быстрый_Запуск.bat` | Автономный GUI 16:9, авто-UAC, полный автоподбор |
| **Windows 10 (x64)** | ✅ Полная поддержка | `DiscordBypass.exe` или `Быстрый_Запуск.bat` | Автономный GUI 16:9, WinDivert 64-bit |
| **Windows 8.1 / 8 (x64)** | ✅ Поддерживается | `Быстрый_Запуск.bat` -> выбор пресета | Консольный режим и служба Zapret |
| **Windows 7 SP1 (x64)** | ✅ Поддерживается | `Быстрый_Запуск.bat` -> пункт [2] или [5] | Режим совместимости WinDivert |
| **macOS (M1 / M2 / M3 / M4)** | ✅ Поддерживается | `sudo bash macos_start.sh` | Apple Silicon ARM64, системный фильтр pf / nfqws |
| **macOS (Intel x86_64)** | ✅ Поддерживается | `sudo bash macos_start.sh` | Intel macOS, поддержка GUI и фонового режима |

---

## ✨ Возможности

- 🚀 **Полный обход Discord:** восстанавливает доступ к сообщениям, вложениям, голосовым комнатам (Voice RTC) и демонстрации экрана.
- 🔍 **Автоподбор при старте:** программа автоматически тестирует ключевые шлюзы Discord (API, Gateway, Media, CDN) и подбирает самый быстрый пресет под вашего интернет-провайдера.
- 📺 **Современный 16:9 Dashboard:** широкоформатный двухколоночный интерфейс на CustomTkinter (1152×648).
- ⚡ **23 готовых пресета Zapret:** тонко настроенные стратегии десинхронизации пакетов (`ALT`, `Voice Fast`, `ALT2 Multisplit`, `ALT6`, `FAKE TLS AUTO` и др.).
- ⏱ **Живая статистика:** таймер аптайма, мониторинг PID процесса и сетевой пинг.
- 📡 **Встроенная диагностика:** проверка доступности API, Gateway, CDN и Media/WebRTC серверов в один клик.

---

## 🚀 Инструкция по запуску

### 🪟 Windows (10/11):
1. Скачайте файл **`DiscordBypass.exe`** ([Скачать v1.0](https://github.com/amber111222/obhoddiscord/releases/download/v1.0/DiscordBypass.exe)).
2. Запустите **`DiscordBypass.exe`** (он автоматически запросит права Администратора).
3. Приложение автоматически проведет быстрый тест серверов Discord, найдет наилучший пресет под вашего провайдера и активирует обход.
4. Запустите Discord и общайтесь без лагов и задержек!

> **Альтернатива:** Если не запускается GUI, используйте [`Быстрый_Запуск.bat`](Быстрый_Запуск.bat) — интерактивное меню с выбором лучших пресетов (`ALT`, `ALT2`, `FAKE TLS`) и службы Windows.

### 🍎 macOS:
1. Клонируйте или скачайте репозиторий:
   ```bash
   git clone https://github.com/amber111222/obhoddiscord.git
   cd obhoddiscord
   ```
2. Разрешите запуск скрипта и запустите с правами суперпользователя:
   ```bash
   chmod +x macos_start.sh
   sudo bash macos_start.sh
   ```
3. Скрипт настроит правила сетевого фильтра и запустит обход для Discord!

---

## 📂 Структура репозитория

```text
obhoddiscord/
├── DiscordBypass.exe       # 🚀 Готовая программа для Windows 10/11 (скачай и запусти!)
├── Быстрый_Запуск.bat      # ⚡ Мульти-меню выбора версий и пресетов для Windows
├── macos_start.sh          # 🍎 Скрипт запуска для macOS (Apple Silicon & Intel)
├── README.md               # Документация и инструкции
├── zapret/                 # Драйверы WinDivert, бинарники winws и пресеты
└── src/                    # Исходный код (кроссплатформенный)
    ├── app.py              # GUI интерфейс 16:9 на CustomTkinter
    ├── engine.py           # Движок управления процессом (Windows/macOS)
    ├── autodetect.py       # Кроссплатформенный бенчмарк и автоподбор
    ├── presets.py          # Загрузка и приоритизация 23 пресетов
    ├── main.py             # Точка входа
    └── build_exe.py        # Скрипт сборки PyInstaller
```

---

## 🛠 Для разработчиков (сборка из исходников)

```bash
# Установка зависимостей
pip install customtkinter pyinstaller

# Сборка исполняемого файла под Windows
python src/build_exe.py
```

---

## 🔍 Теги и ключевые слова (Поиск / Search Index)

<details>
<summary><b>Показать список поддерживаемых поисковых запросов и тегов</b></summary>

### 🇷🇺 Поисковые запросы (RU):
`обход дискорд`, `обход блокировки дискорд`, `дискорд не работает`, `дискорд голосовой чат`, `дискорд войс не работает`, `бесконечное подключение rtc`, `подключение к rtc discord`, `дискорд ркн`, `как починить дискорд`, `дискорд запрет`, `zapret дискорд`, `zapret discord`, `обход дискорда 2024`, `обход дискорда 2025`, `обход дискорда 2026`, `goodbyedpi дискорд`, `goodbyedpi discord voice`, `обход блокировки discord windows 10 11`, `дискорд макос обход`, `discord bypass macos`, `discord fix russia`, `antizapret discord`, `ютуб и дискорд обход`, `дискорд exe скачать`, `программа для обхода дискорда`, `дискорд войс фикс`, `роскомнадзор дискорд обход`, `десинхронизация dpi discord`, `winws discord`, `windivert discord`.

### 🇬🇧 Search Keywords (EN):
`discord bypass`, `discord unblock`, `discord fix`, `discord voice fix`, `discord rtc connecting fix`, `discord russia bypass`, `discord rkn bypass`, `zapret discord`, `goodbyedpi discord`, `discord bypass windows 11`, `discord bypass macos`, `discord dpi bypass`, `discord censorship bypass`, `windivert discord`, `discord voice channels not working`, `discord stream black screen fix`, `discord auto benchmark`, `discord bypass exe download`.

</details>

---

## ⚖️ Лицензия

Проект распространяется исключительно в образовательных целях для исследования протоколов передачи данных и работы сетевых стеков. Ядро обхода основано на открытом проекте [Zapret](https://github.com/bol-van/zapret).

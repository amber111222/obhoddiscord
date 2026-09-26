<div align="center">

# 🛡️ Обход Дискорд / Discord Bypass Pro [Zapret • Голос • Чат • RTC • РКН]
### Лучший инструмент для обхода блокировки Discord в России (Windows 10/11, 7/8 и macOS)

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

## 🏷️ Теги на русском (Russian Tags & Keywords)

### 📌 Хештеги для быстрого поиска:
`#обходдискорда` `#дискорд` `#дискордвойс` `#дискордобход` `#обходдискорд` `#обходблокировкидискорд` `#дискорднеработает` `#дискордркн` `#запретдискорд` `#дискордзапрет` `#антизапрет` `#дискордроссия` `#дискордвойснеработает` `#подключениекrtc` `#бесконечноеподключениеrtc` `#дискордфикс` `#дискорд2026` `#дискорд2025` `#дискордскачать` `#обходзамедления` `#гудбайдпи` `#дискорддесинхронизация` `#обходdiscord` `#дискордмакос` `#дискордвинда` `#дискордстрим` `#войсчатдискорд`

### 🔑 Популярные поисковые фразы (Яндекс, Google, GitHub):
* **Обход блокировки Discord в России:** *обход дискорд, как обойти блокировку дискорда, дискорд обход блокировки россия, рабочий обход дискорда, обход блокировки дискорда 2026, программа для обхода блокировки дискорда без впн, обход дискорда exe скачать, скачать обход дискорда, бесплатный обход дискорда.*
* **Голосовые каналы, звонки и WebRTC:** *дискорд бесконечное подключение к rtc, дискорд войс не работает, не слышно в дискорде, дискорд подключение к голосовому каналу зависло, fix discord rtc connecting, починить войс в дискорде, дискорд не подключается к войсу, черный экран стрима дискорд.*
* **Zapret, GoodCheck и DPI:** *запрет дискорд, zapret discord, zapret для дискорда, обход замедления дискорда, автоподбор пресетов zapret, winws discord, windivert discord, настройка запрета под дискорд, готовый exe запрет дискорд, zapret gui.*
* **Операционные системы:** *обход дискорда windows 11, обход дискорда windows 10, обход дискорда macos m1 m2 m3, дискорд на маке обход блокировки, дискорд для виндовс 10 скачать обход.*

---

## 🔍 English Search Index (Global Search)

`discord bypass`, `discord unblock`, `discord fix`, `discord voice fix`, `discord rtc connecting fix`, `discord russia bypass`, `discord rkn bypass`, `zapret discord`, `goodbyedpi discord`, `discord bypass windows 11`, `discord bypass macos`, `discord dpi bypass`, `discord censorship bypass`, `windivert discord`, `discord voice channels not working`, `discord stream black screen fix`, `discord auto benchmark`, `discord bypass exe download`.

---

## ⚖️ Лицензия

Проект распространяется исключительно в образовательных целях для исследования протоколов передачи данных и работы сетевых стеков. Ядро обхода основано на открытом проекте [Zapret](https://github.com/bol-van/zapret).

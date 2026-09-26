import os
import sys
import time
import threading
import webbrowser
import subprocess
import customtkinter as ctk
from tkinter import messagebox

from engine import ZapretEngine
from presets import get_preset_list, get_preset
from autodetect import AutoDetector

# Set theme and appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DiscordBypassApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Обход Дискорд Pro [Discord Bypass] — Zapret, Голос, Чат, RTC")
        
        # Exact 16:9 Widescreen aspect ratio (1152x648)
        self.geometry("1152x648")
        self.minsize(1024, 576)

        # Base directory
        if getattr(sys, 'frozen', False):
            self.app_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))

        # Set Icon if exists
        if sys.platform.startswith("win"):
            ico_candidates = [
                os.path.join(self.app_dir, "icon.ico"),
                os.path.join(os.path.dirname(self.app_dir), "icon.ico"),
                os.path.join(self.app_dir, "src", "icon.ico"),
            ]
            for ico_path in ico_candidates:
                if os.path.exists(ico_path):
                    try:
                        self.iconbitmap(ico_path)
                        break
                    except Exception:
                        pass

        # Backend Engine and AutoDetector
        self.engine = ZapretEngine(base_dir=self.app_dir)
        self.autodetector = AutoDetector(self.engine)

        # Presets data
        self.presets = get_preset_list()
        self.preset_ids = [p[0] for p in self.presets]
        self.preset_map = {p[0]: p for p in self.presets}

        # App state variables
        self.selected_preset_id = ctk.StringVar(value="general (ALT)")
        self.uptime_var = ctk.StringVar(value="00:00:00")
        self.pid_var = ctk.StringVar(value="—")
        self.preset_label_var = ctk.StringVar(value="general (ALT)")
        self.ping_status_var = ctk.StringVar(value="— мс")
        self.autodetect_status = ctk.StringVar(value="Автоподбор сервера и лучшего обхода запускается...")

        # Switches
        self.quick_test_var = ctk.BooleanVar(value=True) # True = top 6, False = top 14

        # Build 16:9 UI layout
        self._build_ui()

        # Check Admin Rights
        self._check_admin_rights()

        # Engine logger hook
        self.engine.add_log_callback(self._on_engine_log)

        # Periodic timer for uptime and status polling
        self._update_timer()

        # Protocol for clean window closing
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Auto-start server autodetection immediately on app launch if running as admin
        if self.engine.is_admin():
            self.after(400, self._on_start_autodetect)

    def _check_admin_rights(self):
        if not self.engine.is_admin():
            self.admin_badge.configure(
                text="⚠️ Требуются права Администратора",
                fg_color="#ED4245",
                hover_color="#BA3033",
                cursor="hand2"
            )
            self.admin_badge.bind("<Button-1>", lambda e: self._request_elevation())
        else:
            self.admin_badge.configure(
                text="🛡️ Права Администратора: Активны",
                fg_color="#23A55A",
                hover_color="#23A55A",
                cursor=""
            )

    def _request_elevation(self):
        if self.engine.elevate():
            self.destroy()
            sys.exit(0)
        else:
            messagebox.showwarning("Внимание", "Не удалось запросить права Администратора.")

    def _build_ui(self):
        self.configure(fg_color="#111214")

        # =========================================================================
        # 1. TOP HEADER (Sleek Horizontal Bar)
        # =========================================================================
        self.header_frame = ctk.CTkFrame(self, fg_color="#1E1F22", corner_radius=0, height=68)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        header_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_left.pack(side="left", padx=24, pady=10)

        title_lbl = ctk.CTkLabel(
            header_left,
            text="🛡️ ОБХОД ДИСКОРД PRO [DISCORD BYPASS]",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            header_left,
            text="Обход блокировки Discord (Голос, Чат, Стримы, RTC, РКН) • Zapret Core v1.10.3 • Windows & macOS",
            font=ctk.CTkFont(size=12),
            text_color="#949BA4"
        )
        subtitle_lbl.pack(anchor="w")

        header_right = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_right.pack(side="right", padx=24, pady=10)

        self.status_badge = ctk.CTkLabel(
            header_right,
            text="⚫  ОБХОД ВЫКЛЮЧЕН",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2B2D31",
            text_color="#F2F3F5",
            corner_radius=14,
            padx=16,
            pady=6
        )
        self.status_badge.pack(side="right", padx=(10, 0))

        self.admin_badge = ctk.CTkButton(
            header_right,
            text="Проверка прав...",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=30,
            corner_radius=15
        )
        self.admin_badge.pack(side="right")

        # =========================================================================
        # 2. MAIN 16:9 TWO-COLUMN BODY
        # =========================================================================
        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.pack(fill="both", expand=True, padx=20, pady=14)

        # LEFT COLUMN (44% width: Power, Live Stats, Auto-Detection)
        self.left_col = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # RIGHT COLUMN (56% width: Preset Menu, Diagnostics, Live Terminal)
        self.right_col = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # -------------------------------------------------------------------------
        # LEFT COLUMN CARDS
        # -------------------------------------------------------------------------
        # CARD 1: Power & Live Stats
        self.power_card = ctk.CTkFrame(self.left_col, fg_color="#1E1F22", corner_radius=14)
        self.power_card.pack(fill="x", pady=(0, 12))

        p_header = ctk.CTkFrame(self.power_card, fg_color="transparent")
        p_header.pack(fill="x", padx=18, pady=(14, 6))

        p_title = ctk.CTkLabel(
            p_header,
            text="⚡ ПАНЕЛЬ УПРАВЛЕНИЯ",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F2F3F5"
        )
        p_title.pack(side="left")

        # Giant High-Contrast Toggle Button
        self.btn_toggle = ctk.CTkButton(
            self.power_card,
            text="▶  ВКЛЮЧИТЬ ОБХОД ДИСКОРДА",
            font=ctk.CTkFont(size=17, weight="bold"),
            height=52,
            corner_radius=10,
            fg_color="#5865F2",
            hover_color="#4752C4",
            command=self._on_toggle_clicked
        )
        self.btn_toggle.pack(fill="x", padx=18, pady=(4, 12))

        # Live Metrics Grid (3 Stat Tiles)
        stats_frame = ctk.CTkFrame(self.power_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=18, pady=(0, 14))

        # Tile 1: Uptime
        t1 = ctk.CTkFrame(stats_frame, fg_color="#2B2D31", corner_radius=10, height=56)
        t1.pack(side="left", fill="both", expand=True, padx=(0, 6))
        t1.pack_propagate(False)
        ctk.CTkLabel(t1, text="ВРЕМЯ РАБОТЫ", font=ctk.CTkFont(size=10, weight="bold"), text_color="#949BA4").pack(pady=(6, 0))
        self.lbl_uptime = ctk.CTkLabel(t1, textvariable=self.uptime_var, font=ctk.CTkFont(size=14, weight="bold"), text_color="#23A55A")
        self.lbl_uptime.pack()

        # Tile 2: PID
        t2 = ctk.CTkFrame(stats_frame, fg_color="#2B2D31", corner_radius=10, height=56)
        t2.pack(side="left", fill="both", expand=True, padx=3)
        t2.pack_propagate(False)
        ctk.CTkLabel(t2, text="ПРОЦЕСС (PID)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#949BA4").pack(pady=(6, 0))
        self.lbl_pid = ctk.CTkLabel(t2, textvariable=self.pid_var, font=ctk.CTkFont(size=14, weight="bold"), text_color="#00A8FC")
        self.lbl_pid.pack()

        # Tile 3: Active Preset
        t3 = ctk.CTkFrame(stats_frame, fg_color="#2B2D31", corner_radius=10, height=56)
        t3.pack(side="left", fill="both", expand=True, padx=(6, 0))
        t3.pack_propagate(False)
        ctk.CTkLabel(t3, text="АКТИВНЫЙ ПРЕСЕТ", font=ctk.CTkFont(size=10, weight="bold"), text_color="#949BA4").pack(pady=(6, 0))
        self.lbl_active_preset = ctk.CTkLabel(t3, textvariable=self.preset_label_var, font=ctk.CTkFont(size=13, weight="bold"), text_color="#FEE75C")
        self.lbl_active_preset.pack()

        # CARD 2: Smart Auto-Optimization (Benchmark)
        self.auto_card = ctk.CTkFrame(self.left_col, fg_color="#1E1F22", corner_radius=14)
        self.auto_card.pack(fill="both", expand=True)

        a_title = ctk.CTkLabel(
            self.auto_card,
            text="⚡ АВТООПРЕДЕЛЕНИЕ ЛУЧШЕГО ПРЕСЕТА",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F2F3F5"
        )
        a_title.pack(anchor="w", padx=18, pady=(14, 4))

        a_desc = ctk.CTkLabel(
            self.auto_card,
            text="Автоматически тестирует живые сервера Discord (Web, Gateway, RTC Voice) на задержку и активирует идеальный пресет для вашего провайдера.",
            font=ctk.CTkFont(size=11),
            text_color="#949BA4",
            wraplength=440,
            justify="left"
        )
        a_desc.pack(anchor="w", padx=18, pady=(0, 10))

        auto_controls = ctk.CTkFrame(self.auto_card, fg_color="transparent")
        auto_controls.pack(fill="x", padx=18, pady=(0, 8))

        self.btn_autodetect = ctk.CTkButton(
            auto_controls,
            text="🚀 Начать тест пресетов",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#23A55A",
            hover_color="#1F8B4C",
            height=36,
            command=self._on_start_autodetect
        )
        self.btn_autodetect.pack(side="left", padx=(0, 12))

        self.switch_quick = ctk.CTkSwitch(
            auto_controls,
            text="Быстрый тест (Топ 6)",
            variable=self.quick_test_var,
            font=ctk.CTkFont(size=12),
            progress_color="#5865F2"
        )
        self.switch_quick.pack(side="left")

        self.progress_bar = ctk.CTkProgressBar(self.auto_card, height=8, corner_radius=4, progress_color="#5865F2")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=18, pady=(6, 6))

        self.lbl_autostatus = ctk.CTkLabel(
            self.auto_card,
            textvariable=self.autodetect_status,
            font=ctk.CTkFont(size=11),
            text_color="#B5BAC1",
            wraplength=440,
            justify="left"
        )
        self.lbl_autostatus.pack(anchor="w", padx=18, pady=(0, 14))

        # -------------------------------------------------------------------------
        # RIGHT COLUMN CARDS
        # -------------------------------------------------------------------------
        # CARD 3: Preset Selector («МЕНЮ ЗАПРЕТА»)
        self.menu_card = ctk.CTkFrame(self.right_col, fg_color="#1E1F22", corner_radius=14)
        self.menu_card.pack(fill="x", pady=(0, 12))

        m_header = ctk.CTkFrame(self.menu_card, fg_color="transparent")
        m_header.pack(fill="x", padx=18, pady=(14, 6))

        m_title = ctk.CTkLabel(
            m_header,
            text="⚙️ МЕНЮ ЗАПРЕТА (КОНФИГУРАЦИИ ОБХОДА)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F2F3F5"
        )
        m_title.pack(side="left")

        # Combobox
        self.preset_combo = ctk.CTkComboBox(
            self.menu_card,
            values=[p[1] for p in self.presets],
            height=38,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
            corner_radius=8,
            command=self._on_preset_dropdown_change
        )
        self.preset_combo.set(self.presets[0][1])
        self.preset_combo.pack(fill="x", padx=18, pady=(0, 8))

        # Quick preset chips
        chips_frame = ctk.CTkFrame(self.menu_card, fg_color="transparent")
        chips_frame.pack(fill="x", padx=18, pady=(0, 8))

        chips = [
            ("general (ALT)", "ALT ★ Реком."),
            ("Discord Voice & Chat Fast", "Voice Fast ⚡"),
            ("general (ALT2)", "ALT2 Multisplit"),
            ("general (ALT6)", "ALT6"),
            ("general (FAKE TLS AUTO)", "FAKE TLS")
        ]
        for pid, label in chips:
            btn = ctk.CTkButton(
                chips_frame,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                height=26,
                corner_radius=13,
                fg_color="#2B2D31",
                hover_color="#3F4147",
                command=lambda p=pid: self._select_preset_by_id(p)
            )
            btn.pack(side="left", padx=(0, 6))

        # Preset Description Box
        self.desc_box = ctk.CTkFrame(self.menu_card, fg_color="#18191C", corner_radius=8)
        self.desc_box.pack(fill="x", padx=18, pady=(0, 14))

        self.lbl_preset_desc = ctk.CTkLabel(
            self.desc_box,
            text=self.presets[0][2],
            font=ctk.CTkFont(size=11),
            text_color="#DBDEE1",
            justify="left",
            wraplength=570
        )
        self.lbl_preset_desc.pack(anchor="w", padx=12, pady=10)

        # CARD 4: Diagnostics and Live Terminal Log
        self.diag_card = ctk.CTkFrame(self.right_col, fg_color="#1E1F22", corner_radius=14)
        self.diag_card.pack(fill="both", expand=True)

        diag_top = ctk.CTkFrame(self.diag_card, fg_color="transparent")
        diag_top.pack(fill="x", padx=18, pady=(12, 6))

        d_title = ctk.CTkLabel(
            diag_top,
            text="📡 ДИАГНОСТИКА СВЯЗИ И ЖУРНАЛ",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F2F3F5"
        )
        d_title.pack(side="left")

        # Action Buttons row
        btn_row = ctk.CTkFrame(self.diag_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 8))

        self.btn_ping = ctk.CTkButton(
            btn_row,
            text="📡 Проверить пинг Discord",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2B2D31",
            hover_color="#3F4147",
            height=30,
            command=self._test_discord_now
        )
        self.btn_ping.pack(side="left", padx=(0, 8))

        self.btn_open_discord = ctk.CTkButton(
            btn_row,
            text="💬 Запустить Discord",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#5865F2",
            hover_color="#4752C4",
            height=30,
            command=self._launch_discord
        )
        self.btn_open_discord.pack(side="left", padx=(0, 8))

        self.btn_clear_log = ctk.CTkButton(
            btn_row,
            text="🗑 Очистить",
            font=ctk.CTkFont(size=11),
            fg_color="#2B2D31",
            hover_color="#3F4147",
            height=30,
            width=70,
            command=self._clear_log
        )
        self.btn_clear_log.pack(side="right")

        # Live Textbox Console
        self.txt_log = ctk.CTkTextbox(
            self.diag_card,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            fg_color="#18191C",
            text_color="#B5BAC1"
        )
        self.txt_log.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        # Initial Log Message
        self._log("⚡ Система готова. Режим: Обход Discord (Голос + Чат + Стримы).")
        self._log(f"📋 Текущая конфигурация: {self.selected_preset_id.get()}")

    def _on_preset_dropdown_change(self, display_name):
        for pid, name, desc in self.presets:
            if name == display_name:
                self.selected_preset_id.set(pid)
                self.preset_label_var.set(pid)
                self.lbl_preset_desc.configure(text=desc)
                self._log(f"Выбран пресет: {name}")
                if self.engine.is_running():
                    self._start_bypass()
                break

    def _select_preset_by_id(self, pid):
        self.selected_preset_id.set(pid)
        self.preset_label_var.set(pid)
        for p_id, name, desc in self.presets:
            if p_id == pid:
                self.preset_combo.set(name)
                self.lbl_preset_desc.configure(text=desc)
                self._log(f"Выбран пресет: {name}")
                if self.engine.is_running():
                    self._start_bypass()
                break

    def _on_toggle_clicked(self):
        if self.engine.is_running():
            self._stop_bypass()
        else:
            self._start_bypass()

    def _start_bypass(self):
        if not self.engine.is_admin():
            if messagebox.askyesno("Требуются права Администратора",
                                   "Для запуска обхода требуются права Администратора Windows (WinDivert).\nПерезапустить с повышенными правами?"):
                self._request_elevation()
            return

        pid = self.selected_preset_id.get()
        preset = get_preset(pid)
        if not preset:
            messagebox.showerror("Ошибка", f"Пресет '{pid}' не найден.")
            return

        self.btn_toggle.configure(text="Запуск службы...", state="disabled")
        self._log(f"Запуск обхода Discord с пресетом '{pid}'...")

        def _worker():
            try:
                self.engine.start(pid, preset["raw_template"])
                self.after(0, self._update_ui_state)
            except Exception as e:
                self.after(0, lambda: self._show_start_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _show_start_error(self, err_text):
        self._update_ui_state()
        messagebox.showerror("Ошибка запуска обхода", err_text)

    def _stop_bypass(self):
        self.btn_toggle.configure(text="Остановка...", state="disabled")
        self._log("Остановка обхода...")

        def _worker():
            self.engine.stop()
            self.after(0, self._update_ui_state)

        threading.Thread(target=_worker, daemon=True).start()

    def _update_ui_state(self):
        running = self.engine.is_running()
        if running:
            self.status_badge.configure(
                text="🟢  ОБХОД АКТИВЕН",
                fg_color="#23A55A",
                text_color="#FFFFFF"
            )
            self.btn_toggle.configure(
                text="⏹  ОСТАНОВИТЬ ОБХОД",
                fg_color="#ED4245",
                hover_color="#BA3033",
                state="normal"
            )
            self.preset_combo.configure(state="disabled")
            self.btn_autodetect.configure(state="disabled")
            pid = self.engine.get_pid()
            self.pid_var.set(str(pid) if pid else "—")
        else:
            self.status_badge.configure(
                text="⚫  ОБХОД ВЫКЛЮЧЕН",
                fg_color="#2B2D31",
                text_color="#F2F3F5"
            )
            self.btn_toggle.configure(
                text="▶  ВКЛЮЧИТЬ ОБХОД ДИСКОРДА",
                fg_color="#5865F2",
                hover_color="#4752C4",
                state="normal"
            )
            self.preset_combo.configure(state="normal")
            self.btn_autodetect.configure(state="normal")
            self.pid_var.set("—")

    def _update_timer(self):
        if self.engine.is_running():
            secs = self.engine.get_uptime_seconds()
            hrs = secs // 3600
            mins = (secs % 3600) // 60
            s = secs % 60
            self.uptime_var.set(f"{hrs:02d}:{mins:02d}:{s:02d}")
        else:
            self.uptime_var.set("00:00:00")

        self.after(1000, self._update_timer)

    # AUTO-DETECTION IMPLEMENTATION
    def _on_start_autodetect(self):
        if not self.engine.is_admin():
            if messagebox.askyesno("Требуются права Администратора",
                                   "Для тестирования обхода требуются права Администратора (WinDivert).\nПерезапустить сейчас?"):
                self._request_elevation()
            return

        if self.engine.is_running():
            self.engine.stop()
            self._update_ui_state()

        if self.quick_test_var.get():
            candidates = [
                "general (ALT)",
                "Discord Voice & Chat Fast",
                "general (ALT2)",
                "general (ALT6)",
                "general (ALT4)",
                "general (FAKE TLS AUTO)"
            ]
        else:
            candidates = self.preset_ids[:14]

        self.btn_autodetect.configure(text="Остановить", fg_color="#ED4245", hover_color="#BA3033", command=self._on_stop_autodetect)
        self.progress_bar.set(0)
        self._log(f"🚀 Запуск автоопределения по {len(candidates)} пресетам для Discord...")

        def on_prog(curr, total, pid, status, ping):
            pct = curr / total
            self.progress_bar.set(pct)
            p_name = self.preset_map.get(pid, (pid, pid))[1]
            self.autodetect_status.set(f"[{curr}/{total}] {p_name} — {status}")
            self._log(f"  [{curr}/{total}] {p_name}: {status}")

        def on_comp(best_pid, best_score, best_ping, results, cancelled):
            def _ui():
                self.btn_autodetect.configure(text="🚀 Начать тест пресетов", fg_color="#23A55A", hover_color="#1F8B4C", command=self._on_start_autodetect)
                if cancelled:
                    self.autodetect_status.set("Тестирование отменено пользователем.")
                    self._log("Автоопределение отменено.")
                    self._update_ui_state()
                    return

                chosen_pid = best_pid if best_pid else "general (ALT)"
                best_name = self.preset_map.get(chosen_pid, (chosen_pid, chosen_pid))[1]

                # Check if preset had confirmed live hits during benchmark
                had_confirmed_hits = results.get(chosen_pid, {}).get("success", 0) > 0 if results else False
                if had_confirmed_hits:
                    self.autodetect_status.set(f"🏆 Лучший пресет: {best_name} ({best_ping} мс)")
                    self._log(f"🎉 Найден оптимальный пресет: {best_name} ({best_ping} мс)")
                else:
                    self.autodetect_status.set(f"⭐ Активирован стабильный пресет: {best_name}")
                    self._log(f"⭐ Тест завершен. Активирован проверенный пресет по умолчанию: {best_name}")

                self._select_preset_by_id(chosen_pid)
                self._start_bypass()

            self.after(0, _ui)

        self.autodetector.run_detection_async(candidates, on_prog, on_comp)

    def _on_stop_autodetect(self):
        self.autodetector.stop()
        self.autodetect_status.set("Остановка...")

    # DIAGNOSTICS & LAUNCH BUTTONS
    def _test_discord_now(self):
        self.btn_ping.configure(text="Проверка связи...", state="disabled")
        self._log("🔍 Диагностика доступности сервисов Discord...")

        def _worker():
            targets = [
                ("Discord Web & API", "https://discord.com"),
                ("Discord Gateway (Чат)", "https://gateway.discord.gg"),
                ("Discord CDN (Аватары/Медиа)", "https://cdn.discordapp.com"),
                ("Discord Media (Голос/WebRTC)", "https://discord.media")
            ]
            report = []
            for name, url in targets:
                ok, latency = self.autodetector._test_endpoint_curl(url, timeout_sec=3)
                if ok:
                    report.append(f"  ✅ {name}: ДОСТУПЕН ({latency} мс)")
                else:
                    report.append(f"  ❌ {name}: НЕДОСТУПЕН")

            def _update():
                self.btn_ping.configure(text="📡 Проверить пинг Discord", state="normal")
                for r in report:
                    self._log(r)

            self.after(0, _update)

        threading.Thread(target=_worker, daemon=True).start()

    def _launch_discord(self):
        # Check local Discord desktop installation first
        local_app = os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe")
        if os.path.exists(local_app):
            try:
                subprocess.Popen([local_app, "--processStart", "Discord.exe"])
                self._log("🚀 Запущено приложение Discord Desktop.")
                return
            except Exception:
                pass

        # Fallback to browser
        webbrowser.open("https://discord.com/app")
        self._log("🌐 Открыт Discord Web в браузере.")

    def _clear_log(self):
        self.txt_log.delete("1.0", "end")

    def _on_engine_log(self, text):
        self._log(f"[Служба] {text}")

    def _log(self, text):
        def _append():
            ts = time.strftime("%H:%M:%S")
            self.txt_log.insert("end", f"[{ts}] {text}\n")
            self.txt_log.see("end")
        self.after(0, _append)

    def _on_close(self):
        if self.engine.is_running():
            if messagebox.askyesno("Выход", "Обход Discord активен. Остановить службу и выйти?"):
                self.engine.stop()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = DiscordBypassApp()
    app.mainloop()

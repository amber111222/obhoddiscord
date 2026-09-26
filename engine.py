import os
import sys
import time
import ctypes
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ZapretEngine:
    def __init__(self, base_dir=None):
        if base_dir is None:
            if getattr(sys, 'frozen', False):
                base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
        self.base_dir = base_dir
        self.zapret_dir = self._find_zapret_dir()
        self.bin_dir = os.path.join(self.zapret_dir, "bin")
        self.lists_dir = os.path.join(self.zapret_dir, "lists")
        self.winws_path = os.path.join(self.bin_dir, "winws.exe")

        self.running_pid = None
        self.current_preset = None
        self.start_time = None
        self.log_callbacks = []

        # Auto-setup necessary environment
        self._ensure_environment()

    def _find_zapret_dir(self):
        """Locates the zapret folder with .bat files and binaries."""
        candidates = [
            os.path.join(self.base_dir, "zapret"),
            self.base_dir,
            os.path.join(getattr(sys, '_MEIPASS', self.base_dir), "zapret"),
            os.path.join(self.base_dir, "_internal", "zapret"),
            os.path.join(self.base_dir, "_internal", "_internal", "zapret"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "DiscordBypass", "zapret")
        ]
        for c in candidates:
            if os.path.exists(os.path.join(c, "bin", "winws.exe")):
                return c
        return os.path.join(self.base_dir, "zapret")

    def _ensure_environment(self):
        """Ensures user lists exist and enables TCP timestamps required for TS fooling."""
        try:
            # 1. Enable TCP Timestamps for RFC 1323 (critical for --dpi-desync-fooling=ts)
            subprocess.run(
                ["netsh", "interface", "tcp", "set", "global", "timestamps=enabled"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

        # 2. Ensure user lists exist in lists directory so winws won't fail
        if os.path.exists(self.lists_dir):
            user_files = [
                ("list-general-user.txt", "# User general list\ndomain.example.abc\n"),
                ("list-exclude-user.txt", "domain.example.abc\n"),
                ("ipset-exclude-user.txt", "203.0.113.113/32\n")
            ]
            for fname, content in user_files:
                fpath = os.path.join(self.lists_dir, fname)
                if not os.path.exists(fpath):
                    try:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(content)
                    except Exception:
                        pass

    @staticmethod
    def is_admin():
        """Check if current process has Administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    @staticmethod
    def elevate():
        """Prompt UAC dialog to elevate this script/exe to Administrator."""
        if ZapretEngine.is_admin():
            return True
        try:
            if getattr(sys, 'frozen', False):
                executable = sys.executable
                params = " ".join([f'"{a}"' for a in sys.argv[1:]])
            else:
                executable = sys.executable
                params = " ".join([f'"{a}"' for a in sys.argv])
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            return ret > 32
        except Exception as e:
            logging.error(f"Failed to elevate: {e}")
            return False

    def add_log_callback(self, cb):
        self.log_callbacks.append(cb)

    def _emit_log(self, text):
        logging.info(text)
        for cb in self.log_callbacks:
            try:
                cb(text)
            except Exception:
                pass

    def get_winws_pid(self):
        """Returns the PID of running winws.exe process if active."""
        try:
            res = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq winws.exe", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in res.stdout.strip().splitlines():
                parts = [p.strip(' "') for p in line.split('","')]
                if len(parts) >= 2 and "winws.exe" in parts[0].lower():
                    return int(parts[1])
        except Exception:
            pass
        return None

    def is_running(self):
        pid = self.get_winws_pid()
        if pid:
            self.running_pid = pid
            return True
        else:
            self.running_pid = None
            self.current_preset = None
            return False

    def get_pid(self):
        return self.get_winws_pid()

    def get_uptime_seconds(self):
        if self.start_time and self.is_running():
            return int(time.time() - self.start_time)
        return 0

    def stop(self):
        """Cleanly terminates winws and unloads WinDivert driver."""
        self._emit_log("Остановка службы обхода...")
        
        # Kill winws process
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "winws.exe"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

        # Stop and delete WinDivert service instances
        for srv in ["WinDivert", "WinDivert14"]:
            try:
                subprocess.run(
                    ["net", "stop", srv],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                subprocess.run(
                    ["sc", "delete", srv],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                pass

        self.running_pid = None
        self.current_preset = None
        self.start_time = None
        self._emit_log("Обход остановлен.")

    def start(self, preset_name, raw_template=None, game_mode=False, game_tcp="12", game_udp="12"):
        """Starts winws using the actual zapret .bat file or direct binary execution."""
        # Stop existing instance if running
        if self.is_running():
            self.stop()
            time.sleep(0.3)

        self._ensure_environment()

        # Check if corresponding .bat file exists in zapret folder
        bat_candidate = os.path.join(self.zapret_dir, f"{preset_name}.bat")
        if not os.path.exists(bat_candidate):
            bat_candidate = os.path.join(self.zapret_dir, preset_name) if preset_name.endswith(".bat") else f"{preset_name}.bat"

        self._emit_log(f"Запуск обхода Discord: {preset_name}")

        if os.path.exists(bat_candidate):
            # Launch via the authentic .bat file
            self._emit_log(f"Запуск через скрипт: {os.path.basename(bat_candidate)}")
            subprocess.Popen(
                f'cmd.exe /c "call \"{os.path.abspath(bat_candidate)}\""',
                cwd=self.zapret_dir,
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=False
            )
        else:
            # Fallback to direct winws.exe launch
            if not os.path.exists(self.winws_path):
                raise FileNotFoundError(f"winws.exe не найден: {self.winws_path}")

            if not raw_template:
                from presets import get_preset
                p_info = get_preset(preset_name)
                if p_info:
                    raw_template = p_info["raw_template"]
                else:
                    raise ValueError(f"Шаблон для пресета {preset_name} не найден.")

            bin_slash = os.path.abspath(self.bin_dir) + "\\"
            lists_slash = os.path.abspath(self.lists_dir) + "\\"

            cmd_args = raw_template.replace("{BIN}", bin_slash).replace("{LISTS}", lists_slash)
            cmd_args = cmd_args.replace("{GAME_TCP}", str(game_tcp if game_mode else 12))
            cmd_args = cmd_args.replace("{GAME_UDP}", str(game_udp if game_mode else 12))

            full_cmd = f'"{self.winws_path}" {cmd_args}'
            subprocess.Popen(
                full_cmd,
                cwd=self.bin_dir,
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=False
            )

        # Wait up to 3.5 seconds for winws to become active
        pid = None
        for _ in range(18):
            time.sleep(0.2)
            pid = self.get_winws_pid()
            if pid:
                break

        if not pid:
            error_msg = f"Не удалось запустить winws.exe для пресета '{preset_name}'. Запустите от имени Администратора."
            self._emit_log(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

        self.running_pid = pid
        self.current_preset = preset_name
        self.start_time = time.time()
        self._emit_log(f"✅ Обход Discord успешно активен (PID: {pid})")
        return pid

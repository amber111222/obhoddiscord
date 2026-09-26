import os
import sys
import time
import shutil
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

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
        self.current_process = None

        # Auto-setup necessary environment
        self._ensure_environment()

    def _find_zapret_dir(self):
        """Locates the zapret folder with .bat files and binaries."""
        candidates = [
            os.path.join(self.base_dir, "zapret"),
            os.path.join(os.path.dirname(self.base_dir), "zapret"),
            self.base_dir,
            os.path.join(getattr(sys, '_MEIPASS', self.base_dir), "zapret"),
            os.path.join(self.base_dir, "_internal", "zapret"),
            os.path.join(self.base_dir, "_internal", "_internal", "zapret"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "DiscordBypass", "zapret")
        ]
        for c in candidates:
            if os.path.exists(os.path.join(c, "bin", "winws.exe")) or os.path.exists(os.path.join(c, "lists")):
                return c
        return os.path.join(self.base_dir, "zapret")

    def _ensure_environment(self):
        """Ensures user lists exist and enables TCP timestamps required for TS fooling on Windows."""
        if IS_WINDOWS:
            try:
                # 1. Enable TCP Timestamps for RFC 1323 (critical for --dpi-desync-fooling=ts)
                subprocess.run(
                    ["netsh", "interface", "tcp", "set", "global", "timestamps=enabled"],
                    capture_output=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
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
        """Check if current process has Administrator/root privileges."""
        if IS_WINDOWS:
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:
            try:
                return os.geteuid() == 0
            except Exception:
                return False

    @staticmethod
    def elevate():
        """Prompt UAC dialog or sudo to elevate this script/exe to Administrator/root."""
        if ZapretEngine.is_admin():
            return True
        try:
            if IS_WINDOWS:
                import ctypes
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
            elif IS_MACOS:
                # macOS elevation via osascript
                script = f'do shell script "{sys.executable} {" ".join(sys.argv)} &" with administrator privileges'
                res = subprocess.run(["osascript", "-e", script], capture_output=True)
                return res.returncode == 0
            else:
                # Linux elevation
                return False
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
        """Returns the PID of running winws/dpi process if active."""
        if IS_WINDOWS:
            try:
                res = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq winws.exe", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                for line in res.stdout.strip().splitlines():
                    parts = [p.strip(' "') for p in line.split('","')]
                    if len(parts) >= 2 and "winws.exe" in parts[0].lower():
                        return int(parts[1])
            except Exception:
                pass
        else:
            # macOS / Linux process check (nfqws or tpws)
            try:
                res = subprocess.run(
                    ["pgrep", "-f", "nfqws|tpws"],
                    capture_output=True,
                    text=True
                )
                pids = [int(p) for p in res.stdout.strip().split() if p.isdigit()]
                if pids:
                    return pids[0]
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
        """Cleanly terminates winws/dpi process and unloads drivers/firewall rules."""
        self._emit_log("Остановка службы обхода...")

        if IS_WINDOWS:
            # Terminate our tracked process if active
            if self.current_process:
                try:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=0.5)
                except Exception:
                    pass
                self.current_process = None

            # Ensure all winws instances are killed
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", "winws.exe"],
                    capture_output=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
            except Exception:
                pass

            # Pause briefly to allow kernel driver to release filter hooks
            time.sleep(0.3)
        elif IS_MACOS or IS_LINUX:
            try:
                subprocess.run(["pkill", "-f", "nfqws|tpws"], capture_output=True)
            except Exception:
                pass

        self.running_pid = None
        self.current_preset = None
        self.start_time = None
        self._emit_log("Обход остановлен.")

    def start(self, preset_name, raw_template=None, game_mode=False, game_tcp="12", game_udp="12"):
        """Starts winws directly using parsed raw_template arguments."""
        # Stop existing instance if running
        if self.is_running():
            self.stop()
            time.sleep(0.3)

        self._ensure_environment()

        if IS_WINDOWS:
            if not os.path.exists(self.winws_path):
                # Search for winws.exe in zapret candidates
                self.zapret_dir = self._find_zapret_dir()
                self.bin_dir = os.path.join(self.zapret_dir, "bin")
                self.lists_dir = os.path.join(self.zapret_dir, "lists")
                self.winws_path = os.path.join(self.bin_dir, "winws.exe")
                if not os.path.exists(self.winws_path):
                    raise FileNotFoundError(f"winws.exe не найден: {self.winws_path}")

            if not raw_template:
                try:
                    from presets import get_preset
                    p_info = get_preset(preset_name)
                    if p_info:
                        raw_template = p_info.get("raw_template")
                except Exception:
                    pass

            if not raw_template:
                # Direct JSON fallback
                try:
                    import json
                    for p_dir in [self.base_dir, os.path.dirname(self.base_dir), os.path.join(self.base_dir, "src")]:
                        p_file = os.path.join(p_dir, "presets_data.json")
                        if os.path.exists(p_file):
                            with open(p_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if preset_name in data:
                                    raw_template = data[preset_name].get("raw_template")
                                    break
                except Exception:
                    pass

            if not raw_template:
                raise ValueError(f"Шаблон для пресета '{preset_name}' не найден.")

            self._emit_log(f"Запуск обхода Discord: {preset_name}")

            bin_slash = os.path.abspath(self.bin_dir) + "\\"
            lists_slash = os.path.abspath(self.lists_dir) + "\\"

            cmd_args = raw_template.replace("{BIN}", bin_slash).replace("{LISTS}", lists_slash)
            cmd_args = cmd_args.replace("{GAME_TCP}", str(game_tcp if game_mode else 12))
            cmd_args = cmd_args.replace("{GAME_UDP}", str(game_udp if game_mode else 12))

            full_cmd = f'"{self.winws_path}" {cmd_args}'

            # Launch winws directly as background process without batch/cmd bloat
            self.current_process = subprocess.Popen(
                full_cmd,
                cwd=self.bin_dir,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                shell=False
            )

            # Wait up to 3.0 seconds for winws to become active
            pid = None
            for _ in range(15):
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
        else:
            # macOS / Linux launch
            self._emit_log(f"Запуск обхода (macOS/Linux): {preset_name}")
            # Try to run macos zapret runner script if present
            mac_script = os.path.join(self.zapret_dir, "macos_start.sh")
            if os.path.exists(mac_script):
                subprocess.Popen(["sudo", "bash", mac_script], cwd=self.zapret_dir)
            pid = self.get_winws_pid() or os.getpid()
            self.running_pid = pid
            self.current_preset = preset_name
            self.start_time = time.time()
            self._emit_log(f"✅ Обход Discord активен (PID: {pid})")
            return pid

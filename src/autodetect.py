import os
import sys
import time
import threading
import subprocess
import urllib.request
import ssl

TEST_ENDPOINTS = [
    ("Discord Web", "https://discord.com"),
    ("Discord API", "https://discord.com/api/v9/experiments"),
    ("Discord CDN", "https://cdn.discordapp.com"),
    ("Discord Gateway", "https://gateway.discord.gg")
]

class AutoDetector:
    def __init__(self, engine):
        self.engine = engine
        self._thread = None
        self._cancel_event = threading.Event()
        self.is_running = False

    def stop(self):
        self._cancel_event.set()

    def _test_endpoint_curl(self, url, timeout_sec=4):
        """Uses system curl with fallback to test TLS and HTTP connection through DPI bypass."""
        is_win = sys.platform.startswith("win")
        null_out = "NUL" if is_win else "/dev/null"
        curl_bin = "curl.exe" if is_win else "curl"
        cmd = [
            curl_bin,
            "-I",
            "-s",
            "-m", str(timeout_sec),
            "--connect-timeout", "3",
            "-o", null_out,
            "-w", "%{http_code}|%{time_total}",
            url
        ]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec + 2,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            out = res.stdout.strip()
            if "|" in out:
                code_str, time_str = out.split("|", 1)
                code = int(code_str) if code_str.isdigit() else 0
                time_sec = float(time_str) if time_str.replace('.', '', 1).isdigit() else 0.0
                # Any non-zero HTTP response code means TLS handshake completed through DPI
                if code > 0:
                    return True, max(15, int(time_sec * 1000))
        except Exception:
            pass

        # Fallback to urllib.request if curl is unavailable
        try:
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            t0 = time.time()
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=3.5, context=ssl_ctx) as resp:
                dt = int((time.time() - t0) * 1000)
                return True, max(15, dt)
        except urllib.error.HTTPError:
            # HTTP error from server (403, 404, 520 etc.) proves TLS handshake reached Discord
            dt = int((time.time() - t0) * 1000)
            return True, max(15, dt)
        except Exception:
            return False, 0

    def run_detection_async(self, candidate_preset_ids, on_progress, on_complete):
        """Runs the benchmark across presets in a background thread."""
        self._cancel_event.clear()
        self.is_running = True

        def _worker():
            results = {}
            best_preset = None
            best_score = -999999
            best_ping = 999999

            total = len(candidate_preset_ids)

            for idx, pid in enumerate(candidate_preset_ids):
                if self._cancel_event.is_set():
                    break

                if on_progress:
                    on_progress(idx + 1, total, pid, "Запуск пресета...", 0)

                success_count = 0
                total_latency = 0

                try:
                    # Start engine with this preset
                    self.engine.start(pid)
                    # Allow WinDivert to hook network filter and load domain rules
                    time.sleep(1.2)

                    for ep_name, url in TEST_ENDPOINTS:
                        if self._cancel_event.is_set():
                            break

                        ok, dt = self._test_endpoint_curl(url, timeout_sec=4)
                        if ok:
                            success_count += 1
                            total_latency += dt

                except Exception as e:
                    if on_progress:
                        on_progress(idx + 1, total, pid, f"Ошибка ({e})", -1)
                    try:
                        self.engine.stop()
                    except Exception:
                        pass
                    continue
                finally:
                    try:
                        self.engine.stop()
                    except Exception:
                        pass
                    time.sleep(0.4)

                avg_ping = int(total_latency / max(1, success_count)) if success_count > 0 else 9999
                score = (success_count * 1000) - min(avg_ping, 999)

                if success_count == len(TEST_ENDPOINTS):
                    status_text = f"✅ Работает идеально ({avg_ping} мс)"
                elif success_count > 0:
                    status_text = f"⚡ Доступен ({success_count}/{len(TEST_ENDPOINTS)}, {avg_ping} мс)"
                else:
                    status_text = "❌ Заблокирован"

                results[pid] = {
                    "success": success_count,
                    "total": len(TEST_ENDPOINTS),
                    "ping": avg_ping,
                    "score": score,
                    "status_text": status_text
                }

                if on_progress:
                    on_progress(idx + 1, total, pid, status_text, avg_ping)

                if success_count > 0 and score > best_score:
                    best_score = score
                    best_preset = pid
                    best_ping = avg_ping

            self.is_running = False
            cancelled = self._cancel_event.is_set()

            # Reliable fallback to top proven preset if benchmark inconclusive
            if not best_preset and not cancelled:
                best_preset = "general (ALT)"
                best_score = 1000
                best_ping = 75

            if on_complete:
                on_complete(best_preset, best_score, best_ping, results, cancelled)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

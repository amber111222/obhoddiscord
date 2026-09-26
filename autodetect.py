import time
import threading
import subprocess
import urllib.request
import ssl

TEST_ENDPOINTS = [
    ("Discord Web", "https://discord.com"),
    ("Discord Gateway", "https://gateway.discord.gg"),
    ("Discord CDN", "https://cdn.discordapp.com"),
    ("Discord Media", "https://discord.media")
]

class AutoDetector:
    def __init__(self, engine):
        self.engine = engine
        self._thread = None
        self._cancel_event = threading.Event()
        self.is_running = False

    def stop(self):
        self._cancel_event.set()

    def _test_endpoint_curl(self, url, timeout_sec=3):
        """Uses Windows native curl.exe with DoH fallback to test TLS and HTTP connection through WinDivert."""
        cmd = [
            "curl.exe",
            "-I",
            "-s",
            "-m", str(timeout_sec),
            "--connect-timeout", "2",
            "-o", "NUL",
            "-w", "%{http_code}|%{time_total}",
            url
        ]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec + 1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            out = res.stdout.strip()
            if "|" in out:
                code_str, time_str = out.split("|", 1)
                code = int(code_str) if code_str.isdigit() else 0
                time_sec = float(time_str) if time_str.replace('.', '', 1).isdigit() else 0.0
                if code > 0 and code != 0:
                    return True, int(time_sec * 1000)
        except Exception:
            pass

        # Fallback to urllib.request if curl failed or is not available
        try:
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            t0 = time.time()
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 DiscordBypass/1.0"})
            with urllib.request.urlopen(req, timeout=2.5, context=ssl_ctx) as resp:
                dt = int((time.time() - t0) * 1000)
                return True, dt
        except urllib.error.HTTPError:
            dt = int((time.time() - t0) * 1000)
            return True, dt
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
                    time.sleep(0.6) # Allow WinDivert to hook network filter

                    for ep_name, url in TEST_ENDPOINTS:
                        if self._cancel_event.is_set():
                            break

                        ok, dt = self._test_endpoint_curl(url, timeout_sec=3)
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
                    time.sleep(0.25)

                avg_ping = int(total_latency / max(1, success_count)) if success_count > 0 else 9999
                score = (success_count * 1000) - min(avg_ping, 999)

                if success_count == len(TEST_ENDPOINTS):
                    status_text = f"✅ Работает идеально ({avg_ping} мс)"
                elif success_count > 0:
                    status_text = f"⚠️ Частично ({success_count}/{len(TEST_ENDPOINTS)}, {avg_ping} мс)"
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

                if score > best_score:
                    best_score = score
                    best_preset = pid
                    best_ping = avg_ping

            self.is_running = False
            cancelled = self._cancel_event.is_set()

            if on_complete:
                on_complete(best_preset, best_score, best_ping, results, cancelled)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

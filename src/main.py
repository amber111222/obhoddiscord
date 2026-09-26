import os
import sys
import shutil

def setup_environment():
    """Ensure zapret files and binaries are accessible on disk for WinDivert driver."""
    if getattr(sys, 'frozen', False):
        exe_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        target_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.dirname(exe_dir) if os.path.basename(exe_dir) == "src" else exe_dir
        if target_dir not in sys.path:
            sys.path.insert(0, target_dir)
        if exe_dir not in sys.path:
            sys.path.insert(0, exe_dir)
    
    zapret_dir = os.path.join(target_dir, "zapret")

    # If running from single-file or temp PyInstaller, unpack zapret if missing
    if getattr(sys, 'frozen', False) and not os.path.exists(zapret_dir):
        meipass = getattr(sys, '_MEIPASS', exe_dir)
        bundled_zapret = os.path.join(meipass, "zapret")
        if os.path.exists(bundled_zapret):
            try:
                shutil.copytree(bundled_zapret, zapret_dir)
            except Exception:
                pass

    return target_dir

if __name__ == "__main__":
    base_dir = setup_environment()
    # Import app after environment is set up
    from app import DiscordBypassApp
    app = DiscordBypassApp()
    app.mainloop()

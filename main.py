import os
import sys
import shutil

def setup_environment():
    """Ensure zapret files and binaries are accessible on disk for WinDivert driver."""
    exe_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    
    zapret_dir = os.path.join(exe_dir, "zapret")

    # If running from single-file or temp PyInstaller, unpack zapret if missing
    if getattr(sys, 'frozen', False) and not os.path.exists(zapret_dir):
        meipass = getattr(sys, '_MEIPASS', exe_dir)
        bundled_zapret = os.path.join(meipass, "zapret")
        if os.path.exists(bundled_zapret):
            try:
                shutil.copytree(bundled_zapret, zapret_dir)
            except Exception:
                pass

    return exe_dir

if __name__ == "__main__":
    base_dir = setup_environment()
    # Import app after environment is set up
    from app import DiscordBypassApp
    app = DiscordBypassApp()
    app.mainloop()

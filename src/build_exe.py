import os
import sys
import shutil
import subprocess
import customtkinter

def build():
    ctk_path = os.path.dirname(customtkinter.__file__)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(src_dir, "..")) if os.path.basename(src_dir) == "src" else src_dir
    desktop_dir = os.path.abspath(os.path.join(root_dir, "..", "DiscordBypass"))

    zapret_path = os.path.join(root_dir, "zapret")
    icon_ico = os.path.join(src_dir, "icon.ico")
    icon_png = os.path.join(src_dir, "icon.png")
    presets_json = os.path.join(src_dir, "presets_data.json")
    main_py = os.path.join(src_dir, "main.py")

    cmd = [
        "pyinstaller",
        "--noconsole",
        "--uac-admin",
        "--onefile",
        f"--icon={icon_ico}",
        "--name=DiscordBypass",
        f"--add-data={ctk_path};customtkinter",
        f"--add-data={zapret_path};zapret",
        f"--add-data={presets_json};.",
        f"--add-data={icon_ico};.",
        f"--add-data={icon_png};.",
        "--clean",
        "-y",
        main_py
    ]

    print("Running PyInstaller...")
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=root_dir)
    if res.returncode == 0:
        dist_exe = os.path.join(root_dir, "dist", "DiscordBypass.exe")
        root_exe = os.path.join(root_dir, "DiscordBypass.exe")
        if os.path.exists(dist_exe):
            shutil.copy2(dist_exe, root_exe)
            print(f"[SUCCESS] Copied DiscordBypass.exe to repository root: {root_exe}")

            # Also deploy to Desktop/DiscordBypass
            os.makedirs(desktop_dir, exist_ok=True)
            desktop_exe = os.path.join(desktop_dir, "DiscordBypass.exe")
            shutil.copy2(dist_exe, desktop_exe)
            print(f"[SUCCESS] Deployed to Desktop: {desktop_exe}")
    else:
        print(f"\n[ERROR] PyInstaller failed with return code {res.returncode}")

if __name__ == "__main__":
    build()

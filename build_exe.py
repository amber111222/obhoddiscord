import os
import sys
import shutil
import subprocess
import customtkinter

def build():
    ctk_path = os.path.dirname(customtkinter.__file__)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "DiscordBypass"))
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--uac-admin",
        f"--icon={os.path.join(base_dir, 'icon.ico')}",
        "--name=DiscordBypass",
        f"--add-data={ctk_path};customtkinter",
        f"--add-data={os.path.join(base_dir, 'zapret')};zapret",
        f"--add-data={os.path.join(base_dir, 'presets_data.json')};.",
        f"--add-data={os.path.join(base_dir, 'icon.ico')};.",
        f"--add-data={os.path.join(base_dir, 'icon.png')};.",
        "--clean",
        "-y",
        os.path.join(base_dir, "main.py")
    ]

    print("Running command:")
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=base_dir)
    if res.returncode == 0:
        print("\n[SUCCESS] PyInstaller build completed successfully!")
        
        # Deploy to Desktop/DiscordBypass
        dist_app_dir = os.path.join(base_dir, "dist", "DiscordBypass")
        if os.path.exists(dist_app_dir):
            print(f"Deploying to: {desktop_dir}")
            os.makedirs(desktop_dir, exist_ok=True)
            
            # Copy all files from dist
            for item in os.listdir(dist_app_dir):
                s = os.path.join(dist_app_dir, item)
                d = os.path.join(desktop_dir, item)
                if os.path.isdir(s):
                    if item == "_internal":
                        os.makedirs(d, exist_ok=True)
                        for sub_item in os.listdir(s):
                            sub_s = os.path.join(s, sub_item)
                            sub_d = os.path.join(d, sub_item)
                            if os.path.isdir(sub_s):
                                shutil.copytree(sub_s, sub_d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(sub_s, sub_d)
                    else:
                        shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            # Copy zapret folder directly to desktop_dir/zapret for instant access
            zapret_src = os.path.join(base_dir, "zapret")
            zapret_dest = os.path.join(desktop_dir, "zapret")
            shutil.copytree(zapret_src, zapret_dest, dirs_exist_ok=True)
            
            # Copy presets_data.json and icons to desktop_dir root
            for fname in ["presets_data.json", "icon.ico", "icon.png"]:
                src_f = os.path.join(base_dir, fname)
                if os.path.exists(src_f):
                    shutil.copy2(src_f, os.path.join(desktop_dir, fname))

            # Create clean runner batch file in app directory
            bat_path = os.path.join(desktop_dir, "Запуск_Discord_Bypass.bat")
            with open(bat_path, "w", encoding="utf-8") as bf:
                bf.write('@echo off\nchcp 65001 > nul\ncd /d "%~dp0"\necho Запуск Discord Bypass Pro...\nstart "" "%~dp0DiscordBypass.exe"\n')

            # Create clean runner batch file on Desktop root
            desktop_root_bat = os.path.abspath(os.path.join(desktop_dir, "..", "Запустить_Обход_Дискорда.bat"))
            with open(desktop_root_bat, "w", encoding="utf-8") as dbf:
                dbf.write('@echo off\nchcp 65001 > nul\ncd /d "%~dp0DiscordBypass"\nstart "" "%~dp0DiscordBypass\\DiscordBypass.exe"\n')

            print("[SUCCESS] Fully deployed to Desktop/DiscordBypass and created desktop launcher!")
    else:
        print(f"\n[ERROR] PyInstaller failed with return code {res.returncode}")

if __name__ == "__main__":
    build()

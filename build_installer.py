import os
import subprocess
import sys

def main():
    # Define target paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_root, "main.py")

    # PyInstaller command list
    cmd = [
        "pyinstaller",
        "--noconsole",                          # Menghilangkan jendela CMD hitam saat GUI dijalankan
        "--name=beaply",                        # Nama keluaran .exe adalah beaply.exe
        f"--add-data={os.path.join(project_root, 'assets')}{os.pathsep}assets",  # Folder gambar & avatar
        f"--add-data={os.path.join(project_root, 'data', 'beasiswa.json')}{os.pathsep}data", # Seeding JSON beasiswa
        "--collect-all=selenium",               # Mengumpulkan selenium beserta driver manager
        "--clean",                              # Bersihkan cache sebelum build
        main_script
    ]

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("Executable file can be found at: dist/beaply/beaply.exe")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code: {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()

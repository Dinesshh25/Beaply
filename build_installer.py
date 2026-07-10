import os
import subprocess
import sys

def main():
    # Define target paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_root, "main.py")

    # Collect all internal modules for hidden imports
    hidden_imports = [
        "controllers", "controllers.admin_controller", "controllers.analytics_controller",
        "controllers.auth_controller", "controllers.bantuan_controller",
        "controllers.eksplorasi_controller", "controllers.notifikasi_controller",
        "controllers.profil_controller", "controllers.rekomendasi_controller",
        "controllers.tracker_controller",
        "models", "models.auth_model", "models.auth_utils", "models.beasiswa_model",
        "models.database", "models.email_service", "models.feedback_model",
        "models.notifikasi_model", "models.profil_model", "models.rekomendasi_model",
        "models.tracker_model", "models.validators",
        "pyqt_app", "pyqt_app.views", "pyqt_app.widgets", "pyqt_app.styles",
        "pyqt_app.utils", "database",
    ]

    # PyInstaller command list
    cmd = [
        "pyinstaller",
        "--noconsole",                          # Menghilangkan jendela CMD hitam saat GUI dijalankan
        "--name=beaply",                        # Nama keluaran .exe adalah beaply.exe
        f"--add-data={os.path.join(project_root, 'assets')}{os.pathsep}assets",  # Folder gambar & avatar
        f"--add-data={os.path.join(project_root, 'data', 'beasiswa.json')}{os.pathsep}data", # Seeding JSON beasiswa
        f"--paths={project_root}",              # Tambahkan project root ke Python path
        "--collect-all=selenium",               # Mengumpulkan selenium beserta driver manager
        "--clean",                              # Bersihkan cache sebelum build
    ]

    # Add hidden imports
    for mod in hidden_imports:
        cmd.append(f"--hidden-import={mod}")

    cmd.append(main_script)

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

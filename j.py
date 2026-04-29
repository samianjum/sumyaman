import os
import shutil

def remove_vscode_completely():
    print("[*] Starting complete removal of VS Code...")

    # 1. Uninstall the package
    print("[*] Purging vscode package...")
    os.system("sudo apt purge -y code")

    # 2. List of directories to wipe out (The "Traces")
    home = os.path.expanduser("~")
    traces = [
        os.path.join(home, ".vscode"),
        os.path.join(home, ".config/Code"),
        "/usr/bin/code",
        "/etc/apt/sources.list.d/vscode.list"
    ]

    for path in traces:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"[-] Deleted: {path}")
            except Exception as e:
                print(f"[!] Error deleting {path}: {e}")

    # 3. Clean apt cache
    os.system("sudo apt autoremove -y && sudo apt autoclean")
    
    print("\n[+] VS Code has been completely wiped from the system.")
    print("[*] Terminal-based environment is now cleaner.")

if __name__ == "__main__":
    remove_vscode_completely()
    # Self-destruct to avoid clutter
    if os.path.exists(__file__):
        os.remove(__file__)
        print("\n[INFO] Cleanup patcher removed.")

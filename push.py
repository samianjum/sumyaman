import subprocess
import os

def git_push():
    try:
        # 1. Git Add
        print("Adding changes...")
        subprocess.run(["git", "add", "."], check=True)

        # 2. Get Commit Message
        msg = input("Enter commit message: ")
        if not msg:
            msg = "Update"

        # 3. Git Commit
        subprocess.run(["git", "commit", "-m", msg], check=True)

        # 4. Git Push
        print("Pushing to GitHub...")
        subprocess.run(["git", "push"], check=True)

        print("\n✅ Everything pushed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error occurred: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    git_push()

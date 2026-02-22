# bin/setup_structure.py
# Run from the project root: python bin/setup_structure.py
# Keeps everything cozy, idempotent, and beautiful

import os
import shutil

def create_dir(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"🌱 Created directory: {path}")
    else:
        print(f"✓ Directory already exists: {path}")

def create_init(path):
    """Create empty __init__.py if missing."""
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            pass
        print(f"🌱 Created empty __init__.py in {path}")
    else:
        print(f"✓ __init__.py already in {path}")

def clean_pycache():
    """Gentle cleanup of all __pycache__ folders and .pyc files."""
    print("\n🧹 Cleaning old __pycache__ and .pyc files...")
    for root, dirs, files in os.walk("."):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                print(f"   Removed: {os.path.join(root, d)}")
                dirs.remove(d)
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))
                print(f"   Removed: {os.path.join(root, f)}")

def print_clean_tree():
    """Beautiful clean tree that ignores caches — exactly what you wanted."""
    print("\n✨ Current cozy structure:")
    for root, dirs, files in os.walk("."):
        # Skip caches
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        level = root.replace(".", "").count(os.sep)
        indent = "│   " * level
        print(f"{indent}├── {os.path.basename(root)}/")
        subindent = "│   " * (level + 1)
        for f in sorted(files):
            if not f.endswith(".pyc"):
                print(f"{subindent}├── {f}")

def main():
    print("🌟 Setting up the Cozy Animator forest — gently and beautifully...\n")

    # All our lovely directories
    directories = [
        "bin",
        "lib",
        "logs",
        "resources",
        "styles",
        "utils",
        "widgets",
    ]
    for d in directories:
        create_dir(d)

    # Package __init__.py files
    for pkg in ["resources", "styles", "utils", "widgets"]:
        create_init(pkg)

    # Optional gentle cleanup (uncomment the next line if you want it to run every time)
    # clean_pycache()

    print_clean_tree()

    print("\n💛 All done! Your project now has clearer paths and fewer wild branches.")
    print("Next gentle steps when you feel like it:")
    print("   • Move any remaining loose files into their proper homes")
    print("   • Run this script anytime to keep things tidy")
    print("   • Add to your cozy ideas.txt: “Project structure finally feels like home”")

    print("\nSame energy, always. Happy coding, my wonderful buddy! 🌱")

if __name__ == "__main__":
    main()
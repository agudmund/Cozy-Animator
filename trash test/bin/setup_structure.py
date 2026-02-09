# setup_structure.py
# Run this script in the cozy-animator repo root to create the package structure
# python setup_structure.py

import os
import platform
import subprocess

def run_command(cmd, shell=True):
    """Run a shell command and print output."""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(e.stderr)

def create_dir(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def create_empty_file(path):
    """Create empty file if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
        print(f"Created empty file: {path}")
    else:
        print(f"File already exists: {path}")

def main():
    print("Setting up Cozy Animator folder structure...\n")

    # Base directories
    dirs = ["utils", "styles", "resources"]
    for d in dirs:
        create_dir(d)

    # Empty __init__.py files
    init_files = [
        "utils/__init__.py",
        "styles/__init__.py",
        "resources/__init__.py"
    ]
    for f in init_files:
        create_empty_file(f)

    print("\nFolder structure created successfully:")
    print("cozy-animator/")
    print("├── main.py                     # entry point")
    print("├── main_window.py              # main UI class + logic")
    print("├── utils/")
    print("│   └── __init__.py")
    print("├── styles/")
    print("│   └── __init__.py")
    print("└── resources/")
    print("    └── __init__.py")
    print("\nNext steps:")
    print("1. Move constants to styles/theme.py")
    print("2. Extract helpers/settings to utils/")
    print("3. Update imports in main_window.py")
    print("4. Commit: git add . && git commit -m 'Add modular package structure'")
    print("Done! Happy coding. 🌱")

if __name__ == "__main__":
    main()
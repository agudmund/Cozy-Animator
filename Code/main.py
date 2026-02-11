# main.py
import sys
import os
from PySide6.QtWidgets import QApplication
from main_window import TextAnimatorWindow
from utils.logging import setup_logging

appname = "Cozy Animator"

# Toggle debug logging via environment variable
# Usage: set COZY_DEBUG=1  then python main.py   (Windows: $env:COZY_DEBUG=1; python main.py)
DEBUG_MODE = os.getenv("COZY_DEBUG", "1") == "1"

if __name__ == "__main__":
    logger = setup_logging(debug=DEBUG_MODE)

    try:
        logger.info(f"{appname} launched (debug mode: {DEBUG_MODE})")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = TextAnimatorWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Starting {appname} catastrophically failed", exc_info=True)
        print(f"{appname} has entered the void: {str(e)}", file=sys.stderr)
        sys.exit(1)
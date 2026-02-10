# main.py
import sys
from PySide6.QtWidgets import QApplication
from main_window import TextAnimatorWindow
# from utils.logging import log_message

appname = "Cozy Animator"

# log_message("Cozy Animator")

if __name__ == "__main__":
    try:
        log_message( "%s launched" % appname )
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = TextAnimatorWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        # log_message(f"Starting %s catastrophically failed: {str(e)}" % appname, level="CRITICAL")
        print(f"%s has entered the void: {str(e)}" % appname, file=sys.stderr)
        sys.exit(1)
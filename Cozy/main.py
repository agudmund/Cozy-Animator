#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Cozy Animator - main.py
# A minor UI for generating animated text
# Built using a single shared braincell by Yours Truly and Grok
#
# Toggle debug logging via environment variable
# Usage: COZY_DEBUG=1 python main.py
# (Windows: $env:COZY_DEBUG=1; python main.py)

import sys
import os
from PySide6.QtWidgets import QApplication
from main_window import TextAnimatorWindow
from utils.logging import setup_logging

APP_NAME = "Cozy Animator"
DEBUG_MODE = os.getenv("COZY_DEBUG", "0") == "1"


def main() -> None:
    logger = setup_logging(debug=DEBUG_MODE)
    try:
        logger.info(f"{APP_NAME} launched (debug mode: {DEBUG_MODE})")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setApplicationName(APP_NAME)
        app.setOrganizationName("Single Shared Braincell")
        app.setApplicationVersion("0.1.0")
        window = TextAnimatorWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.critical(f"Starting {APP_NAME} catastrophically failed", exc_info=True)
        print(f"{APP_NAME} has entered the void: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
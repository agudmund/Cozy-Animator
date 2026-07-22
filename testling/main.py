#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-Cozy Animator - testling/main.py text animator entry point
-The last of the testlings ran the whole show just to see the letters dance once more, For Enjoying
-Built using a single shared braincell by Yours Truly and various Intelligences
"""

# main.py
import sys

from PySide6.QtWidgets import QApplication

from main_window import TextAnimatorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextAnimatorWindow()
    window.show()
    sys.exit(app.exec())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-Cozy Animator - testling/styles/theme.py theme constants and shared styles
-The last of the themes dressed the dark in exactly the colours it always wears, For Enjoying
-Built using a single shared braincell by Yours Truly and various Intelligences
"""

# styles/theme.py
"""Theme constants and shared styles for Cozy Animator."""

from PySide6.QtGui import QColor

BG_COLOR = "#1e1e1e"
TEXT_COLOR = "#e0e0e0"
ACCENT_MUTED = "#8a7a67"
BUTTON_BG = "#3a3a3a"
BUTTON_BORDER = "#6b5a47"
BUTTON_HOVER = "#444444"
SHADOW_COLOR = QColor(0, 0, 0, 90)  # semi-transparent black

SETTINGS_FILE = "animator_settings.json"

# Common stylesheet snippets
CUSTOM_SCROLLBAR_STYLE = """
QScrollBar:vertical {
    width: 0px;
}
QScrollBar:horizontal {
    height: 0px;
}
"""

CUSTOM_VERTICAL_SLIDER_STYLE = """
QSlider::groove:vertical {
    background: #3a3a3a;
    width: 6px;
    border-radius: 3px;
    margin: 0px;
}
QSlider::handle:vertical {
    background: #6b5a47;
    border: 1px solid #8a7a67;
    height: 18px;
    width: 18px;
    margin: -6px -6px -6px -6px;
    border-radius: 9px;
}
QSlider::handle:vertical:hover {
    background: #8a7a67;
}
"""
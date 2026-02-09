# utils/settings.py
"""Settings persistence using JSON file."""

import json
import os

SETTINGS_FILE = "animator_settings.json"

def load_settings(widget):
    """Load saved settings into UI widgets."""
    if not os.path.exists(SETTINGS_FILE):
        return

    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
        widget.unit_combo.setCurrentText(data.get("unit", "letter"))
        widget.trans_combo.setCurrentText(data.get("transition", "fade"))
        widget.frames_spin.setValue(data.get("frames", 4))
        widget.flicker_check.setChecked(data.get("flicker", True))
        widget.strength_spin.setValue(data.get("strength", 0.08))
        widget.width_spin.setValue(data.get("width", 1920))
        widget.height_spin.setValue(data.get("height", 1080))
        widget.wrap_spin.setValue(data.get("wrap_width", 60))
        widget.input_font_slider.setValue(data.get("input_font_size", 18))
    except Exception as e:
        print(f"Settings load error: {e}")

def save_settings(widget):
    """Save current UI state to JSON."""
    data = {
        "unit": widget.unit_combo.currentText(),
        "transition": widget.trans_combo.currentText(),
        "frames": widget.frames_spin.value(),
        "flicker": widget.flicker_check.isChecked(),
        "strength": widget.strength_spin.value(),
        "width": widget.width_spin.value(),
        "height": widget.height_spin.value(),
        "wrap_width": widget.wrap_spin.value(),
        "input_font_size": widget.input_font_slider.value(),
    }
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Settings save error: {e}")
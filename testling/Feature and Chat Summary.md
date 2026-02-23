Project: Cozy Animator – Frame SequenceCore idea: A cozy, dark-themed writing/animation tool where typed text auto-animates in a live preview (fade/stamp transitions, flicker, per-letter/word pacing).
UI layout: Split-screen (left: tall text input + controls; right: fixed-size preview + scrubber + play/pause). No rescaling/jumps during typing or status changes.
Preview: Locked to 4:3 aspect ratio (640×480 base), fixed policy + size to prevent layout shifts. Frames generated in background thread (QThread) to avoid UI freeze.
Key features:Auto-preview on typing pause (300 ms debounce)
Real-time updates on Frames/unit & Strength sliders (100 ms debounce)
Persistent pause (no auto-resume on typing/settings change; regenerate only on explicit resume)
Custom scrollbar slider (vertical on right of input)
Live word/char count
Input font size slider
Clear Text button
Settings persistence (JSON save/load on closeEvent)
Spellchecker (PyEnchant): red wavy underlines + right-click suggestions, debounced to 1 second inactivity

Dependencies: PySide6, pygame, pyenchant (requirements.txt updated)
Structure: main.py (entry), main_window.py (UI/logic), styles/theme.py, utils/{settings, helpers, spellchecker}.py, bin/setup_structure.py
Repo: https://github.com/agudmund/cozy-animator (public, MIT licensed)
Known pain points solved: Preview rescaling, typing lag, circular imports, missing Qt imports (QSlider, QSizePolicy, QGraphicsDropShadowEffect), native scrollbar leaks, crash on large pastes (background thread + max frames cap)
Current state: Stable, crash-resistant, cozy, functional spellcheck, persistent settings/pause, ready for creative use or next polish


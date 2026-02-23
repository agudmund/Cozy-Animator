# main_window.py
import logging
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox, QSpinBox, QCheckBox, QPushButton,
    QDoubleSpinBox, QMessageBox, QProgressBar, QToolButton,
    QSlider, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor, QImage, QPixmap, QTextCursor

from styles.theme import (
    BG_COLOR, TEXT_COLOR, ACCENT_MUTED, BUTTON_BG, BUTTON_BORDER,
    BUTTON_HOVER, SHADOW_COLOR, CUSTOM_SCROLLBAR_STYLE,
    CUSTOM_VERTICAL_SLIDER_STYLE, SETTINGS_FILE
)
from utils.settings import load_settings, save_settings
from utils.helpers import wrap_text
from utils.spellchecker import SpellHighlighter, show_spell_suggestions

DRAFT_PATH = Path("last_draft.txt")

logger = logging.getLogger(__name__)


class FrameGeneratorWorker(QThread):
    frames_ready = Signal(list)  # list of PIL.Image
    progress = Signal(int)
    error = Signal(str)

    def __init__(self, text, unit_type, transition, frames_per_unit,
                 flicker, flicker_strength, width, height, wrap_width,
                 debug_overlay=False, max_frames_debug=60):
        super().__init__()
        self.text = text
        self.unit_type = unit_type
        self.transition = transition
        self.frames_per_unit = frames_per_unit
        self.flicker = flicker
        self.flicker_strength = flicker_strength
        self.width = width
        self.height = height
        self.wrap_width = wrap_width
        self.debug_overlay = debug_overlay
        self.max_frames_debug = max_frames_debug

    def run(self):
        try:
            pil_frames = []
            if not self.text.strip():
                logger.debug("Empty text → no frames")
                self.frames_ready.emit([])
                return

            font = None
            for name in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
                try:
                    font = ImageFont.truetype(name, 80)
                    logger.info("Font loaded: %s", name)
                    break
                except IOError:
                    continue
            if font is None:
                font = ImageFont.load_default()
                logger.warning("Using default font (may render small)")

            preview_margin = 60
            base_y = 80

            units = self.text.split() if self.unit_type == 'word' else list(self.text)
            prev_text = ''
            frame_count = 0
            total_frames = len(units) * self.frames_per_unit

            for idx, unit in enumerate(units):
                if frame_count >= self.max_frames_debug:
                    logger.warning("Debug cap reached (%d)", self.max_frames_debug)
                    break

                unit_to_add = unit + ' ' if self.unit_type == 'word' and idx < len(units)-1 else unit

                if self.transition == 'fade':
                    for i in range(self.frames_per_unit):
                        if frame_count >= self.max_frames_debug:
                            break
                        alpha = int(255 * (i + 1) / self.frames_per_unit)
                        reveal_len = int(len(unit_to_add) * (i + 1) / self.frames_per_unit)
                        current_text = prev_text + unit_to_add[:reveal_len]
                        wrapped = wrap_text(current_text, self.wrap_width)

                        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(img)

                        if self.debug_overlay:
                            draw.rectangle((20, 20, 380, 140), fill=(255, 0, 0, 140),
                                           outline=(255, 255, 0, 220), width=4)
                            draw.text((40, 50), "DEBUG OVERLAY VISIBLE", font=font, fill=(0, 255, 0, 255))

                        y = base_y
                        factor = 1 + random.uniform(-self.flicker_strength, self.flicker_strength) if self.flicker else 1.0
                        bright = min(255, int(255 * factor))
                        color = (bright, bright, bright, alpha)

                        for line in wrapped:
                            draw.text((preview_margin, y), line, font=font, fill=color)
                            y += int(font.size * 1.2 if hasattr(font, 'size') else 36)

                        pil_frames.append(img.copy())
                        frame_count += 1
                        self.progress.emit(int(frame_count / total_frames * 100) if total_frames else 0)

                    prev_text += unit_to_add

                else:
                    prev_text += unit_to_add
                    wrapped = wrap_text(prev_text, self.wrap_width)

                    for _ in range(self.frames_per_unit):
                        if frame_count >= self.max_frames_debug:
                            break

                        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(img)

                        if self.debug_overlay:
                            draw.rectangle((20, 20, 380, 140), fill=(255, 0, 0, 140),
                                           outline=(255, 255, 0, 220), width=4)
                            draw.text((40, 50), "DEBUG OVERLAY VISIBLE", font=font, fill=(0, 255, 0, 255))

                        y = base_y
                        factor = 1 + random.uniform(-self.flicker_strength, self.flicker_strength) if self.flicker else 1.0
                        bright = min(255, int(255 * factor))
                        color = (bright, bright, bright, 255)

                        for line in wrapped:
                            draw.text((preview_margin, y), line, font=font, fill=color)
                            y += int(font.size * 1.2 if hasattr(font, 'size') else 36)

                        pil_frames.append(img.copy())
                        frame_count += 1
                        self.progress.emit(int(frame_count / total_frames * 100) if total_frames else 0)

            logger.info("Worker complete – %d PIL images ready", len(pil_frames))
            self.frames_ready.emit(pil_frames)

        except Exception as e:
            logger.exception("Worker failed")
            self.error.emit(str(e))


class TextAnimatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cozy Animator – Frame Sequence 🌱")
        self.resize(1000, 780)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR};")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.status_label = QLabel("Ready 💕")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color:{ACCENT_MUTED};")

        split_layout = QHBoxLayout()
        split_layout.setSpacing(24)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(16)

        self.is_typing = False
        self.typing_cooldown_timer = QTimer(self)
        self.typing_cooldown_timer.setSingleShot(True)
        self.typing_cooldown_timer.setInterval(1400)
        self.typing_cooldown_timer.timeout.connect(self._on_typing_cooldown)

        self._setup_left_panel()
        split_layout.addWidget(self.left_panel, stretch=1)

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(16)

        self._setup_right_panel()
        split_layout.addWidget(self.right_panel, stretch=1)

        self.main_layout.addLayout(split_layout, stretch=1)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(16)
        footer_layout.addWidget(self.progress, stretch=1)
        footer_layout.addWidget(self.status_label, stretch=0)
        footer_widget = QWidget()
        footer_widget.setLayout(footer_layout)
        self.main_layout.addWidget(footer_widget)

        self.spellcheck_timer = QTimer(self)
        self.spellcheck_timer.setSingleShot(True)
        self.spellcheck_timer.timeout.connect(self._run_spellcheck)
        self.spellcheck_timer.setInterval(1000)

        self._setup_timers()
        self._setup_connections()

        self.preview_frames = []
        self.current_frame_idx = 0
        self.is_preview_active = False
        self.is_paused = False
        self.is_scrubbing = False

        self.generator_worker = None
        self.spell_highlighter = SpellHighlighter(self.text_edit.document())

        load_settings(self)
        self._load_last_draft()

        self._update_input_font_size()
        self.input_font_slider.valueChanged.connect(self._update_input_font_size)

        self.update_scroll_slider_range()
        self.text_edit.textChanged.connect(self.update_scroll_slider_range)

        self.text_edit.setFocus()
        self.text_edit.moveCursor(QTextCursor.End)
        self.activateWindow()
        self.update_count_label()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(SHADOW_COLOR)
        self.central_widget.setGraphicsEffect(shadow)

        logger.info("Fresh start — all lessons learned, ready to shine 💜")

    def _setup_left_panel(self):
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.addStretch()
        for symbol, tooltip in [("📜", "Log"), ("📋", "Features"), ("⚙", "Settings")]:
            btn = QToolButton()
            btn.setText(symbol)
            btn.setFont(QFont("Segoe UI Emoji", 18))
            btn.setStyleSheet(
                f"QToolButton {{background:transparent; color:{ACCENT_MUTED}; border:none;}} "
                f"QToolButton:hover {{color:{TEXT_COLOR};}}"
            )
            btn.setFixedSize(36, 36)
            btn.setToolTip(tooltip)
            top_layout.addWidget(btn)
        self.left_layout.addWidget(top_bar)

        title = QLabel("Generate Animated Text Frames")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(title)

        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type or paste your poem / phrase here...")
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setStyleSheet(
            f"background: #2a2a2a; border:1px solid {BUTTON_BORDER}; border-radius:10px; "
            f"padding:14px; color:{TEXT_COLOR}; line-height:140%;"
        )
        self.text_edit.viewport().setStyleSheet(CUSTOM_SCROLLBAR_STYLE)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setMinimumHeight(140)
        input_layout.addWidget(self.text_edit, stretch=1)

        slider_container = QWidget()
        slider_container.setFixedWidth(30)
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(0)

        self.scroll_slider = QSlider(Qt.Vertical)
        self.scroll_slider.setRange(0, 100)
        self.scroll_slider.setValue(0)
        self.scroll_slider.setInvertedAppearance(True)
        self.scroll_slider.setStyleSheet(CUSTOM_VERTICAL_SLIDER_STYLE)
        slider_layout.addWidget(self.scroll_slider)
        input_layout.addWidget(slider_container)

        self.left_layout.addWidget(input_container, stretch=1)

        font_row = QHBoxLayout()
        font_lbl = QLabel("Input font size:")
        font_lbl.setStyleSheet(f"color:{ACCENT_MUTED};")
        self.input_font_slider = QSlider(Qt.Horizontal)
        self.input_font_slider.setRange(12, 32)
        self.input_font_slider.setValue(18)
        self.input_font_slider.setTickPosition(QSlider.TicksBelow)
        self.input_font_slider.setTickInterval(2)
        font_row.addWidget(font_lbl)
        font_row.addWidget(self.input_font_slider)
        self.left_layout.addLayout(font_row)

        self.pause_while_typing = QCheckBox("Pause preview while typing")
        self.pause_while_typing.setChecked(False)
        self.pause_while_typing.stateChanged.connect(self._on_pause_typing_changed)
        self.left_layout.addWidget(self.pause_while_typing)

        debug_row = QHBoxLayout()
        self.debug_overlay_check = QCheckBox("Show debug overlay (red/green)")
        self.debug_overlay_check.setChecked(True)
        self.debug_overlay_check.stateChanged.connect(self._trigger_preview_update)
        debug_row.addWidget(self.debug_overlay_check)

        self.disable_preview_check = QCheckBox("Disable preview generation")
        self.disable_preview_check.stateChanged.connect(self._on_disable_preview_changed)
        debug_row.addWidget(self.disable_preview_check)
        self.left_layout.addLayout(debug_row)

        self.count_label = QLabel("Words: 0 • Characters: 0")
        self.count_label.setStyleSheet(f"color: {ACCENT_MUTED}; font-size: 13px; text-align: right;")
        self.left_layout.addWidget(self.count_label)

        controls = QVBoxLayout()
        controls.setSpacing(10)

        self.unit_combo = QComboBox(); self.unit_combo.addItems(["letter", "word"])
        self.trans_combo = QComboBox(); self.trans_combo.addItems(["fade", "stamp"])
        self.frames_spin = QSpinBox(); self.frames_spin.setRange(1, 30); self.frames_spin.setValue(4)
        self.flicker_check = QCheckBox("Brightness flicker"); self.flicker_check.setChecked(True)
        self.strength_spin = QDoubleSpinBox(); self.strength_spin.setRange(0.0, 0.5); self.strength_spin.setValue(0.08)
        self.width_spin = QSpinBox(); self.width_spin.setRange(640, 3840); self.width_spin.setValue(1920)
        self.height_spin = QSpinBox(); self.height_spin.setRange(480, 2160); self.height_spin.setValue(1080)

        row1 = QHBoxLayout()
        for lbl_text, w in [("Per:", self.unit_combo), ("Transition:", self.trans_combo), ("Frames/unit:", self.frames_spin)]:
            lbl = QLabel(lbl_text); lbl.setStyleSheet(f"color:{ACCENT_MUTED};")
            row1.addWidget(lbl); row1.addWidget(w)
        controls.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self.flicker_check)
        lbl_str = QLabel("Strength:"); lbl_str.setStyleSheet(f"color:{ACCENT_MUTED};")
        row2.addWidget(lbl_str); row2.addWidget(self.strength_spin)
        controls.addLayout(row2)

        res_row = QHBoxLayout()
        lbl_res = QLabel("Resolution:"); lbl_res.setStyleSheet(f"color:{ACCENT_MUTED};")
        res_row.addWidget(lbl_res); res_row.addWidget(self.width_spin)
        lbl_x = QLabel("×"); lbl_x.setStyleSheet(f"color:{ACCENT_MUTED};")
        res_row.addWidget(lbl_x); res_row.addWidget(self.height_spin)
        controls.addLayout(res_row)

        self.left_layout.addLayout(controls)

        btn_row = QHBoxLayout()
        self.generate_btn = QPushButton("Generate PNG Sequence")
        self.generate_btn.setFixedHeight(48)
        self.generate_btn.setStyleSheet(
            f"background:{BUTTON_BG}; border:1px solid {BUTTON_BORDER}; border-radius:10px; "
            f"color:{TEXT_COLOR}; font-weight:bold;"
        )
        self.generate_btn.clicked.connect(self.generate_frames)
        btn_row.addWidget(self.generate_btn)

        clear_btn = QPushButton("Clear Text")
        clear_btn.setFixedHeight(48)
        clear_btn.setStyleSheet(
            f"background:#444444; border:1px solid {BUTTON_BORDER}; border-radius:10px; "
            f"color:#e0e0e0; font-weight:bold;"
        )
        clear_btn.clicked.connect(self.clear_text)
        btn_row.addWidget(clear_btn)

        self.left_layout.addLayout(btn_row)

    def _setup_right_panel(self):
        preview_title = QLabel("Preview (wrapped for readability)")
        preview_title.setStyleSheet(f"color:{ACCENT_MUTED}; font-size:13px;")
        self.right_layout.addWidget(preview_title)

        wrap_row = QHBoxLayout()
        wrap_lbl = QLabel("Wrap preview lines at:")
        wrap_lbl.setStyleSheet(f"color:{ACCENT_MUTED};")
        self.wrap_spin = QSpinBox()
        self.wrap_spin.setRange(40, 120)
        self.wrap_spin.setValue(60)
        self.wrap_spin.setSuffix(" chars")
        wrap_row.addWidget(wrap_lbl)
        wrap_row.addWidget(self.wrap_spin)
        self.right_layout.addLayout(wrap_row)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.preview_label.setStyleSheet("background: #000000; border:1px solid #444; border-radius:8px;")
        self.preview_label.setMinimumHeight(480)
        self.preview_label.setMaximumHeight(480)
        self.preview_label.setFixedWidth(640)

        self.preview_label.setScaledContents(True)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFocusPolicy(Qt.StrongFocus)
        self.preview_label.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.preview_label.setAttribute(Qt.WA_NoSystemBackground, False)

        self.right_layout.addWidget(self.preview_label, stretch=0)

        scrub_row = QHBoxLayout()
        scrub_lbl = QLabel("Scrub frame:")
        scrub_lbl.setStyleSheet(f"color:{ACCENT_MUTED};")
        self.scrub_slider = QSlider(Qt.Horizontal)
        self.scrub_slider.setRange(0, 0)
        self.scrub_slider.setStyleSheet("""
            QSlider::groove:horizontal {background:#3a3a3a; height:6px; border-radius:3px;}
            QSlider::handle:horizontal {background:#6b5a47; border:1px solid #8a7a67; width:18px; height:18px;
                                        margin:-6px -6px -6px -6px; border-radius:9px;}
            QSlider::handle:horizontal:hover {background:#8a7a67;}
        """)
        self.scrub_slider.sliderPressed.connect(self.pause_on_scrub)
        self.scrub_slider.sliderReleased.connect(self.resume_after_scrub)
        self.scrub_slider.valueChanged.connect(self.scrub_to_frame)
        scrub_row.addWidget(scrub_lbl)
        scrub_row.addWidget(self.scrub_slider)
        self.right_layout.addLayout(scrub_row)

        self.play_pause_btn = QPushButton("Pause Preview")
        self.play_pause_btn.setFixedHeight(36)
        self.play_pause_btn.setStyleSheet(
            f"background:{BUTTON_BG}; border:1px solid {BUTTON_BORDER}; border-radius:8px; color:{TEXT_COLOR};"
        )
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.right_layout.addWidget(self.play_pause_btn, alignment=Qt.AlignCenter)

    def _setup_timers(self):
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.update_preview_frame)

        self.preview_update_timer = QTimer(self)
        self.preview_update_timer.setSingleShot(True)
        self.preview_update_timer.timeout.connect(self._regenerate_preview)

    def _setup_connections(self):
        self.text_edit.textChanged.connect(self.update_count_label)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.textChanged.connect(self._trigger_preview_update)
        self.text_edit.textChanged.connect(self._reset_spellcheck_timer)
        self.text_edit.verticalScrollBar().valueChanged.connect(self.sync_slider_from_text)
        self.scroll_slider.valueChanged.connect(self.sync_text_from_slider)

        self.frames_spin.valueChanged.connect(self._update_preview_on_settings_change)
        self.strength_spin.valueChanged.connect(self._update_preview_on_settings_change)

        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_spell_menu)

    def _on_text_changed(self):
        self.is_typing = True
        self.typing_cooldown_timer.start(1400)

        if not self.pause_while_typing.isChecked():
            self.preview_timer.stop()

    def _on_typing_cooldown(self):
        self.is_typing = False
        if not self.pause_while_typing.isChecked():
            self._regenerate_preview()

    def _on_pause_typing_changed(self, state):
        if state == Qt.Checked:
            if self.generator_worker and self.generator_worker.isRunning():
                self.generator_worker.quit()
                self.generator_worker.wait(500)
            self.preview_timer.stop()
            self.status_label.setText("Preview paused (typing)")
        else:
            if self.preview_frames and not self.is_paused:
                self.preview_timer.start(66)
                self.status_label.setText("Preview playing…")

    def _on_disable_preview_changed(self, state):
        if state == Qt.Checked:
            self.preview_label.clear()
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Preview generation disabled\n(for testing)")
            self.scrub_slider.setRange(0, 0)
            self.preview_frames = []
            self.status_label.setText("Preview disabled")
            if self.generator_worker and self.generator_worker.isRunning():
                self.generator_worker.quit()
                self.generator_worker.wait(300)
        else:
            self.preview_label.clear()
            self.preview_label.setText("")
            self._regenerate_preview()

    def _trigger_preview_update(self):
        self.preview_update_timer.start(500)

    def _update_preview_on_settings_change(self):
        self.preview_update_timer.start(500)

    def _reset_spellcheck_timer(self):
        self.spellcheck_timer.start(1000)

    def _run_spellcheck(self):
        self.spell_highlighter.rehighlight()

    def show_spell_menu(self, pos):
        show_spell_suggestions(self.text_edit, pos)

    def update_preview_frame(self):
        if not self.preview_frames:
            return
        pix = self.preview_frames[self.current_frame_idx]
        scaled = pix.scaled(
            self.preview_label.width(),
            self.preview_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.clear()
        self.preview_label.setPixmap(scaled)
        self.scrub_slider.setValue(self.current_frame_idx)
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.preview_frames)

    def _regenerate_preview(self):
        if self.disable_preview_check.isChecked():
            return

        if self.is_typing or self.pause_while_typing.isChecked():
            return

        if self.generator_worker and self.generator_worker.isRunning():
            return

        text = self.text_edit.toPlainText().strip()
        if not text:
            self.preview_label.clear()
            self.preview_label.setPixmap(QPixmap())
            self.scrub_slider.setRange(0, 0)
            self.preview_frames = []
            self.status_label.setText("Ready")
            return

        self.preview_label.clear()  # ensure clean slate before new generation
        self.status_label.setText("Generating preview... (we've got this, my love 💕)")
        QApplication.processEvents()

        self.generator_worker = FrameGeneratorWorker(
            text=text,
            unit_type=self.unit_combo.currentText(),
            transition=self.trans_combo.currentText(),
            frames_per_unit=self.frames_spin.value(),
            flicker=self.flicker_check.isChecked(),
            flicker_strength=self.strength_spin.value(),
            width=self.width_spin.value(),
            height=self.height_spin.value(),
            wrap_width=self.wrap_spin.value(),
            debug_overlay=self.debug_overlay_check.isChecked(),
            max_frames_debug=60
        )

        self.generator_worker.frames_ready.connect(self._on_frames_ready)
        self.generator_worker.progress.connect(self._on_generator_progress)
        self.generator_worker.error.connect(self._on_generator_error)
        self.generator_worker.start()

    def _on_frames_ready(self, pil_images):
        self.preview_label.clear()  # always start fresh

        self.preview_frames = []

        for idx, pil_img in enumerate(pil_images):
            qimage = QImage(
                pil_img.tobytes(),
                pil_img.width,
                pil_img.height,
                QImage.Format_RGBA8888
            )

            if qimage.isNull():
                logger.critical("QImage construction failed for frame %d", idx)
                continue

            logger.info("QImage created OK for frame %d – size %dx%d", 
                        idx, qimage.width(), qimage.height())

            pixmap = QPixmap.fromImage(qimage)
            if pixmap.isNull():
                logger.error("QPixmap.fromImage returned null for frame %d", idx)
                continue

            scaled = pixmap.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if scaled.isNull():
                logger.warning("Scaled pixmap null for frame %d", idx)
                continue

            self.preview_frames.append(scaled)
            logger.debug("Frame %d ready for display", idx)

        if not self.preview_frames:
            self.status_label.setText("No valid frames generated")
            logger.warning("Zero frames after processing – check PIL drawing or conversion")
            return

        self.scrub_slider.setRange(0, len(self.preview_frames) - 1)
        self.current_frame_idx = 0
        self.scrub_to_frame(0)
        logger.info("Frames loaded – preview should now show content 💚")

        if not self.is_paused:
            self.preview_timer.start(66)
            self.is_preview_active = True
            self.status_label.setText("Preview playing… (look at us go, darling! 🌟)")
        else:
            self.status_label.setText("Preview ready (paused)")

    def _on_generator_progress(self, percent):
        self.status_label.setText(f"Generating... {percent}%")

    def _on_generator_error(self, msg):
        self.status_label.setText(f"Error: {msg}")

    def pause_on_scrub(self):
        self.is_scrubbing = True
        self.preview_timer.stop()

    def resume_after_scrub(self):
        self.is_scrubbing = False
        if self.is_preview_active and not self.is_paused:
            self.preview_timer.start(66)

    def scrub_to_frame(self, value):
        if not self.preview_frames or value >= len(self.preview_frames):
            return

        pix = self.preview_frames[value]
        if pix.isNull():
            logger.error("Null pixmap at frame %d", value)
            return

        self.preview_label.clear()
        scaled = pix.scaled(
            self.preview_label.width(),
            self.preview_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        if scaled.isNull():
            logger.error("Scaled pixmap null at frame %d", value)
            return

        self.preview_label.setPixmap(scaled)
        self.preview_label.update()
        self.preview_label.repaint()
        self.preview_label.setUpdatesEnabled(False)
        self.preview_label.setUpdatesEnabled(True)

    def toggle_play_pause(self):
        if not self.preview_frames:
            return
        if self.is_paused:
            self.preview_timer.start(66)
            self.play_pause_btn.setText("Pause Preview")
            self.is_paused = False
            self.status_label.setText("Preview playing…")
        else:
            self.preview_timer.stop()
            self.play_pause_btn.setText("Resume Preview")
            self.is_paused = True
            self.status_label.setText("Preview paused")

    def generate_frames(self):
        QMessageBox.information(self, "Export", "PNG sequence generation not implemented yet.")

    def clear_text(self):
        self.text_edit.clear()
        self.preview_label.clear()
        self.preview_label.setPixmap(QPixmap())
        self.scrub_slider.setRange(0, 0)
        self.preview_frames = []
        self.current_frame_idx = 0
        self.preview_timer.stop()
        self.is_preview_active = False
        self.is_paused = False
        self.play_pause_btn.setText("Pause Preview")
        self.status_label.setText("Ready")
        self.update_count_label()

    def _update_input_font_size(self):
        size = self.input_font_slider.value()
        font = QFont("Segoe UI", size)
        self.text_edit.setCurrentFont(font)
        self.text_edit.setFont(font)

    def sync_slider_from_text(self, value):
        self.scroll_slider.blockSignals(True)
        self.scroll_slider.setValue(value)
        self.scroll_slider.blockSignals(False)

    def sync_text_from_slider(self, value):
        self.text_edit.verticalScrollBar().setValue(value)

    def update_scroll_slider_range(self):
        max_scroll = self.text_edit.verticalScrollBar().maximum()
        self.scroll_slider.setRange(0, max_scroll if max_scroll > 0 else 100)

    def update_count_label(self):
        text = self.text_edit.toPlainText().strip()
        words = len(text.split())
        chars = len(text)
        self.count_label.setText(f"Words: {words} • Characters: {chars}")

    def closeEvent(self, event):
        self.preview_timer.stop()
        if self.generator_worker and self.generator_worker.isRunning():
            self.generator_worker.requestInterruption()
            self.generator_worker.quit()
            if not self.generator_worker.wait(5000):
                logger.warning("Generator thread timeout – forced terminate")
                self.generator_worker.terminate()
                self.generator_worker.wait(1000)
        self._save_draft()
        save_settings(self)
        super().closeEvent(event)

    def _load_last_draft(self):
        if not DRAFT_PATH.exists():
            logger.debug("No draft file found")
            return
        try:
            with open(DRAFT_PATH, "r", encoding="utf-8") as f:
                text = f.read().rstrip()
            self.text_edit.setPlainText(text)
            logger.info("Draft loaded – %d characters", len(text))
            # Give Qt a moment to process text change
            QTimer.singleShot(300, self._trigger_preview_update)
            self.status_label.setText("Last draft loaded")
        except Exception as e:
            logger.error("Draft load failed: %s", e)
            self.status_label.setText(f"Could not load draft: {e}")

    def _save_draft(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            return
        try:
            with open(DRAFT_PATH, "w", encoding="utf-8") as f:
                f.write(text)
            logger.debug("Draft saved")
        except Exception as e:
            logger.error("Draft save failed: %s", e)


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)-7s %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    app = QApplication(sys.argv)
    window = TextAnimatorWindow()
    window.show()
    sys.exit(app.exec())
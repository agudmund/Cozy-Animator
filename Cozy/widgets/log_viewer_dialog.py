# widgets/log_viewer_dialog.py
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget,
    QTextBrowser, QSlider, QLineEdit,
    QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QFont, QColor, QTextCharFormat, QTextCursor,
    QTextDocument
)

class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Today's Log   📜")
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        self.logger = parent.logger if hasattr(parent, 'logger') else None

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter log messages…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a;
                border: 1px solid #4a3a2f;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #8a7a67; }
        """)
        self.search_input.textChanged.connect(self._debounce_filter)
        left_layout.addWidget(self.search_input)

        self.log_display = QTextBrowser()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 11))
        self.log_display.setStyleSheet("""
            QTextBrowser {
                background: #222;
                color: #e0e0e0;
                border: none;
            }
        """)
        left_layout.addWidget(self.log_display, 1)

        main_layout.addWidget(left, 1)

        slider_container = QWidget()
        slider_container.setFixedWidth(44)
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 10, 0, 10)
        slider_layout.setSpacing(0)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setInvertedAppearance(True)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: #3a3a3a;
                width: 6px;
                border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: #6b5a47;
                border: 1px solid #8a7a67;
                height: 20px;
                width: 20px;
                margin: -7px -7px -7px -7px;
                border-radius: 10px;
            }
            QSlider::handle:vertical:hover { background: #8a7a67; }
        """)
        self.slider.valueChanged.connect(self._on_slider_moved)
        slider_layout.addWidget(self.slider, 1)

        main_layout.addWidget(slider_container)

        self.logs_directory = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.logs_directory, exist_ok=True)

        self.current_date_str = datetime.now().strftime("%Y-%m-%d")
        self.current_log_file_path = os.path.join(
            self.logs_directory,
            f"cozy_animator_{self.current_date_str}.log"
        )

        self.full_content = ""
        self.lines = []
        self.last_mtime = 0
        self.last_filter_text = ""

        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(250)
        self.filter_timer.timeout.connect(self._apply_filter)

        # Refresh timer – checks file changes while dialog is open
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(5000)  # every 5 seconds
        self.refresh_timer.timeout.connect(self._try_refresh_log)

        self.log_display.verticalScrollBar().valueChanged.connect(self._sync_slider_from_text)
        self.log_display.document().contentsChange.connect(self._update_slider_range)


    def showEvent(self, event):
        super().showEvent(event)
        ardivaardark = not self.full_content
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s <<<<<<<<<<<<<<<<<<<<<<<<<<" % ardivaardark)
        # if not self.full_content:
        self._load_and_display()
        self._update_slider_range()
        self.refresh_timer.start()  # start tailing when shown

    def hideEvent(self, event):
        super().hideEvent(event)
        self.refresh_timer.stop()  # pause tailing when hidden

    def closeEvent(self, event):
        self.refresh_timer.stop()
        self.filter_timer.stop()
        super().closeEvent(event)

    def _debounce_filter(self):
        self.filter_timer.start()
 
    def _get_current_log_path(self):
        return self.current_log_file_path

    def _load_and_display(self, force=False):
        path = self._get_current_log_path()
        if not os.path.exists(path):
            self.log_display.setPlainText(
                "No log entries yet today.\n\n"
                "Your cozy session is still young… ☕"
            )
            self.full_content = ""
            self.lines = []
            self._update_slider_range()
            return

        mtime = os.path.getmtime(path)
        if not force and mtime == self.last_mtime:
            return

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().rstrip()

        self.full_content = content
        self.lines = content.splitlines()
        self.last_mtime = mtime
        print ('moving to apply filter')
        self._apply_filter()

        sb = self.log_display.verticalScrollBar()
        if sb.value() >= sb.maximum() - 100 or sb.value() == 0:
            sb.setValue(sb.maximum())

        self._update_slider_range()

    def _try_refresh_log(self):
        path = self._get_current_log_path()
        if not os.path.exists(path):
            return

        mtime = os.path.getmtime(path)
        if mtime != self.last_mtime:
            print("Log file updated — refreshing view")
            self._load_and_display(force=True)
            # Keep current scroll position if user is reading older parts
            # or force to bottom:
            # sb = self.log_display.verticalScrollBar()
            # sb.setValue(sb.maximum())

    def _apply_filter(self):
        term = self.search_input.text().strip().lower()
        self.last_filter_text = term  # always update

        self.log_display.clear()

        if not term:
            self.log_display.setPlainText(self.full_content)
            self.log_display.repaint()
            QApplication.processEvents()
        else:
            matched_lines = [line for line in self.lines if term in line.lower()]
            if not matched_lines:
                self.log_display.setPlainText(f'No matches for "{term}"')
            else:
                filtered_text = "\n".join(matched_lines)
                self.log_display.setPlainText(filtered_text)

                doc = self.log_display.document()
                cursor = QTextCursor(doc)
                cursor.beginEditBlock()

                cursor.setPosition(0)
                while True:
                    cursor = doc.find(term, cursor)
                    if cursor.isNull():
                        break

                    fmt = QTextCharFormat()
                    fmt.setBackground(QColor("#5a4a2f"))
                    fmt.setForeground(QColor("#ffcc66"))
                    cursor.mergeCharFormat(fmt)

                    cursor.setPosition(cursor.position() + len(term))

                cursor.endEditBlock()

                self.log_display.repaint()
                QApplication.processEvents()

        sb = self.log_display.verticalScrollBar()
        sb.setValue(sb.maximum())
        self._update_slider_range()
        
    def _update_slider_range(self):
        max_v = self.log_display.verticalScrollBar().maximum()
        self.slider.setRange(0, max_v if max_v > 0 else 100)
        if max_v > 0:
            self.slider.setValue(max_v)

    def _on_slider_moved(self, value):
        self.log_display.verticalScrollBar().setValue(value)

    def _sync_slider_from_text(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)

    def closeEvent(self, event):
        self.refresh_timer.stop()
        self.filter_timer.stop()
        super().closeEvent(event)
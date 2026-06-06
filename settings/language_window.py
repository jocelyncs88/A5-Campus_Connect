# ==============================================================
# FILE: settings/language_window.py
# TUGAS: Panel pengaturan bahasa (Language Setting)
#        Campus Connect — berlaku sama untuk semua role:
#        admin, mahasiswa, eo, umum (guest)
#
# SPESIFIKASI FONT:
#   "Language Setting"              → size 55, #516465, bold
#   "Select your preferred..."      → size 20, #828282
#   "App Language"                  → size 27, #828282, bold
#   "Default Language"              → size 30, #516465, bold
#   "Choose the main language..."   → size 25, #828282
#   "English" / "Indonesia"         → size 14, #747C86
#   Garis pembatas                  → #888780, height 1
# ==============================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QSizePolicy, QScrollArea,
)

from language_manager import lang


# ─── WARNA ─────────────────────────────────────────────────────
C_TITLE    = "#516465"
C_SUBTITLE = "#828282"
C_OPTION   = "#747C86"
C_DIVIDER  = "#888780"
C_RADIO_ON = "#516465"
C_HOVER    = "#EEF4F4"


class _RadioOptionRow(QWidget):
    """Satu baris pilihan bahasa dengan custom radio button."""
    selected = pyqtSignal(str)

    def __init__(self, code: str, label: str, parent=None):
        super().__init__(parent)
        self.code = code
        self._checked = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(52)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        from PyQt5.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(14)

        self._radio_dot = QLabel()
        self._radio_dot.setFixedSize(22, 22)
        self._radio_dot.setAlignment(Qt.AlignCenter)
        self._update_radio_style()

        self._lbl = QLabel(label)
        font = QFont()
        font.setPointSize(13)
        self._lbl.setFont(font)
        self._lbl.setStyleSheet(f"color: {C_OPTION}; background: transparent;")

        layout.addWidget(self._radio_dot)
        layout.addWidget(self._lbl)
        layout.addStretch()

        self.setStyleSheet("background: transparent; border-radius: 8px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.code)

    def enterEvent(self, event):
        if not self._checked:
            self.setStyleSheet(f"background: {C_HOVER}; border-radius: 8px;")

    def leaveEvent(self, event):
        if not self._checked:
            self.setStyleSheet("background: transparent; border-radius: 8px;")

    def set_checked(self, checked: bool):
        self._checked = checked
        self._update_radio_style()
        if checked:
            self.setStyleSheet(f"background: {C_HOVER}; border-radius: 8px;")
        else:
            self.setStyleSheet("background: transparent; border-radius: 8px;")

    def update_label(self, text: str):
        self._lbl.setText(text)

    def _update_radio_style(self):
        if self._checked:
            self._radio_dot.setText("●")
            self._radio_dot.setStyleSheet(f"""
                QLabel {{
                    background: white;
                    border-radius: 11px;
                    border: 2px solid {C_RADIO_ON};
                    color: {C_RADIO_ON};
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
        else:
            self._radio_dot.setText("")
            self._radio_dot.setStyleSheet(f"""
                QLabel {{
                    background: white;
                    border-radius: 11px;
                    border: 2px solid {C_DIVIDER};
                }}
            """)


def _make_divider() -> QFrame:
    """Garis pembatas: #888780, weight 871 (min-width), height 1."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Plain)
    line.setMinimumWidth(871)
    line.setMaximumWidth(16777215)
    line.setFixedHeight(1)
    line.setStyleSheet(f"""
        QFrame {{
            background-color: {C_DIVIDER};
            border: none;
            max-height: 1px;
            min-height: 1px;
        }}
    """)
    return line


class LanguagePanel(QWidget):
    """
    Panel Language Setting untuk semua role pengguna.
    Dipasang sebagai salah satu halaman di QStackedWidget Settings.
    """
    language_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._build_ui()
        lang.language_changed.connect(self._retranslate)

    # ─────────────────────────────────────────────────────────
    # BANGUN UI
    # ─────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(0)

        # "Language Setting" — size 55, #516465, bold
        self._lbl_title = QLabel(lang.t("lang.panel_title"))
        f = QFont(); f.setPointSize(30); f.setBold(True)
        self._lbl_title.setFont(f)
        self._lbl_title.setStyleSheet(f"color: {C_TITLE}; background: transparent;")
        self._lbl_title.setWordWrap(True)
        layout.addWidget(self._lbl_title)

        layout.addSpacing(6)

        # "Select your preferred language ..." — size 20, #828282
        self._lbl_subtitle = QLabel(lang.t("lang.panel_subtitle"))
        f2 = QFont(); f2.setPointSize(13)
        self._lbl_subtitle.setFont(f2)
        self._lbl_subtitle.setStyleSheet(f"color: {C_SUBTITLE}; background: transparent;")
        self._lbl_subtitle.setWordWrap(True)
        layout.addWidget(self._lbl_subtitle)

        layout.addSpacing(32)

        # garis pembatas atas
        layout.addWidget(_make_divider())
        layout.addSpacing(28)

        # "App Language" — size 27, #828282, bold
        self._lbl_section = QLabel(lang.t("lang.section_label"))
        f3 = QFont(); f3.setPointSize(15); f3.setBold(True)
        self._lbl_section.setFont(f3)
        self._lbl_section.setStyleSheet(f"color: {C_SUBTITLE}; background: transparent;")
        layout.addWidget(self._lbl_section)

        layout.addSpacing(24)

        # Card Default Language
        layout.addWidget(self._build_language_card())

        layout.addSpacing(28)

        # garis pembatas bawah
        layout.addWidget(_make_divider())

        layout.addStretch()

        outer.addWidget(scroll)

    def _build_language_card(self) -> QWidget:
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        from PyQt5.QtWidgets import QVBoxLayout
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(0, 8, 0, 8)
        vbox.setSpacing(8)

        # "Default Language" — size 30, #516465, bold
        self._lbl_default = QLabel(lang.t("lang.default_label"))
        f4 = QFont(); f4.setPointSize(16); f4.setBold(True)
        self._lbl_default.setFont(f4)
        self._lbl_default.setStyleSheet(f"color: {C_TITLE}; background: transparent;")
        vbox.addWidget(self._lbl_default)

        # "Choose the main language ..." — size 25, #828282
        self._lbl_choose = QLabel(lang.t("lang.default_desc"))
        f5 = QFont(); f5.setPointSize(12)
        self._lbl_choose.setFont(f5)
        self._lbl_choose.setStyleSheet(f"color: {C_SUBTITLE}; background: transparent;")
        self._lbl_choose.setWordWrap(True)
        vbox.addWidget(self._lbl_choose)

        vbox.addSpacing(12)

        # Opsi: English & Indonesia — size 14, #747C86
        self._opt_en = _RadioOptionRow("en", lang.t("lang.option_en"))
        self._opt_id = _RadioOptionRow("id", lang.t("lang.option_id"))

        self._opt_en.selected.connect(self._on_language_selected)
        self._opt_id.selected.connect(self._on_language_selected)

        vbox.addWidget(self._opt_en)
        vbox.addWidget(self._opt_id)

        self._sync_radio()
        return card

    # ─────────────────────────────────────────────────────────
    # LOGIKA BAHASA
    # ─────────────────────────────────────────────────────────
    def _on_language_selected(self, code: str):
        lang.set_language(code)
        self.language_changed.emit(code)

    def _sync_radio(self):
        c = lang.current
        self._opt_en.set_checked(c == "en")
        self._opt_id.set_checked(c == "id")

    def _retranslate(self, _code: str = ""):
        self._lbl_title.setText(lang.t("lang.panel_title"))
        self._lbl_subtitle.setText(lang.t("lang.panel_subtitle"))
        self._lbl_section.setText(lang.t("lang.section_label"))
        self._lbl_default.setText(lang.t("lang.default_label"))
        self._lbl_choose.setText(lang.t("lang.default_desc"))
        self._opt_en.update_label(lang.t("lang.option_en"))
        self._opt_id.update_label(lang.t("lang.option_id"))
        self._sync_radio()


# ─────────────────────────────────────────────────────────────
# PREVIEW STANDALONE
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("Language Setting — Preview")
    win.resize(1100, 720)
    win.setCentralWidget(LanguagePanel())
    win.show()
    sys.exit(app.exec_())
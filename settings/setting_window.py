# ==============================================================
# FILE: settings/setting_window.py
# Settings container for Campus Connect.
# Routes EO edit submissions into admin approval requests.
# ==============================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from settings.account_window import AccountPanel
from settings.notifications_window import NotificationsPanel
from settings.your_events_window import YourEventsPanel
from setting_item_widget import SettingItem


COLOR_PINK_LIGHT = "#F7CBCA"
COLOR_GRAY_LIGHT = "#D2E6E5"
COLOR_TEAL_DARK = "#516465"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED = "#9AABAB"
COLOR_DIVIDER = "#D2E6E5"

ROLE_ORGANIZER = "eo"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM = "umum"


class SettingsWindow(QWidget):
    minta_buka_add_event = pyqtSignal()

    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_window_root")

        self.user_data = user_data or {
            "nama": "",
            "bio": "",
            "email": "",
            "kontak": "",
            "role": ROLE_UMUM,
            "inisial": "",
        }
        self.role = self.user_data.get("role", ROLE_UMUM)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        id_lobster = QFontDatabase.addApplicationFont(
            os.path.join(base_dir, "assets", "LobsterTwo-Regular.ttf")
        )
        id_sans = QFontDatabase.addApplicationFont(
            os.path.join(base_dir, "assets", "GoogleSans_17pt-Regular.ttf")
        )
        self.font_lobster = (
            QFontDatabase.applicationFontFamilies(id_lobster)[0]
            if id_lobster != -1
            else "serif"
        )
        self.font_sans = (
            QFontDatabase.applicationFontFamilies(id_sans)[0]
            if id_sans != -1
            else "sans-serif"
        )

        self.setStyleSheet(f"""
            #settings_window_root {{
                background: transparent;
            }}
            #settings_window_root QWidget {{
                font-family: '{self.font_sans}';
            }}
        """)

        self.setup_ui()

    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self.buat_topbar())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        body_layout.addWidget(self.buat_sidebar())

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        self.panel_account = AccountPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget,
        )
        self.panel_your_events = YourEventsPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget,
        )
        self.panel_your_events.minta_edit_event.connect(self.buka_halaman_edit_event)
        self.panel_your_events.minta_buka_add_event.connect(self.buka_add_event)

        self.panel_notif = NotificationsPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget,
        )
        self.panel_appearance = self.buat_panel_appearance()
        self.panel_language = self.buat_panel_language()

        self.stacked_widget.addWidget(self.panel_account)
        self.stacked_widget.addWidget(self.panel_your_events)
        self.stacked_widget.addWidget(self.panel_notif)
        self.stacked_widget.addWidget(self.panel_appearance)
        self.stacked_widget.addWidget(self.panel_language)

        body_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addWidget(body, stretch=1)

        self.stacked_widget.setCurrentIndex(0)

    def buat_topbar(self):
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background-color: white; border-bottom: 1px solid %s;" % COLOR_DIVIDER)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(20, 0, 20, 0)

        icon_menu = QLabel("≡")
        icon_menu.setStyleSheet(f"font-size: 22px; color: {COLOR_TEXT_PRIMARY}; font-weight: bold;")

        lbl_title = QLabel("Settings")
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.btn_home = QPushButton("  Home")
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setIconSize(QSize(16, 16))
        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_home.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLOR_TEXT_PRIMARY};
                font-size: 13px; border: none; padding: 6px 12px;
            }}
            QPushButton:hover {{ color: {COLOR_TEAL_DARK}; font-weight: bold; }}
        """)
        self.btn_home.clicked.connect(self.close)

        avatar_text = self.user_data.get("inisial", "")
        avatar = QLabel(avatar_text)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {COLOR_TEAL_DARK}; color: white;
            font-weight: bold; font-size: 13px; border-radius: 18px;
        """)

        layout.addWidget(icon_menu)
        layout.addSpacing(10)
        layout.addWidget(lbl_title)
        layout.addSpacerItem(spacer)
        layout.addWidget(self.btn_home)
        layout.addSpacing(8)
        layout.addWidget(avatar)
        return topbar

    def buat_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"background-color: white; border-right: 1px solid {COLOR_DIVIDER};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        menus = [
            ("Account", 0, "profile"),
            ("Your events", 1, "event"),
            ("Notifications", 2, "bell"),
            ("Appearance", 3, "paint"),
            ("Language", 4, "language"),
        ]

        self.sidebar_buttons = []
        for label, index, icon_file in menus:
            btn = QPushButton(f"  {label}")
            btn.setIcon(QIcon(f"assets/{icon_file}.png"))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setStyleSheet(self._style_sidebar_btn(False))
            btn.clicked.connect(lambda checked, i=index: self.switch_panel(i))

            if label == "Your events" and self.role not in [ROLE_ORGANIZER, ROLE_MAHASISWA]:
                btn.hide()

            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        layout.addStretch()

        if self.sidebar_buttons:
            self.sidebar_buttons[0].setChecked(True)
            self.sidebar_buttons[0].setStyleSheet(self._style_sidebar_btn(True))

        return sidebar

    def _style_sidebar_btn(self, aktif=False):
        if aktif:
            return f"""
                QPushButton {{
                    background-color: {COLOR_GRAY_LIGHT};
                    color: {COLOR_TEAL_DARK}; font-weight: bold;
                    font-size: 13px; text-align: left; border: none;
                    border-left: 3px solid {COLOR_TEAL_DARK}; padding-left: 20px;
                }}
            """
        return f"""
            QPushButton {{
                background-color: transparent; color: {COLOR_TEXT_PRIMARY};
                font-size: 13px; text-align: left; border: none; padding-left: 23px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_GRAY_LIGHT}; color: {COLOR_TEAL_DARK};
            }}
        """

    def switch_panel(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.sidebar_buttons):
            aktif = i == index
            btn.setChecked(aktif)
            btn.setStyleSheet(self._style_sidebar_btn(aktif))

        if index == 1 and hasattr(self, "panel_your_events"):
            self.panel_your_events._render()

    def buka_add_event(self):
        self.minta_buka_add_event.emit()

    def buka_halaman_edit_event(self, data_event):
        from add_event_page import AddEventPage

        panel_edit = AddEventPage(data_event=data_event)
        panel_edit.dibatalkan.connect(lambda: self._tutup_edit_event(panel_edit))
        panel_edit.event_dipublikasi.connect(
            lambda form_data, ev=data_event, p=panel_edit: self._simpan_perubahan_event(ev, form_data, p)
        )

        self.stacked_widget.addWidget(panel_edit)
        self.stacked_widget.setCurrentWidget(panel_edit)

    def _tutup_edit_event(self, panel):
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.removeWidget(panel)
        panel.deleteLater()

    def _simpan_perubahan_event(self, existing_event, form_data, panel):
        import db_manager

        def _show_message(kind, title, text):
            box = QMessageBox(panel)
            box.setWindowTitle(title)
            box.setText(text)
            box.setStandardButtons(QMessageBox.Ok)
            box.setIcon(QMessageBox.Information if kind == "info" else QMessageBox.Warning)
            box.setStyleSheet("""
                QMessageBox { background-color: #ffffff; }
                QMessageBox QLabel { color: #1a1a1a; min-width: 320px; }
            """)

            ok_btn = box.button(QMessageBox.Ok)
            if ok_btn:
                ok_btn.setStyleSheet("""
                    QPushButton {
                        min-width: 80px;
                        padding: 6px 12px;
                        border: 1px solid #CBD5E0;
                        border-radius: 6px;
                        background-color: #f8fafc;
                        color: #1a1a1a;
                    }
                    QPushButton:hover { background-color: #eef2f7; }
                    QPushButton:pressed { background-color: #dde6ef; }
                """)
            box.exec_()

        try:
            tanggal_raw = form_data.get("tanggal", "")
            waktu_raw = form_data.get("waktu", "")
            try:
                from datetime import datetime

                months = [
                    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
                ]
                parsed = datetime.strptime(tanggal_raw, "%Y-%m-%d")
                tanggal_waktu_baru = f"{parsed.day:02d} {months[parsed.month - 1]} {parsed.year} {waktu_raw}".strip()
            except Exception:
                tanggal_waktu_baru = f"{tanggal_raw} {waktu_raw}".strip()

            request_payload = {
                "event_id": existing_event.get("event_id", ""),
                "requested_by_email": self.user_data.get("email", ""),
                "nama_event": form_data.get("nama_event", existing_event.get("nama_event", "")),
                "deskripsi_singkat": form_data.get("deskripsi_singkat", existing_event.get("deskripsi_singkat", "")),
                "gambar_poster": form_data.get("gambar_poster", existing_event.get("gambar_poster", "")),
                "jenis_event": form_data.get("jenis_event", existing_event.get("jenis_event", "")),
                "tanggal_waktu": tanggal_waktu_baru,
                "source": form_data.get("source", existing_event.get("source", "manual")),
                "kategori": form_data.get("kategori", existing_event.get("kategori", "")),
                "lokasi": form_data.get("lokasi", existing_event.get("lokasi", "")),
                "tipe_tiket": form_data.get("tipe_tiket", existing_event.get("tipe_tiket", "Free")),
                "harga_tiket": form_data.get("harga_tiket", existing_event.get("harga_tiket", "0")),
                "nama_eo": form_data.get("penyelenggara", existing_event.get("nama_eo", "")),
            }

            db_manager.create_event_update_request(request_payload)
            _show_message(
                "info",
                "Request Terkirim",
                "Perubahan event sudah dikirim ke admin untuk divalidasi."
            )
        except Exception as exc:
            _show_message("warn", "Error Database", f"Gagal mengirim request perubahan:\n{exc}")
            return

        self._tutup_edit_event(panel)
        if hasattr(self, "panel_your_events"):
            self.panel_your_events._render()

    def buat_panel_notif(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Notifications")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        if self.role == ROLE_ORGANIZER:
            deskripsi = "Atur kapan kamu ingin mendapat notifikasi tentang pendaftar event yang kamu buat."
        elif self.role == ROLE_MAHASISWA:
            deskripsi = "Atur kapan kamu ingin mendapat pengingat untuk event yang kamu ikuti."
        else:
            deskripsi = "Atur preferensi notifikasi umum kamu di sini."

        lbl_info = QLabel(deskripsi)
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        layout.addWidget(
            SettingItem(
                judul="New registrant",
                deskripsi="Get alerts every time a user registers",
                nama_setting="notif_registrant",
                default_on=True,
            )
        )
        layout.addStretch()
        return panel

    def buat_panel_appearance(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Appearance")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        lbl_info = QLabel("Pengaturan tema dan tampilan akan hadir di sprint berikutnya.")
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_info)
        layout.addStretch()
        return panel

    def buat_panel_language(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Language")
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        lbl_info = QLabel("Pengaturan bahasa antarmuka akan hadir di sprint berikutnya.")
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_info)
        layout.addStretch()
        return panel


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    user_dummy = {
        "nama": "",
        "bio": "",
        "email": "eo@gmail.com",
        "kontak": "",
        "role": ROLE_ORGANIZER,
        "inisial": "EO",
    }

    window = SettingsWindow(user_data=user_dummy)
    window.show()
    sys.exit(app.exec_())

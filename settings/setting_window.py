# ==============================================================
# FILE: settings/setting_window.py  (UPDATED)
# PERUBAHAN:
#   - buka_halaman_edit_event: connect event_dipublikasi ke
#     _simpan_perubahan_event agar edit tersimpan ke database
#   - _simpan_perubahan_event: method baru untuk UPDATE row event
#   - _tutup_edit_event: tidak berubah
# ==============================================================

import sys
import os
# Tambahkan root project ke sys.path agar bisa import toggle_widget,
# setting_item_widget, dll yang berada di root, bukan di folder settings/
# Ini diperlukan baik saat dijalankan langsung maupun via main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from settings.account_window import AccountPanel
from settings.your_events_window import YourEventsPanel
from settings.notifications_window import NotificationsPanel


COLOR_PINK_LIGHT   = "#F7CBCA"
COLOR_GRAY_LIGHT   = "#D2E6E5"
COLOR_TEAL_DARK    = "#516465"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED   = "#9AABAB"
COLOR_DIVIDER      = "#D2E6E5"

ROLE_ORGANIZER = "eo"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"


class SettingsWindow(QWidget):

    minta_buka_add_event = pyqtSignal()

    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)

        self.user_data = user_data or {
            "nama"   : "",
            "bio"    : "",
            "email"  : "",
            "kontak" : "",
            "role"   : ROLE_UMUM,
            "inisial": ""
        }
        self.role = self.user_data.get("role", ROLE_UMUM)

        self.setWindowTitle("Settings - Campus Connect")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        id_lobster = QFontDatabase.addApplicationFont(
            os.path.join(BASE_DIR, "assets", "LobsterTwo-Regular.ttf")
        )
        id_sans = QFontDatabase.addApplicationFont(
            os.path.join(BASE_DIR, "assets", "GoogleSans_17pt-Regular.ttf")
        )
        self.font_lobster = (
            QFontDatabase.applicationFontFamilies(id_lobster)[0]
            if id_lobster != -1 else "serif"
        )
        self.font_sans = (
            QFontDatabase.applicationFontFamilies(id_sans)[0]
            if id_sans != -1 else "sans-serif"
        )

        self.setStyleSheet(f"""
            QWidget {{
                font-family: '{self.font_sans}';
                background: transparent;
            }}
        """)

        self.setup_ui()

    # ----------------------------------------------------------
    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        topbar = self.buat_topbar()
        root_layout.addWidget(topbar)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = self.buat_sidebar()
        body_layout.addWidget(sidebar)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        self.panel_account = AccountPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget
        )
        self.panel_your_events = YourEventsPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget
        )
        self.panel_your_events.minta_edit_event.connect(self.buka_halaman_edit_event)
        self.panel_your_events.minta_buka_add_event.connect(self.buka_add_event)

        self.panel_notif = NotificationsPanel(
            user_data=self.user_data,
            stacked_widget=self.stacked_widget
        )
        self.panel_appearance = self.buat_panel_appearance()
        self.panel_language   = self.buat_panel_language()

        self.stacked_widget.addWidget(self.panel_account)      # index 0
        self.stacked_widget.addWidget(self.panel_your_events)  # index 1
        self.stacked_widget.addWidget(self.panel_notif)        # index 2
        self.stacked_widget.addWidget(self.panel_appearance)   # index 3
        self.stacked_widget.addWidget(self.panel_language)     # index 4

        body_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addWidget(body, stretch=1)

        self.stacked_widget.setCurrentIndex(0)

    # ----------------------------------------------------------
    def buka_add_event(self):
        self.btn_home.clicked.emit()
        self.minta_buka_add_event.emit()

    # ----------------------------------------------------------
    def buat_topbar(self):
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet(
            f"background-color: white; border-bottom: 1px solid {COLOR_DIVIDER};"
        )

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(20, 0, 20, 0)

        icon_menu = QLabel("≡")
        icon_menu.setStyleSheet(
            f"font-size: 22px; color: {COLOR_TEXT_PRIMARY}; font-weight: bold;"
        )

        lbl_title = QLabel("Settings")
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};"
        )

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

        inisial = self.user_data.get("inisial", "")
        avatar = QLabel(inisial if inisial else "")
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

    # ----------------------------------------------------------
    def buat_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            f"background-color: white; border-right: 1px solid {COLOR_DIVIDER};"
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        menus = [
            ("Account",       0, "profile"),
            ("Your events",   1, "event"),
            ("Notifications", 2, "bell"),
            ("Appearance",    3, "paint"),
            ("Language",      4, "language"),
        ]

        self.sidebar_buttons = []

        for label, index, icon_file in menus:
            btn = QPushButton(f"  {label}")
            btn.setIcon(QIcon(f"assets/{icon_file}.png"))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setStyleSheet(self._style_sidebar_btn(aktif=False))
            btn.clicked.connect(lambda checked, i=index: self.switch_panel(i))

            if label == "Your events" and self.role not in [ROLE_ORGANIZER, ROLE_MAHASISWA]:
                btn.hide()

            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        layout.addStretch()

        self.sidebar_buttons[0].setChecked(True)
        self.sidebar_buttons[0].setStyleSheet(self._style_sidebar_btn(aktif=True))

        return sidebar

    # ----------------------------------------------------------
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
        else:
            return f"""
                QPushButton {{
                    background-color: transparent; color: {COLOR_TEXT_PRIMARY};
                    font-size: 13px; text-align: left; border: none; padding-left: 23px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_GRAY_LIGHT}; color: {COLOR_TEAL_DARK};
                }}
            """

    # ----------------------------------------------------------
    def switch_panel(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.sidebar_buttons):
            aktif = (i == index)
            btn.setChecked(aktif)
            btn.setStyleSheet(self._style_sidebar_btn(aktif=aktif))

    # ----------------------------------------------------------
    # EDIT EVENT — dibuka dari YourEventsPanel saat icon edit diklik
    # ----------------------------------------------------------
    def buka_halaman_edit_event(self, data_event):
        """Buka AddEventPage dalam mode edit, pre-filled dengan data_event."""
        from add_event_page import AddEventPage

        panel_edit = AddEventPage(data_event=data_event)

        # Tombol Cancel → tutup tanpa simpan
        panel_edit.dibatalkan.connect(
            lambda: self._tutup_edit_event(panel_edit)
        )

        # Tombol "Simpan Perubahan" → update ke database
        panel_edit.event_dipublikasi.connect(
            lambda form_data, ev=data_event, p=panel_edit:
                self._simpan_perubahan_event(ev, form_data, p)
        )

        self.stacked_widget.addWidget(panel_edit)
        self.stacked_widget.setCurrentWidget(panel_edit)

    def _tutup_edit_event(self, panel):
        """Kembali ke Your Events dan hapus panel edit dari memori."""
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.removeWidget(panel)
        panel.deleteLater()

    def _simpan_perubahan_event(self, existing_event, form_data, panel):
        """
        UPDATE row event di database langsung, tanpa melewati prepare_update.

        Alasan bypass prepare_update:
          - Validasi form sudah dilakukan di AddEventPage.publikasi_event()
            sebelum sinyal di-emit.
          - prepare_update gagal karena existing_event dari DB hanya punya
            'tanggal_waktu' format Indonesian ("18 Mei 2026 10:00") tapi
            tidak punya key 'tanggal' dan 'waktu' terpisah yang dibutuhkan
            oleh build_event_payload → validasi gagal → dialog "Gagal Menyimpan".

        Strategy UPDATE:
          1. WHERE event_id = ?  (event manual: "MAN-xxxxxxxxxx")
          2. Fallback WHERE id = ? (integer PK) jika event_id tidak ditemukan
        """
        import sqlite3
        import db_manager

        # Identifier event
        event_id_target = (existing_event.get("event_id") or "").strip()
        db_id_target    = existing_event.get("id", "")   # integer PRIMARY KEY

        # Bangun tanggal_waktu format Indonesian agar konsisten dengan data lama di DB
        # Contoh: "2026-05-18" + "10:00"  →  "18 Mei 2026 10:00"
        tanggal_raw = form_data.get("tanggal", "")
        waktu_raw   = form_data.get("waktu",   "")
        try:
            from datetime import datetime
            _MONTHS = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember",
            ]
            parsed = datetime.strptime(tanggal_raw, "%Y-%m-%d")
            tanggal_waktu_baru = (
                f"{parsed.day:02d} {_MONTHS[parsed.month - 1]} {parsed.year}"
                f" {waktu_raw}"
            ).strip()
        except Exception:
            tanggal_waktu_baru = f"{tanggal_raw} {waktu_raw}".strip()

        # Nilai kolom yang akan di-UPDATE (form_data menang atas existing_event)
        nama_event    = form_data.get("nama_event",        existing_event.get("nama_event", ""))
        deskripsi     = form_data.get("deskripsi_singkat", existing_event.get("deskripsi_singkat", ""))
        jenis_event   = form_data.get("jenis_event",       existing_event.get("jenis_event", ""))
        kategori      = form_data.get("kategori",          existing_event.get("kategori", ""))
        gambar        = form_data.get("gambar_poster",     existing_event.get("gambar_poster", ""))
        lokasi        = form_data.get("lokasi",            existing_event.get("lokasi", ""))
        tipe_tiket    = form_data.get("tipe_tiket",        existing_event.get("tipe_tiket", "Free"))
        harga_tiket   = form_data.get("harga_tiket",       existing_event.get("harga_tiket", "0"))
        penyelenggara = form_data.get("penyelenggara",     existing_event.get("nama_eo", ""))

        _SQL = """
            UPDATE events SET
                nama_event        = ?,
                deskripsi_singkat = ?,
                jenis_event       = ?,
                kategori          = ?,
                tanggal_waktu     = ?,
                gambar_poster     = ?,
                lokasi            = ?,
                tipe_tiket        = ?,
                harga_tiket       = ?,
                nama_eo           = ?
            WHERE {where}
        """
        _VALUES = (
            nama_event, deskripsi, jenis_event, kategori,
            tanggal_waktu_baru, gambar, lokasi,
            tipe_tiket, harga_tiket, penyelenggara,
        )

        try:
            conn   = sqlite3.connect(db_manager.DB_NAME)
            cursor = conn.cursor()
            rows_affected = 0

            # 1. UPDATE by event_id (string)
            if event_id_target:
                cursor.execute(
                    _SQL.format(where="event_id = ?"),
                    _VALUES + (event_id_target,)
                )
                rows_affected = cursor.rowcount

            # 2. Fallback: UPDATE by integer id
            if rows_affected == 0 and db_id_target:
                cursor.execute(
                    _SQL.format(where="id = ?"),
                    _VALUES + (db_id_target,)
                )
                rows_affected = cursor.rowcount

            conn.commit()
            conn.close()

            if rows_affected == 0:
                QMessageBox.warning(
                    panel, "Tidak Ditemukan",
                    f"Event tidak ditemukan di database.\n"
                    f"event_id='{event_id_target}', db_id='{db_id_target}'"
                )
                return

            QMessageBox.information(panel, "Berhasil", "Event berhasil diperbarui! ✓")

        except Exception as e:
            QMessageBox.warning(
                panel, "Error Database",
                f"Gagal menyimpan perubahan:\n{e}"
            )
            return

        # Tutup panel edit dan refresh kartu Your Events
        self._tutup_edit_event(panel)
        if hasattr(self, "panel_your_events"):
            self.panel_your_events._render()

    # ----------------------------------------------------------
<<<<<<< HEAD
    # FUNGSI buat_panel_appearance()
    # Membangun panel "Appearance" berisi pengaturan tampilan
    # Tampilan panel ini SAMA untuk semua role user
    # ----------------------------------------------------------
=======
    # PANEL APPEARANCE & LANGUAGE
    # ----------------------------------------------------------
    def buat_panel_notif(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Notifications")
        lbl_judul.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};"
        )
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

        item = SettingItem(
            judul="New registrant",
            deskripsi="Get alerts every time a user registers",
            nama_setting="notif_registrant",
            default_on=True
        )
        layout.addWidget(item)
        layout.addStretch()
        return panel

>>>>>>> fitur-jocelyn
    def buat_panel_appearance(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel("Appearance")
        lbl_judul.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};"
        )
        layout.addWidget(lbl_judul)

        lbl_info = QLabel("Pengaturan tema dan tampilan akan hadir di sprint berikutnya.")
        lbl_info.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-style: italic;"
        )
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
        lbl_judul.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};"
        )
        layout.addWidget(lbl_judul)

        lbl_info = QLabel("Pengaturan bahasa antarmuka akan hadir di sprint berikutnya.")
        lbl_info.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-style: italic;"
        )
        layout.addWidget(lbl_info)
        layout.addStretch()
        return panel


# ==============================================================
# TESTING MANDIRI
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    user_dummy = {
        "nama": "", "bio": "", "email": "eo@gmail.com",
        "kontak": "", "role": ROLE_ORGANIZER, "inisial": "EO"
    }

    window = SettingsWindow(user_data=user_dummy)
    window.show()
    sys.exit(app.exec_())
# ==============================================================
# FILE: settings/setting_window.py
# Settings container for Campus Connect.
# Routes EO edit submissions into admin approval requests.
#
# FIX MULTILINGUAL (3 titik):
#   1. Popup sukses request edit event → lang.t(...)
#   2. Popup error database → lang.t(...)
#   3. buat_panel_notif() → semua string hardcoded pakai lang.t(...)
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
from settings.language_window import LanguagePanel
from setting_item_widget import SettingItem
from language_manager import lang


COLOR_PINK_LIGHT = "#F7CBCA"
COLOR_GRAY_LIGHT = "#D2E6E5"
COLOR_TEAL_DARK = "#516465"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED = "#9AABAB"
COLOR_DIVIDER = "#D2E6E5"

ROLE_ORGANIZER = "eo"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM = "umum"


def _is_eo_role(role):
    return (role or "").lower().strip() in ("eo", "organizer")

def _is_mahasiswa_role(role):
    return (role or "").lower().strip() in ("mahasiswa", "student")


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

        lang.language_changed.connect(self._retranslate)

    def _retranslate(self, _code: str = ""):
        if hasattr(self, "lbl_settings_title"):
            self.lbl_settings_title.setText(lang.t("settings.title"))
        if hasattr(self, "btn_home"):
            self.btn_home.setText(lang.t("settings.home_btn"))
        if hasattr(self, "sidebar_buttons") and hasattr(self, "_sidebar_menu_defs"):
            for btn, (key, _, __) in zip(self.sidebar_buttons, self._sidebar_menu_defs):
                btn.setText(f"  {lang.t(key)}")

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
        self.panel_language = LanguagePanel()

        self.stacked_widget.addWidget(self.panel_account)      # index 0
        self.stacked_widget.addWidget(self.panel_your_events)  # index 1
        self.stacked_widget.addWidget(self.panel_notif)        # index 2
        self.stacked_widget.addWidget(self.panel_language)     # index 3

        body_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addWidget(body, stretch=1)

        self.stacked_widget.setCurrentIndex(0)

    def buat_topbar(self):
        topbar = QWidget()
        topbar.setFixedHeight(72)
        topbar.setStyleSheet("background-color: white; border-bottom: 1px solid %s;" % COLOR_DIVIDER)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 0, 24, 0)

        icon_menu = QLabel("≡")
        icon_menu.setFixedSize(38, 38)
        icon_menu.setAlignment(Qt.AlignCenter)
        icon_menu.setStyleSheet(f"font-size: 30px; color: {COLOR_TEXT_PRIMARY}; font-weight: bold;")

        self.lbl_settings_title = QLabel(lang.t("settings.title"))
        self.lbl_settings_title.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.btn_home = QPushButton(lang.t("settings.home_btn"))
        self.btn_home.setIcon(QIcon("assets/home.png"))
        self.btn_home.setIconSize(QSize(20, 20))
        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_home.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLOR_TEXT_PRIMARY};
                font-size: 15px; border: none; padding: 8px 14px;
            }}
            QPushButton:hover {{ color: {COLOR_TEAL_DARK}; font-weight: bold; }}
        """)
        self.btn_home.clicked.connect(self.close)

        self.avatar_topbar = QLabel()
        self.avatar_topbar.setFixedSize(42, 42)
        self.avatar_topbar.setAlignment(Qt.AlignCenter)
        self.refresh_topbar_avatar()

        layout.addWidget(icon_menu)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_settings_title)
        layout.addSpacerItem(spacer)
        layout.addWidget(self.btn_home)
        layout.addSpacing(8)
        layout.addWidget(self.avatar_topbar)
        return topbar

    def refresh_topbar_avatar(self):
        """
        Refresh avatar kecil di pojok kanan atas halaman Settings.
        Jika user sudah upload foto, tampilkan foto tersebut sebagai lingkaran.
        Jika belum ada foto, fallback ke inisial user.
        """
        if not hasattr(self, "avatar_topbar"):
            return

        # Ambil data profil terbaru dari DB agar path foto selalu paling update.
        email = (self.user_data.get("email") or "").strip()
        if email:
            try:
                import db_manager
                profil = db_manager.get_user_profile(email)
                if profil:
                    self.user_data.update({
                        "nama": profil.get("nama", self.user_data.get("nama", "")),
                        "inisial": profil.get("inisial", self.user_data.get("inisial", "")),
                        "foto_profil_path": profil.get("foto_profil_path", self.user_data.get("foto_profil_path", "")),
                    })
            except Exception as err:
                print(f"[SettingsWindow] Gagal refresh profil topbar: {err}")

        foto_pixmap = self.user_data.get("foto_profil")
        if foto_pixmap and not foto_pixmap.isNull():
            self.avatar_topbar.setText("")
            self.avatar_topbar.setPixmap(self._pixmap_ke_lingkaran(foto_pixmap, 42))
            self.avatar_topbar.setStyleSheet("border-radius: 21px; background: transparent;")
            return

        foto_path = self.user_data.get("foto_profil_path", "")
        if foto_path and os.path.exists(foto_path):
            pixmap = QPixmap(foto_path)
            if not pixmap.isNull():
                self.avatar_topbar.setText("")
                self.avatar_topbar.setPixmap(self._pixmap_ke_lingkaran(pixmap, 42))
                self.avatar_topbar.setStyleSheet("border-radius: 21px; background: transparent;")
                return

        # Fallback kalau user belum upload foto profil.
        inisial = self._ambil_inisial_user()
        self.avatar_topbar.setPixmap(QPixmap())
        self.avatar_topbar.setText(inisial)
        self.avatar_topbar.setStyleSheet(f"""
            background-color: {COLOR_TEAL_DARK}; color: white;
            font-weight: bold; font-size: 15px; border-radius: 21px;
        """)

    def _ambil_inisial_user(self):
        """Ambil inisial dari user_data, nama, atau email."""
        inisial = (self.user_data.get("inisial") or "").strip()
        if inisial:
            return inisial[:2].upper()

        nama = (self.user_data.get("nama") or "").strip()
        if nama:
            return "".join(part[0].upper() for part in nama.split()[:2])

        email = (self.user_data.get("email") or "").strip()
        return email[:1].upper() if email else ""

    @staticmethod
    def _pixmap_ke_lingkaran(pixmap, size):
        """Crop QPixmap menjadi lingkaran ukuran `size` x `size`."""
        scaled = pixmap.scaled(
            size,
            size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )
        if scaled.width() != size or scaled.height() != size:
            x = (scaled.width() - size) // 2
            y = (scaled.height() - size) // 2
            scaled = scaled.copy(x, y, size, size)

        hasil = QPixmap(size, size)
        hasil.fill(Qt.transparent)

        painter = QPainter(hasil)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        return hasil

    def buat_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f"background-color: white; border-right: 1px solid {COLOR_DIVIDER};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(8)

        self._sidebar_menu_defs = [
            ("settings.account",       0, "profile"),
            ("settings.your_events",   1, "event"),
            ("settings.notifications", 2, "bell"),
            ("settings.language",      3, "language"),
        ]

        self.sidebar_buttons = []
        for key, index, icon_file in self._sidebar_menu_defs:
            btn = QPushButton(f"  {lang.t(key)}")
            btn.setIcon(QIcon(f"assets/{icon_file}.png"))
            btn.setIconSize(QSize(22, 22))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(58)
            btn.setStyleSheet(self._style_sidebar_btn(False))
            btn.clicked.connect(lambda checked, i=index: self.switch_panel(i))

            if key == "settings.your_events" and not (_is_eo_role(self.role) or _is_mahasiswa_role(self.role)):
                btn.hide()

            if key == "settings.notifications" and self.role == "admin":
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
                    font-size: 15px; text-align: left; border: none;
                    border-left: 4px solid {COLOR_TEAL_DARK}; padding-left: 24px;
                }}
            """
        return f"""
            QPushButton {{
                background-color: transparent; color: {COLOR_TEXT_PRIMARY};
                font-size: 15px; text-align: left; border: none; padding-left: 24px;
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
            panel = self.panel_your_events
            if not getattr(panel, "_rendered", False):
                panel._render()
                panel._rendered = True

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
                        min-width: 80px; padding: 6px 12px;
                        border: 1px solid #CBD5E0; border-radius: 6px;
                        background-color: #f8fafc; color: #1a1a1a;
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

            # FIX #1 — popup sukses pakai lang.t()
            _show_message(
                "info",
                lang.t("settings.request_sent_title"),
                lang.t("settings.request_sent_body"),
            )
        except Exception as exc:
            # FIX #2 — popup error database pakai lang.t()
            _show_message(
                "warn",
                lang.t("settings.db_error_title"),
                f"{lang.t('settings.db_error_body')}\n{exc}",
            )
            return

        self._tutup_edit_event(panel)
        if hasattr(self, "panel_your_events"):
            self.panel_your_events._render()

    def buat_panel_notif(self):
        """
        Legacy panel — sudah digantikan oleh NotificationsPanel.
        Tetap diterjemahkan agar tidak ada string hardcoded tersisa
        kalau suatu saat method ini masih dipanggil.
        """
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(16)

        lbl_judul = QLabel(lang.t("notif.title"))
        lbl_judul.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(lbl_judul)

        # FIX #3 — deskripsi per-role pakai lang.t()
        if _is_eo_role(self.role):
            deskripsi = lang.t("notif.desc_organizer")
        elif _is_mahasiswa_role(self.role):
            deskripsi = lang.t("notif.desc_mahasiswa")
        else:
            deskripsi = lang.t("notif.desc_umum")

        lbl_info = QLabel(deskripsi)
        lbl_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        # FIX #3 — judul & deskripsi SettingItem pakai lang.t()
        layout.addWidget(
            SettingItem(
                judul=lang.t("notif.item_registrant_title"),
                deskripsi=lang.t("notif.item_registrant_desc"),
                nama_setting="notif_registrant",
                default_on=True,
            )
        )
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
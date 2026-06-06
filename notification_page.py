# ==============================================================
# FILE: notification_page.py
# TUGAS: Halaman daftar notifikasi untuk EO dan Student/Umum
#
# Tipe notifikasi yang didukung:
#   EO_APPROVAL     → ✅ / ❌  (approve/reject dari admin)
#   H1_REMINDER     → 🔔        (reminder H-1 event)
#   EVENT_UPDATED   → 📢        (perubahan detail event yang di-book)
#   NEW_LIKED_MATCH → ✨        (event baru cocok kategori liked)
#   CAMPUS_NEW_EVENT→ 🏫        (event Internal baru dari kampus)
#
# SINYAL YANG DIPANCARKAN:
#   kembali_diklik          → navigasi kembali ke homepage
#   badge_berubah(int)      → update angka di badge lonceng navbar
#   buka_your_events()      → navigasi ke Settings > Your Events
#                             (untuk notif EVENT_UPDATED)
#   buka_detail_event(str)  → emit event_id, temanmu connect ke pop up
#                             (untuk notif NEW_LIKED_MATCH, CAMPUS_NEW_EVENT,
#                              H1_REMINDER)
#
# CARA PAKAI dari main_window.py:
#   from notification_page import NotificationPage
#   self.notif_page = NotificationPage(
#       email_user="student@email.com",
#       user_role="mahasiswa"
#   )
#   self.notif_page.kembali_diklik.connect(self.show_home_page)
#   self.notif_page.badge_berubah.connect(self._set_badge)
#   self.notif_page.buka_your_events.connect(self.buka_my_events)
#   self.notif_page.buka_detail_event.connect(self._on_buka_detail_event)
# ==============================================================

import sys
import os
from language_manager import lang
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import db_manager

# ==============================================================
# KONSTANTA WARNA
# ==============================================================
COLOR_TEAL_DARK    = "#516465"
COLOR_TEAL_MID     = "#2D6A6A"
COLOR_GRAY_LIGHT   = "#D2E6E5"
COLOR_PINK_LIGHT   = "#F7CBCA"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED   = "#828282"
COLOR_UNREAD_BG    = "#EAF3F3"
COLOR_READ_BG      = "#FFFFFF"
COLOR_DIVIDER      = "#E0EDED"

# ==============================================================
# MAPPING tipe_notif → icon emoji
# ==============================================================
_TIPE_ICON = {
    "EO_APPROVAL"     : None,   # ditentukan dari isi judul (✅/❌)
    "H1_REMINDER"     : "🔔",
    "EVENT_UPDATED"   : "📢",
    "NEW_LIKED_MATCH" : "✨",
    "CAMPUS_NEW_EVENT": "🏫",
}

# Tipe yang actionable (klik → arahkan ke halaman lain)
_TIPE_ACTIONABLE = {"EVENT_UPDATED", "H1_REMINDER", "NEW_LIKED_MATCH", "CAMPUS_NEW_EVENT"}


# ==============================================================
# HELPER: waktu relatif
# ==============================================================
def _waktu_relatif(created_at_str: str) -> str:
    try:
        waktu = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return created_at_str or ""
    sekarang = datetime.now()
    delta = sekarang - waktu
    if delta < timedelta(minutes=1):
        return "Just now"
    elif delta < timedelta(hours=1):
        menit = int(delta.total_seconds() // 60)
        return f"{menit} minute{'s' if menit > 1 else ''} ago"
    elif delta < timedelta(days=1):
        jam = int(delta.total_seconds() // 3600)
        return f"{jam} hour{'s' if jam > 1 else ''} ago"
    elif delta < timedelta(days=2):
        return "Yesterday"
    elif delta < timedelta(days=7):
        return f"{delta.days} days ago"
    else:
        return waktu.strftime("%d %b %Y")


# ==============================================================
# CLASS NotifItemWidget
# ==============================================================
class NotifItemWidget(QWidget):
    """
    Satu baris item notifikasi.
    Sinyal diklik(notif_id, tipe_notif, event_id_ref).
    """
    diklik = pyqtSignal(int, str, str)

    def __init__(self, notif_data: dict, font_regular: str, font_semi: str,
                 parent=None):
        super().__init__(parent)
        self.notif_data   = notif_data
        self.notif_id     = notif_data.get("id", -1)
        self.is_read      = bool(notif_data.get("is_read", 0))
        self.tipe_notif   = notif_data.get("tipe_notif", "EO_APPROVAL")
        self.event_id_ref = notif_data.get("event_id_ref", "") or ""
        self.font_regular = font_regular
        self.font_semi    = font_semi
        self._build_ui()
        self.setCursor(Qt.PointingHandCursor)

    # ----------------------------------------------------------
    def _icon_for_notif(self) -> str:
        """Pilih emoji icon berdasarkan tipe notif."""
        tipe = self.tipe_notif
        if tipe == "EO_APPROVAL":
            judul = self.notif_data.get("judul", "")
            if any(k in judul.lower() for k in ("reject", "ditolak", "❌")):
                return "❌"
            return "✅"
        return _TIPE_ICON.get(tipe, "🔔")

    # ----------------------------------------------------------
    def _build_ui(self):
        self._apply_bg()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # ---- ICON ----
        icon_text = self._icon_for_notif()
        lbl_icon = QLabel(icon_text)
        lbl_icon.setFont(QFont(self.font_regular, 20))
        lbl_icon.setFixedWidth(36)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("background: transparent;")
        layout.addWidget(lbl_icon)

        # ---- TENGAH: judul + pesan ----
        tengah = QWidget()
        tengah.setStyleSheet("background: transparent;")
        tengah_layout = QVBoxLayout(tengah)
        tengah_layout.setContentsMargins(0, 0, 0, 0)
        tengah_layout.setSpacing(4)

        judul = self.notif_data.get("judul", "")
        lbl_judul = QLabel(judul)
        lbl_judul.setFont(QFont(self.font_semi, 13))
        weight = "bold" if not self.is_read else "normal"
        lbl_judul.setStyleSheet(
            f"color: {COLOR_TEAL_DARK}; font-weight: {weight}; background: transparent;"
        )
        tengah_layout.addWidget(lbl_judul)

        pesan = self.notif_data.get("pesan", "")
        lbl_pesan = QLabel(pesan)
        lbl_pesan.setFont(QFont(self.font_regular, 11))
        lbl_pesan.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        lbl_pesan.setWordWrap(True)
        tengah_layout.addWidget(lbl_pesan)

        # Label "Tap to view" untuk notif actionable yang belum dibaca
        if self.tipe_notif in _TIPE_ACTIONABLE and not self.is_read:
            lbl_tap = QLabel(lang.t("notif.tap_to_view"))
            lbl_tap.setFont(QFont(self.font_regular, 10))
            lbl_tap.setStyleSheet(
                f"color: {COLOR_TEAL_MID}; background: transparent; font-style: italic;"
            )
            tengah_layout.addWidget(lbl_tap)

        layout.addWidget(tengah, stretch=1)

        # ---- KANAN: waktu + dot unread ----
        kanan = QWidget()
        kanan.setStyleSheet("background: transparent;")
        kanan_layout = QVBoxLayout(kanan)
        kanan_layout.setContentsMargins(0, 0, 0, 0)
        kanan_layout.setSpacing(6)
        kanan_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)

        waktu_str = _waktu_relatif(self.notif_data.get("created_at", ""))
        lbl_waktu = QLabel(waktu_str)
        lbl_waktu.setFont(QFont(self.font_regular, 10))
        lbl_waktu.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        lbl_waktu.setAlignment(Qt.AlignRight)
        kanan_layout.addWidget(lbl_waktu)

        if not self.is_read:
            dot = QLabel("●")
            dot.setFont(QFont(self.font_regular, 10))
            dot.setStyleSheet("color: #E57373; background: transparent;")
            dot.setAlignment(Qt.AlignRight)
            kanan_layout.addWidget(dot)

        layout.addWidget(kanan)

    # ----------------------------------------------------------
    def _apply_bg(self):
        bg = COLOR_READ_BG if self.is_read else COLOR_UNREAD_BG
        self.setStyleSheet(f"""
            NotifItemWidget {{
                background-color: {bg};
                border-radius: 12px;
            }}
            NotifItemWidget:hover {{
                background-color: {COLOR_GRAY_LIGHT};
            }}
        """)

    # ----------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.diklik.emit(self.notif_id, self.tipe_notif, self.event_id_ref)
        super().mousePressEvent(event)

    # ----------------------------------------------------------
    def tandai_sudah_dibaca(self):
        self.is_read = True
        self._apply_bg()
        for child in self.findChildren(QWidget):
            child.deleteLater()
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self.notif_data["is_read"] = 1
        self._build_ui()


# ==============================================================
# CLASS NotificationPage
# ==============================================================
class NotificationPage(QWidget):
    """
    Halaman notifikasi untuk EO dan Student.

    Sinyal:
        kembali_diklik              → kembali ke homepage
        badge_berubah(int)          → update badge lonceng navbar
        buka_your_events()          → buka Settings > Your Events
                                      (notif EVENT_UPDATED)
        buka_detail_event(str)      → emit event_id ke pop up deskripsi
                                      (notif H1_REMINDER, NEW_LIKED_MATCH,
                                       CAMPUS_NEW_EVENT)
    """
    kembali_diklik   = pyqtSignal()
    badge_berubah    = pyqtSignal(int)
    buka_your_events = pyqtSignal()
    buka_detail_event = pyqtSignal(str)   # membawa event_id

    def __init__(self, email_user: str = "", user_role: str = "guest",
                 parent=None):
        super().__init__(parent)
        # Support panggilan lama dengan keyword email_eo= (backward compat)
        self.email_user = email_user
        self.user_role  = user_role
        self._load_fonts()
        self.setStyleSheet("background: transparent;")
        self._build_ui()
        self.muat_notifikasi()

    # ----------------------------------------------------------
    # Properti alias untuk kompatibilitas panggilan lama (email_eo=)
    @property
    def email_eo(self):
        return self.email_user

    @email_eo.setter
    def email_eo(self, v):
        self.email_user = v

    # ----------------------------------------------------------
    def _load_fonts(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        assets = os.path.join(BASE_DIR, "assets")
        id_reg  = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_18pt-Regular.ttf"))
        id_bold = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_18pt-Bold.ttf"))
        fam_reg  = QFontDatabase.applicationFontFamilies(id_reg)
        fam_bold = QFontDatabase.applicationFontFamilies(id_bold)
        if not fam_reg:
            id_fb = QFontDatabase.addApplicationFont(
                os.path.join(assets, "GoogleSans_17pt-Regular.ttf"))
            fam_reg = QFontDatabase.applicationFontFamilies(id_fb)
        if not fam_bold:
            id_fbb = QFontDatabase.addApplicationFont(
                os.path.join(assets, "GoogleSans_17pt-Bold.ttf"))
            fam_bold = QFontDatabase.applicationFontFamilies(id_fbb)
        self.font_regular = fam_reg[0]  if fam_reg  else "Inter"
        self.font_semi    = fam_bold[0] if fam_bold else "Inter"

    # ----------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._buat_topbar())

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                border: none; background: rgba(255,255,255,60);
                width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #5D6B6B; border-radius: 4px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none; background: none;
            }
        """)
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(60, 24, 60, 40)
        self.list_layout.setSpacing(10)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        root.addWidget(self.scroll, stretch=1)

    # ----------------------------------------------------------
    def _buat_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(70)
        bar.setStyleSheet(f"background-color: {COLOR_GRAY_LIGHT};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(12)

        btn_kembali = QPushButton()
        btn_kembali.setIcon(QIcon("assets/back.png"))
        btn_kembali.setIconSize(QSize(22, 22))
        btn_kembali.setCursor(Qt.PointingHandCursor)
        btn_kembali.setFixedSize(40, 40)
        btn_kembali.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover {
                background: rgba(255,255,255,120); border-radius: 20px;
            }
        """)
        btn_kembali.clicked.connect(self.kembali_diklik.emit)
        layout.addWidget(btn_kembali)

        lbl_judul = QLabel(lang.t("notif.title"))
        lbl_judul.setFont(QFont(self.font_semi, 18))
        lbl_judul.setStyleSheet(
            f"color: {COLOR_TEAL_DARK}; font-weight: bold; background: transparent;"
        )
        layout.addWidget(lbl_judul)
        layout.addStretch()

        self.btn_baca_semua = QPushButton(lang.t("notif.mark_all_read"))
        self.btn_baca_semua.setCursor(Qt.PointingHandCursor)
        self.btn_baca_semua.setFont(QFont(self.font_regular, 11))
        self.btn_baca_semua.setStyleSheet(f"""
            QPushButton {{
                color: {COLOR_TEAL_MID}; background: transparent;
                border: none; font-weight: bold;
            }}
            QPushButton:hover {{
                color: {COLOR_TEAL_DARK}; text-decoration: underline;
            }}
        """)
        self.btn_baca_semua.clicked.connect(self._tandai_semua_dibaca)
        layout.addWidget(self.btn_baca_semua)
        return bar

    # ----------------------------------------------------------
    def muat_notifikasi(self):
        """Ambil notifikasi dari DB dan tampilkan ke list."""
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.email_user:
            self._tampilkan_kosong("Please log in to view your notifications.")
            return

        notif_list = db_manager.get_notifikasi(self.email_user)

        if not notif_list:
            self._tampilkan_kosong("You're all caught up! No notifications yet.")
            return

        self._item_widgets = []

        for notif in notif_list:
            item_widget = NotifItemWidget(
                notif_data=notif,
                font_regular=self.font_regular,
                font_semi=self.font_semi,
            )
            item_widget.diklik.connect(self._on_item_diklik)
            self._item_widgets.append(item_widget)
            self.list_layout.addWidget(item_widget)

            divider = QFrame()
            divider.setFrameShape(QFrame.HLine)
            divider.setFixedHeight(1)
            divider.setStyleSheet(
                f"background-color: {COLOR_DIVIDER}; border: none;"
            )
            self.list_layout.addWidget(divider)

        self.list_layout.addStretch()

        jumlah_unread = sum(1 for n in notif_list if not n.get("is_read", 0))
        self.badge_berubah.emit(jumlah_unread)

    # ----------------------------------------------------------
    def _tampilkan_kosong(self, pesan: str):
        lbl = QLabel(pesan)
        lbl.setFont(QFont(self.font_regular, 14))
        lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        self.list_layout.addStretch()
        self.list_layout.addWidget(lbl)
        self.list_layout.addStretch()

    # ----------------------------------------------------------
    def _on_item_diklik(self, notif_id: int, tipe_notif: str, event_id_ref: str):
        """
        Saat item diklik:
        1. Tandai dibaca di DB
        2. Update tampilan item
        3. Emit sinyal navigasi sesuai tipe
        4. Update badge
        """
        db_manager.tandai_notifikasi_dibaca(notif_id)

        for w in getattr(self, "_item_widgets", []):
            if w.notif_id == notif_id and not w.is_read:
                w.tandai_sudah_dibaca()
                break

        # Navigasi berdasarkan tipe notifikasi
        if tipe_notif == "EVENT_UPDATED":
            # Arahkan ke Settings > Your Events
            self.buka_your_events.emit()
        elif tipe_notif in ("H1_REMINDER", "NEW_LIKED_MATCH", "CAMPUS_NEW_EVENT"):
            # Emit event_id — temanmu connect ke pop up deskripsi event
            if event_id_ref:
                self.buka_detail_event.emit(event_id_ref)

        jumlah = db_manager.hitung_notifikasi_belum_dibaca(self.email_user)
        self.badge_berubah.emit(jumlah)

    # ----------------------------------------------------------
    def _tandai_semua_dibaca(self):
        if not self.email_user:
            return
        db_manager.tandai_semua_notifikasi_dibaca(self.email_user)
        for w in getattr(self, "_item_widgets", []):
            if not w.is_read:
                w.tandai_sudah_dibaca()
        self.badge_berubah.emit(0)

    # ----------------------------------------------------------
    def set_email(self, email: str, role: str = ""):
        """
        Update email + role user aktif dan muat ulang notifikasi.
        Dipanggil dari main_window.py saat login / logout.

        Backward-compatible: boleh dipanggil dengan satu argumen saja
        (main_window.py lama yang hanya kirim email).
        """
        self.email_user = email
        if role:
            self.user_role = role
        self.muat_notifikasi()


# ==============================================================
# BLOK TESTING MANDIRI
# ==============================================================
if __name__ == "__main__":
    import db_manager as _db
    _db.init_db()

    # Seed notif EO
    _db.simpan_notifikasi(
        "eo@test.com", "Event Approved ✅",
        '"Workshop UI/UX" has been approved by the admin and is now live!',
        tipe_notif="EO_APPROVAL"
    )
    # Seed notif Student
    _db.simpan_notifikasi(
        "student@test.com", "🔔 Reminder: Workshop UI/UX is tomorrow!",
        "Don't forget — \"Workshop UI/UX\" is happening tomorrow at 13:00.",
        tipe_notif="H1_REMINDER", event_id_ref="EVT-006"
    )
    _db.simpan_notifikasi(
        "student@test.com", "📢 Event Update: Sparta Festival",
        '"Sparta Festival" has been updated by the organizer. Check the latest details.',
        tipe_notif="EVENT_UPDATED", event_id_ref="EVT-001"
    )
    _db.simpan_notifikasi(
        "student@test.com", "✨ New event you might like!",
        '"Seminar Nasional AI" is a new Seminar event that matches your interests.',
        tipe_notif="NEW_LIKED_MATCH", event_id_ref="EVT-NEW"
    )
    _db.simpan_notifikasi(
        "student@test.com", "🏫 New campus event: Kelas Karir 4.0",
        '"Kelas Karir 4.0" from your campus is now live on Campus Connect!',
        tipe_notif="CAMPUS_NEW_EVENT", event_id_ref="EVT-003"
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = QMainWindow()
    window.setWindowTitle("Notification Page — Student Preview")
    window.resize(900, 650)
    window.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #B5CECE, stop:0.4 #C8DCDC,
                stop:0.75 #D6E6E6, stop:1 #F7CBCA
            );
        }
    """)
    page = NotificationPage(email_user="student@test.com", user_role="mahasiswa")
    page.kembali_diklik.connect(window.close)
    page.badge_berubah.connect(lambda n: print(f"[BADGE] Unread: {n}"))
    page.buka_your_events.connect(lambda: print("[ACTION] Buka Your Events"))
    page.buka_detail_event.connect(lambda eid: print(f"[ACTION] Buka detail event: {eid}"))
    window.setCentralWidget(page)
    window.show()
    sys.exit(app.exec_())
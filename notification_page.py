# ==============================================================
# FILE: notification_page.py
# TUGAS: Halaman daftar notifikasi untuk EO
#        Menampilkan semua notif approve/reject dari admin,
#        dengan badge unread count, dan tandai-baca saat diklik.
#
# CARA PAKAI dari main_window.py:
#   from notification_page import NotificationPage
#   self.notif_page = NotificationPage(email_eo="eo@email.com")
#   self.notif_page.kembali_diklik.connect(self.show_home_page)
#   self.notif_page.badge_berubah.connect(self.update_bell_badge)
# ==============================================================

import sys
import os
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
COLOR_UNREAD_BG    = "#EAF3F3"   # background item belum dibaca
COLOR_READ_BG      = "#FFFFFF"   # background item sudah dibaca
COLOR_DIVIDER      = "#E0EDED"


# ==============================================================
# HELPER: waktu relatif ("2 hours ago", "Yesterday", dsb.)
# ==============================================================
def _waktu_relatif(created_at_str: str) -> str:
    """Mengubah string datetime ISO menjadi teks relatif yang ramah."""
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
        hari = delta.days
        return f"{hari} days ago"
    else:
        return waktu.strftime("%d %b %Y")


# ==============================================================
# CLASS NotifItemWidget
# Satu baris item notifikasi di dalam daftar
# ==============================================================
class NotifItemWidget(QWidget):
    """Widget satu baris notifikasi. Emit sinyal diklik(notif_id)."""

    diklik = pyqtSignal(int)   # membawa notif_id

    def __init__(self, notif_data: dict, font_regular: str, font_semi: str, parent=None):
        super().__init__(parent)
        self.notif_data = notif_data
        self.notif_id   = notif_data.get("id", -1)
        self.is_read    = bool(notif_data.get("is_read", 0))
        self.font_regular = font_regular
        self.font_semi    = font_semi

        self._build_ui()
        self.setCursor(Qt.PointingHandCursor)

    # ----------------------------------------------------------
    def _build_ui(self):
        self._apply_bg()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # ---- ICON ✅ / ❌ ----
        judul = self.notif_data.get("judul", "")
        if "ditolak" in judul.lower() or "rejected" in judul.lower() or "❌" in judul:
            icon_text = "❌"
            icon_color = "#E57373"
        else:
            icon_text = "✅"
            icon_color = "#4CAF50"

        lbl_icon = QLabel(icon_text)
        lbl_icon.setFont(QFont(self.font_regular, 22))
        lbl_icon.setFixedWidth(36)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("background: transparent;")
        layout.addWidget(lbl_icon)

        # ---- KOLOM TENGAH: judul + pesan ----
        tengah = QWidget()
        tengah.setStyleSheet("background: transparent;")
        tengah_layout = QVBoxLayout(tengah)
        tengah_layout.setContentsMargins(0, 0, 0, 0)
        tengah_layout.setSpacing(4)

        lbl_judul = QLabel(judul)
        lbl_judul.setFont(QFont(self.font_semi, 13))
        weight = "bold" if not self.is_read else "normal"
        lbl_judul.setStyleSheet(f"color: {COLOR_TEAL_DARK}; font-weight: {weight}; background: transparent;")
        tengah_layout.addWidget(lbl_judul)

        pesan = self.notif_data.get("pesan", "")
        lbl_pesan = QLabel(pesan)
        lbl_pesan.setFont(QFont(self.font_regular, 11))
        lbl_pesan.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        lbl_pesan.setWordWrap(True)
        tengah_layout.addWidget(lbl_pesan)

        layout.addWidget(tengah, stretch=1)

        # ---- KOLOM KANAN: waktu + dot unread ----
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

        # Dot merah kecil kalau belum dibaca
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
            self.diklik.emit(self.notif_id)
        super().mousePressEvent(event)

    # ----------------------------------------------------------
    def tandai_sudah_dibaca(self):
        """Update tampilan item menjadi 'sudah dibaca' tanpa rebuild."""
        self.is_read = True
        self._apply_bg()
        # Re-build isi (cara paling bersih agar dot & bold hilang)
        # Hapus semua child widget lama lalu bangun ulang
        for child in self.findChildren(QWidget):
            child.deleteLater()
        # Hapus layout lama
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self.notif_data["is_read"] = 1
        self._build_ui()


# ==============================================================
# CLASS NotificationPage
# Halaman penuh yang berisi daftar notifikasi EO
# ==============================================================
class NotificationPage(QWidget):
    """
    Halaman notifikasi yang bisa ditambahkan ke layout utama
    (sama polanya dengan AdminPage, DetailEventPage, dsb).

    Sinyal:
        kembali_diklik  → navigasi kembali ke homepage
        badge_berubah   → int, jumlah notif belum dibaca terbaru
                          (untuk update badge lonceng di navbar)
    """

    kembali_diklik = pyqtSignal()
    badge_berubah  = pyqtSignal(int)

    def __init__(self, email_eo: str = "", parent=None):
        super().__init__(parent)
        self.email_eo = email_eo
        self._load_fonts()
        self.setStyleSheet("background: transparent;")
        self._build_ui()
        self.muat_notifikasi()

    # ----------------------------------------------------------
    def _load_fonts(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        assets = os.path.join(BASE_DIR, "assets")

        id_reg = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_18pt-Regular.ttf")
        )
        id_bold = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_18pt-Bold.ttf")
        )

        fam_reg  = QFontDatabase.applicationFontFamilies(id_reg)
        fam_bold = QFontDatabase.applicationFontFamilies(id_bold)

        if not fam_reg:
            id_fb = QFontDatabase.addApplicationFont(
                os.path.join(assets, "GoogleSans_17pt-Regular.ttf")
            )
            fam_reg = QFontDatabase.applicationFontFamilies(id_fb)

        if not fam_bold:
            id_fbb = QFontDatabase.addApplicationFont(
                os.path.join(assets, "GoogleSans_17pt-Bold.ttf")
            )
            fam_bold = QFontDatabase.applicationFontFamilies(id_fbb)

        self.font_regular = fam_reg[0]  if fam_reg  else "Inter"
        self.font_semi    = fam_bold[0] if fam_bold else "Inter"

    # ----------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- TOPBAR ----
        topbar = self._buat_topbar()
        root.addWidget(topbar)

        # ---- AREA SCROLL ----
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

        # Tombol kembali
        btn_kembali = QPushButton()
        btn_kembali.setIcon(QIcon("assets/back.png"))
        btn_kembali.setIconSize(QSize(22, 22))
        btn_kembali.setCursor(Qt.PointingHandCursor)
        btn_kembali.setFixedSize(40, 40)
        btn_kembali.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
            }
            QPushButton:hover {
                background: rgba(255,255,255,120); border-radius: 20px;
            }
        """)
        btn_kembali.clicked.connect(self.kembali_diklik.emit)
        layout.addWidget(btn_kembali)

        # Judul halaman
        lbl_judul = QLabel("Notifications")
        lbl_judul.setFont(QFont(self.font_semi, 18))
        lbl_judul.setStyleSheet(f"color: {COLOR_TEAL_DARK}; font-weight: bold; background: transparent;")
        layout.addWidget(lbl_judul)

        layout.addStretch()

        # Tombol "Mark all as read"
        self.btn_baca_semua = QPushButton("Mark all as read")
        self.btn_baca_semua.setCursor(Qt.PointingHandCursor)
        self.btn_baca_semua.setFont(QFont(self.font_regular, 11))
        self.btn_baca_semua.setStyleSheet(f"""
            QPushButton {{
                color: {COLOR_TEAL_MID};
                background: transparent;
                border: none;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {COLOR_TEAL_DARK};
                text-decoration: underline;
            }}
        """)
        self.btn_baca_semua.clicked.connect(self._tandai_semua_dibaca)
        layout.addWidget(self.btn_baca_semua)

        return bar

    # ----------------------------------------------------------
    def muat_notifikasi(self):
        """Ambil notifikasi dari DB dan tampilkan ke list."""
        # Bersihkan list lama
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.email_eo:
            self._tampilkan_kosong("Login sebagai Event Organizer untuk melihat notifikasi.")
            return

        notif_list = db_manager.get_notifikasi(self.email_eo)

        if not notif_list:
            self._tampilkan_kosong("Belum ada notifikasi.")
            return

        self._item_widgets = []   # simpan referensi untuk update badge

        for notif in notif_list:
            item_widget = NotifItemWidget(
                notif_data=notif,
                font_regular=self.font_regular,
                font_semi=self.font_semi,
            )
            item_widget.diklik.connect(self._on_item_diklik)
            self._item_widgets.append(item_widget)
            self.list_layout.addWidget(item_widget)

            # Garis pembatas
            divider = QFrame()
            divider.setFrameShape(QFrame.HLine)
            divider.setFixedHeight(1)
            divider.setStyleSheet(f"background-color: {COLOR_DIVIDER}; border: none;")
            self.list_layout.addWidget(divider)

        self.list_layout.addStretch()

        # Emit badge count
        jumlah_unread = sum(1 for n in notif_list if not n.get("is_read", 0))
        self.badge_berubah.emit(jumlah_unread)

    # ----------------------------------------------------------
    def _tampilkan_kosong(self, pesan: str):
        """Tampilkan pesan kosong di tengah area list."""
        lbl = QLabel(pesan)
        lbl.setFont(QFont(self.font_regular, 14))
        lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        self.list_layout.addStretch()
        self.list_layout.addWidget(lbl)
        self.list_layout.addStretch()

    # ----------------------------------------------------------
    def _on_item_diklik(self, notif_id: int):
        """Saat item diklik: tandai dibaca di DB, update UI, emit badge baru."""
        db_manager.tandai_notifikasi_dibaca(notif_id)

        # Update tampilan item yang bersangkutan
        for w in getattr(self, "_item_widgets", []):
            if w.notif_id == notif_id and not w.is_read:
                w.tandai_sudah_dibaca()
                break

        # Hitung ulang badge
        jumlah = db_manager.hitung_notifikasi_belum_dibaca(self.email_eo)
        self.badge_berubah.emit(jumlah)

    # ----------------------------------------------------------
    def _tandai_semua_dibaca(self):
        """Tandai semua notifikasi sebagai dibaca."""
        if not self.email_eo:
            return
        db_manager.tandai_semua_notifikasi_dibaca(self.email_eo)

        for w in getattr(self, "_item_widgets", []):
            if not w.is_read:
                w.tandai_sudah_dibaca()

        self.badge_berubah.emit(0)

    # ----------------------------------------------------------
    def set_email(self, email: str):
        """
        Update email EO yang aktif dan muat ulang notifikasi.
        Dipanggil dari main_window.py saat login / logout.
        """
        self.email_eo = email
        self.muat_notifikasi()


# ==============================================================
# BLOK TESTING MANDIRI
# ==============================================================
if __name__ == "__main__":
    import db_manager as _db
    _db.init_db()

    # Seed data dummy
    _db.simpan_notifikasi(
        "eo@test.com",
        "Event Disetujui ✅",
        "Workshop UI/UX telah disetujui admin dan kini live di Campus Connect!"
    )
    _db.simpan_notifikasi(
        "eo@test.com",
        "Event Ditolak ❌",
        "Seminar AI tidak disetujui admin. Silakan periksa detail event atau hubungi admin."
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QMainWindow()
    window.setWindowTitle("Notification Page — Preview")
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

    page = NotificationPage(email_eo="eo@test.com")
    page.kembali_diklik.connect(window.close)
    page.badge_berubah.connect(lambda n: print(f"[BADGE] Unread: {n}"))

    window.setCentralWidget(page)
    window.show()
    sys.exit(app.exec_())
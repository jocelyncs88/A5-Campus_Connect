# ==============================================================
# FILE: settings/notifications_window.py
# TUGAS: Membangun panel "Notification Settings" di halaman Settings
#        dengan 2 skenario tampilan berbeda berdasarkan role user:
#
#   ROLE_ORGANIZER → Registration & Tickets (New registrant,
#                    Quota alerts, Registration cancellations)
#   ROLE_MAHASISWA / ROLE_UMUM → My Schedule (Event reminder,
#                    Critical updates) + Discovery (Interest match,
#                    Campus Spotlight)
#
# DIBUAT OLEH: UI/UX Designer (fitur-Settings)
#
# CARA PAKAI dari setting_window.py:
#   from settings.notifications_window import NotificationsPanel
#   self.panel_notif = NotificationsPanel(
#       user_data=self.user_data,
#       stacked_widget=self.stacked_widget
#   )
#
# DEFAULT MESSAGES:
#   Quota alerts (90%):
#     "Hooray! {nama_event} has already reached 90% capacity!
#      Only a few spots left — keep the momentum going!"
#   Quota alerts (sold out):
#     "{nama_event} is now SOLD OUT! Congratulations on a
#      fully booked event!"
#   Registration cancellations:
#     "{nama_audience} has cancelled their booking for
#      {nama_event}. You may want to follow up with them."
# ==============================================================

import sys
import os

# Tambahkan root ke sys.path agar bisa import toggle_widget
# yang berada di root project, bukan di dalam folder settings/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from toggle_widget import ToggleSwitch


# ==============================================================
# KONSTANTA WARNA
# Sesuai dengan spesifikasi dari mockup dan konsisten dengan
# file settings lainnya
# ==============================================================
COLOR_TEAL_DARK      = "#516465"   # Judul utama & sub-judul kategori
COLOR_TEXT_MUTED     = "#828282"   # Keterangan judul & deskripsi item
COLOR_DIVIDER        = "#888780"   # Garis pembatas antar item
COLOR_WHITE          = "#FFFFFF"   # Background sidebar


# ==============================================================
# KONSTANTA ROLE USER
# ==============================================================
ROLE_ORGANIZER = "eo"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"


# ==============================================================
# CLASS NotificationsPanel
# Mewarisi QWidget — dimasukkan ke stacked_widget settings_window
#
# Menampilkan panel berbeda berdasarkan role:
#   EO      → Registration & Tickets notifications
#   Student/Umum → My Schedule + Discovery notifications
# ==============================================================
class NotificationsPanel(QWidget):

    # ----------------------------------------------------------
    # FUNGSI __init__
    #
    # Parameter:
    #   user_data      = dictionary data user yang login
    #   stacked_widget = QStackedWidget milik settings_window
    #   parent         = komponen induk
    # ----------------------------------------------------------
    def __init__(self, user_data=None, stacked_widget=None, parent=None):
        super().__init__(parent)

        self.user_data = user_data or {
            "nama"   : "",
            "role"   : ROLE_UMUM,
            "inisial": ""
        }
        self.role = self.user_data.get("role", ROLE_UMUM)
        self.stacked_widget = stacked_widget

        # Menyimpan status setiap toggle notification
        # Key: nama_setting, Value: bool (True=ON, False=OFF)
        self.notif_states = {}

        # Memuat font Inter dari assets
        self._load_fonts()

        self.setStyleSheet("background: transparent;")
        self._render()


    # ----------------------------------------------------------
    # FUNGSI _load_fonts()
    # Memuat font Inter dari folder assets
    # Sesuai spesifikasi mockup yang menggunakan font Inter
    # ----------------------------------------------------------
    def _load_fonts(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets = os.path.join(BASE_DIR, "assets")

        # Coba load Inter, fallback ke GoogleSans jika tidak ada
        id_inter = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_28pt-Regular.ttf")
        )
        id_inter_semi = QFontDatabase.addApplicationFont(
            os.path.join(assets, "Inter_28pt-SemiBold.ttf")
        )

        families_regular = QFontDatabase.applicationFontFamilies(id_inter)
        families_semi    = QFontDatabase.applicationFontFamilies(id_inter_semi)

        # Fallback ke GoogleSans jika Inter tidak tersedia
        if not families_regular:
            id_fallback = QFontDatabase.addApplicationFont(
                os.path.join(assets, "GoogleSans_17pt-Regular.ttf")
            )
            families_regular = QFontDatabase.applicationFontFamilies(id_fallback)

        if not families_semi:
            id_fallback_bold = QFontDatabase.addApplicationFont(
                os.path.join(assets, "GoogleSans_17pt-Bold.ttf")
            )
            families_semi = QFontDatabase.applicationFontFamilies(id_fallback_bold)

        self.font_regular = families_regular[0] if families_regular else "sans-serif"
        self.font_semi    = families_semi[0]    if families_semi    else "sans-serif"


    # ----------------------------------------------------------
    # FUNGSI _render()
    # Membangun ulang tampilan panel berdasarkan role
    # ----------------------------------------------------------
    def _render(self):

        # Bersihkan layout lama jika ada
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.layout())

        # Bungkus seluruh konten dalam QScrollArea
        # agar bisa di-scroll jika konten melebihi tinggi layar
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        konten = QWidget()
        konten.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(konten)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(0)

        # ---- JUDUL UTAMA ----
        # Ukuran 55, warna #516465, font Inter
        lbl_judul = QLabel("Notification Settings")
        lbl_judul.setFont(QFont(self.font_semi, 30))
        lbl_judul.setStyleSheet(f"color: {COLOR_TEAL_DARK};")
        layout.addWidget(lbl_judul)
        layout.addSpacing(8)

        # ---- KETERANGAN JUDUL ----
        # Ukuran 23, warna #828282, font Inter
        lbl_ket = QLabel(
            "We may still send you important notifications about your "
            "account outside of your notification settings."
        )
        lbl_ket.setFont(QFont(self.font_regular, 13))
        lbl_ket.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_ket.setWordWrap(True)
        layout.addWidget(lbl_ket)
        layout.addSpacing(32)

        # ---- RENDER KONTEN SESUAI ROLE ----
        if self.role == ROLE_ORGANIZER:
            self._render_eo(layout)
        else:
            self._render_student(layout)

        layout.addStretch()
        scroll.setWidget(konten)
        outer_layout.addWidget(scroll)


    # ==========================================================
    # ---- TAMPILAN EVENT ORGANIZER ----
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _render_eo()
    # Membangun tampilan notifikasi untuk Event Organizer:
    #   Kategori "Registration & Tickets":
    #   - New registrant
    #   - Quota alerts
    #   - Registration cancellations
    # ----------------------------------------------------------
    def _render_eo(self, layout):

        # ---- KATEGORI: Registration & Tickets ----
        self._buat_label_kategori("Registration & Tickets", layout)
        layout.addSpacing(12)

        # Item 1: New registrant
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_new_registrant",
            judul="New registrant",
            deskripsi=(
                "Get alerts every time a user registers "
                "or purchases a ticket."
            ),
            default_on=True,
            pesan_default=(
                "🎉 New registration! {nama_audience} has just registered "
                "for {nama_event}. Your event is gaining traction!"
            )
        )

        # Item 2: Quota alerts
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_quota_alerts",
            judul="Quota alerts",
            deskripsi=(
                "Automatic warnings when your event capacity reaches 90% "
                "and when sold out."
            ),
            default_on=True,
            pesan_default=(
                "90%: \"Hooray! {nama_event} has already reached 90% capacity! "
                "Only a few spots left — keep the momentum going!\"\n"
                "Sold out: \"{nama_event} is now SOLD OUT! "
                "Congratulations on a fully booked event!\""
            )
        )

        # Item 3: Registration cancellations
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_cancellations",
            judul="Registration cancellations",
            deskripsi=(
                "Notification if a participant cancels their booking."
            ),
            default_on=True,
            pesan_default=(
                "{nama_audience} has cancelled their booking for "
                "{nama_event}. You may want to follow up with them."
            )
        )


    # ==========================================================
    # ---- TAMPILAN STUDENT / UMUM ----
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _render_student()
    # Membangun tampilan notifikasi untuk mahasiswa/umum:
    #   Kategori "My Schedule":
    #   - Event reminder
    #   - Critical updates
    #   Kategori "Discovery":
    #   - Interest match
    #   - Campus Spotlight
    # ----------------------------------------------------------
    def _render_student(self, layout):

        # ---- KATEGORI: My Schedule ----
        self._buat_label_kategori("My Schedule", layout)
        layout.addSpacing(12)

        # Item 1: Event reminder
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_event_reminder",
            judul="Event reminder",
            deskripsi=(
                "Stay on track with alerts 1 day before your event start."
            ),
            default_on=True,
            pesan_default=(
                "⏰ Reminder: {nama_event} is happening tomorrow! "
                "Don't forget — it starts at {waktu_event}. See you there!"
            )
        )

        # Item 2: Critical updates
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_critical_updates",
            judul="Critical updates",
            deskripsi=(
                "Instant alerts for any last-minute changes in venue, "
                "time, or cancellations."
            ),
            default_on=True,
            pesan_default=(
                "📢 Important update for {nama_event}: The organizer has "
                "made changes to the event details. Please check the latest "
                "information to stay up to date."
            )
        )

        layout.addSpacing(24)

        # ---- KATEGORI: Discovery ----
        self._buat_label_kategori("Discovery", layout)
        layout.addSpacing(12)

        # Item 3: Interest match
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_interest_match",
            judul="Interest match",
            deskripsi=(
                "Get notified about new events that match your favorite."
            ),
            default_on=True,
            pesan_default=(
                "✨ We found a new event you might love! {nama_event} "
                "matches your interests based on your liked events. "
                "Check it out!"
            )
        )

        # Item 4: Campus Spotlight
        self._buat_item_notif(
            layout=layout,
            nama_setting="notif_campus_spotlight",
            judul="Campus Spotlight",
            deskripsi=(
                "Exclusive updates on internal events from your "
                "university's organizations."
            ),
            default_on=True,
            pesan_default=(
                "🏫 Your campus just added a new event: {nama_event}. "
                "Be the first to know and grab your spot!"
            )
        )


    # ==========================================================
    # ---- HELPER FUNCTIONS ----
    # ==========================================================

    # ----------------------------------------------------------
    # FUNGSI _buat_label_kategori()
    # Membuat label sub-judul kategori notifikasi
    # Ukuran 27, warna #516465, font Inter
    #
    # Parameter:
    #   teks   = teks kategori, contoh: "My Schedule"
    #   layout = layout tempat label ditambahkan
    # ----------------------------------------------------------
    def _buat_label_kategori(self, teks, layout):
        lbl = QLabel(teks)
        lbl.setFont(QFont(self.font_semi, 15))
        lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        layout.addWidget(lbl)


    # ----------------------------------------------------------
    # FUNGSI _buat_item_notif()
    # Membuat satu baris item notifikasi yang terdiri dari:
    #   - Judul notifikasi (kiri atas)
    #   - Deskripsi notifikasi (kiri bawah)
    #   - Label "Push" + ToggleSwitch (kanan)
    #   - Garis pembatas di bawah
    #
    # Parameter:
    #   layout        = layout tempat item ditambahkan
    #   nama_setting  = key unik untuk menyimpan status toggle
    #   judul         = nama notifikasi, contoh: "Event reminder"
    #   deskripsi     = penjelasan singkat notifikasi
    #   default_on    = status awal toggle (True=ON, False=OFF)
    #   pesan_default = contoh pesan notifikasi yang akan dikirim
    #                   (untuk referensi developer, tidak ditampilkan di UI)
    # ----------------------------------------------------------
    def _buat_item_notif(self, layout, nama_setting, judul, deskripsi,
                          default_on=True, pesan_default=""):

        # Simpan status awal ke dictionary
        self.notif_states[nama_setting] = default_on

        # ---- CONTAINER BARIS ITEM ----
        item_widget = QWidget()
        item_widget.setStyleSheet("background: transparent;")
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 16, 0, 16)
        item_layout.setSpacing(16)

        # ---- KOLOM KIRI: Judul + Deskripsi ----
        kiri = QWidget()
        kiri.setStyleSheet("background: transparent;")
        kiri_layout = QVBoxLayout(kiri)
        kiri_layout.setContentsMargins(0, 0, 0, 0)
        kiri_layout.setSpacing(4)

        # Judul notifikasi
        # Ukuran 30, warna #516465, font Inter SemiBold
        lbl_judul = QLabel(judul)
        lbl_judul.setFont(QFont(self.font_semi, 16))
        lbl_judul.setStyleSheet(f"color: {COLOR_TEAL_DARK};")
        kiri_layout.addWidget(lbl_judul)

        # Deskripsi notifikasi
        # Ukuran 23, warna #828282, font Inter Regular
        lbl_desk = QLabel(deskripsi)
        lbl_desk.setFont(QFont(self.font_regular, 12))
        lbl_desk.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_desk.setWordWrap(True)
        kiri_layout.addWidget(lbl_desk)

        item_layout.addWidget(kiri, stretch=1)

        # ---- KOLOM KANAN: Label "Push" + Toggle ----
        kanan = QWidget()
        kanan.setStyleSheet("background: transparent;")
        kanan_layout = QHBoxLayout(kanan)
        kanan_layout.setContentsMargins(0, 0, 0, 0)
        kanan_layout.setSpacing(8)
        kanan_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Toggle switch
        toggle = ToggleSwitch()
        toggle.set_on(default_on)
        toggle.setCursor(Qt.PointingHandCursor)

        # Label "Push" yang mengikuti status toggle
        # Warna teks menyesuaikan status ON/OFF
        lbl_push = QLabel("Push")
        lbl_push.setFont(QFont(self.font_regular, 11))
        lbl_push.setStyleSheet(
            f"color: {COLOR_TEAL_DARK};" if default_on
            else f"color: {COLOR_TEXT_MUTED};"
        )

        # Saat toggle diklik → update status + warna label Push
        def on_toggled(is_on, key=nama_setting, lbl=lbl_push):
            self.notif_states[key] = is_on
            lbl.setStyleSheet(
                f"color: {COLOR_TEAL_DARK};" if is_on
                else f"color: {COLOR_TEXT_MUTED};"
            )

        toggle.toggled.connect(on_toggled)

        kanan_layout.addWidget(toggle)
        kanan_layout.addWidget(lbl_push)

        item_layout.addWidget(kanan)
        layout.addWidget(item_widget)

        # ---- GARIS PEMBATAS ----
        # Warna #888780 sesuai spesifikasi mockup
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"color: {COLOR_DIVIDER}; background-color: {COLOR_DIVIDER};")
        layout.addWidget(divider)


    # ----------------------------------------------------------
    # FUNGSI get_notif_states()
    # Mengembalikan dictionary status semua toggle notifikasi
    # Berguna untuk menyimpan preferensi user ke database
    #
    # Return:
    #   dict { nama_setting: bool }
    #   contoh: { "notif_event_reminder": True, ... }
    # ----------------------------------------------------------
    def get_notif_states(self):
        return self.notif_states.copy()


# ==============================================================
# BLOK TESTING MANDIRI
# Jalankan: python settings/notifications_window.py
# Ganti "role" untuk test tampilan EO vs student/umum
# ==============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = QDialog()
    dialog.setWindowTitle("Notification Settings - Preview")
    dialog.setFixedSize(900, 650)
    dialog.setStyleSheet("""
        QDialog {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #BDD7D8, stop:0.5 #D6E6E6,
                stop:0.75 #D2E6E5, stop:1 #F7CBCA
            );
        }
    """)

    stacked = QStackedWidget(dialog)
    stacked.setGeometry(0, 0, 900, 650)
    stacked.setStyleSheet("background: transparent;")

    # Ganti role untuk test:
    # ROLE_ORGANIZER → tampilan EO
    # ROLE_MAHASISWA → tampilan student
    # ROLE_UMUM      → tampilan umum (sama dengan student)
    user_dummy = {
        "nama"   : "Student",
        "role"   : ROLE_MAHASISWA,   # Ganti di sini
        "inisial": "S"
    }

    panel = NotificationsPanel(user_data=user_dummy, stacked_widget=stacked)
    stacked.addWidget(panel)
    stacked.setCurrentWidget(panel)

    dialog.show()
    sys.exit(app.exec_())
# ==============================================================
# FILE: setting_item_widget.py
# TUGAS: Membuat komponen satu baris pengaturan
#        berisi judul, deskripsi, dan toggle ON/OFF
#        Digunakan di halaman Settings → Notifications,
#        Appearance, Language, dan Your Events
# DIBUAT OLEH: UI/UX Component Builder
# ==============================================================


# QWidget     = class dasar untuk semua komponen visual di PyQt5
# QHBoxLayout = pengatur tata letak horizontal (kiri ke kanan)
# QVBoxLayout = pengatur tata letak vertikal (atas ke bawah)
# QLabel      = komponen untuk menampilkan teks
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

# pyqtSignal = cara membuat sinyal komunikasi antar komponen
from PyQt5.QtCore import pyqtSignal

# Mengimport class ToggleSwitch dari file toggle_widget.py
# ToggleSwitch = komponen tombol ON/OFF yang sudah dibuat sebelumnya
from toggle_widget import ToggleSwitch
from PyQt5.QtGui import QFont


# ==============================================================
# CLASS SettingItem
# Mewarisi QWidget artinya SettingItem ADALAH komponen UI
# Satu objek SettingItem = satu baris pengaturan di halaman Settings
# Contoh: "New registrant" dengan toggle Push ON
# ==============================================================
class SettingItem(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Sinyal ini dipancarkan saat user mengubah toggle ON/OFF
    # Membawa 2 data sekaligus:
    #   str  = nama_setting, untuk tahu pengaturan mana yang diubah
    #   bool = status, True (ON) atau False (OFF)
    # Contoh: toggled.emit("notif_email", True)
    # ----------------------------------------------------------
    toggled = pyqtSignal(str, bool)


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek SettingItem pertama kali dibuat
    #
    # Parameter:
    #   judul        = teks judul pengaturan (tebal)
    #                  contoh: "New registrant"
    #   deskripsi    = teks penjelasan di bawah judul (abu-abu)
    #                  contoh: "Get alerts every time a user registers"
    #   nama_setting = pengenal unik pengaturan ini
    #                  contoh: "notif_push", "notif_email"
    #                  dibawa sinyal agar main_window tahu yang mana diubah
    #   default_on   = status awal toggle saat pertama dibuat
    #                  True = ON (default), False = OFF
    #   parent       = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, judul, deskripsi, nama_setting, default_on=True, parent=None):

        super().__init__(parent)

        # Menyimpan nama_setting sebagai atribut objek
        # Digunakan saat sinyal dipancarkan agar main_window tau
        # pengaturan mana yang sedang diubah user
        self.nama_setting = nama_setting

        # Memanggil fungsi untuk membangun tampilan item
        # Mengirim judul, deskripsi, dan status awal toggle
        self.setup_ui(judul, deskripsi, default_on)

        # Memanggil fungsi untuk mengatur gaya visual item
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun tampilan satu baris pengaturan:
    #   Kiri  = judul (tebal) + deskripsi (abu-abu) → tersusun vertikal
    #   Kanan = toggle ON/OFF
    # Dipanggil sekali saat objek pertama kali dibuat
    # ----------------------------------------------------------
    def setup_ui(self, judul, deskripsi, default_on):

        # Layout horizontal sebagai susunan utama item
        # Elemen tersusun dari kiri ke kanan:
        # [teks kiri] [stretch] [toggle kanan]
        layout = QHBoxLayout()

        # Margin: atas-bawah 12px, kiri-kanan 0px
        # Memberi jarak antar item agar tidak terlalu rapat
        layout.setContentsMargins(0, 12, 0, 12)


        # ---- BAGIAN KIRI: JUDUL DAN DESKRIPSI ----

        # Layout vertikal khusus untuk teks kiri
        # Judul di atas, deskripsi di bawahnya
        text_layout = QVBoxLayout()

        # Membuat label judul dengan teks yang dikirim dari luar
        # contoh: "New registrant"
        self.judul_label = QLabel(judul)

        # Memberi nama objek untuk ditarget QSS di apply_style()
        # "judul_label" = style font tebal, warna hitam
        self.judul_label.setObjectName("judul_label")

        # Membuat label deskripsi dengan teks penjelasan
        # contoh: "Get alerts every time a user registers"
        self.deskripsi_label = QLabel(deskripsi)

        # Memberi nama objek untuk ditarget QSS
        # "deskripsi_label" = style font kecil, warna abu-abu
        self.deskripsi_label.setObjectName("deskripsi_label")

        # Mengaktifkan word wrap agar deskripsi panjang
        # tidak terpotong melainkan turun ke baris berikutnya
        self.deskripsi_label.setWordWrap(True)

        # Menambahkan judul dan deskripsi ke layout teks
        # Judul di atas, deskripsi di bawah
        text_layout.addWidget(self.judul_label)
        text_layout.addWidget(self.deskripsi_label)


        # ---- BAGIAN KANAN: TOGGLE SWITCH ----

        # Membuat objek ToggleSwitch dari toggle_widget.py
        self.toggle = ToggleSwitch()

        # Mengatur status awal toggle sesuai parameter default_on
        # True = ON (teal gelap), False = OFF (abu)
        self.toggle.set_on(default_on)

        # Menghubungkan sinyal toggled dari ToggleSwitch
        # ke sinyal toggled milik SettingItem ini
        # lambda status = fungsi kecil yang menerima nilai True/False
        # dari toggle, lalu meneruskannya bersama nama_setting
        # Contoh alur:
        #   User klik toggle → toggle.toggled.emit(True)
        #   → lambda menerima True
        #   → self.toggled.emit("notif_push", True)
        #   → main_window.py menerima dan merespons
        self.toggle.toggled.connect(
            lambda status: self.toggled.emit(self.nama_setting, status)
        )


        # ---- MENYUSUN SEMUA ELEMEN KE LAYOUT UTAMA ----

        # Menambahkan layout teks (judul+deskripsi) ke layout utama
        # Posisinya di sebelah kiri
        layout.addLayout(text_layout)

        # Mendorong toggle ke sebelah kanan
        # addStretch() = mengisi ruang kosong di antara teks dan toggle
        layout.addStretch()

        # Menambahkan toggle ke layout utama
        # Posisinya di sebelah kanan karena addStretch() sudah mendorong
        layout.addWidget(self.toggle)

        # Menerapkan layout ke widget item ini
        self.setLayout(layout)


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual menggunakan QSS
    # Disesuaikan dengan mockup Figma
    # ----------------------------------------------------------
    def apply_style(self):

        self.setStyleSheet("""
            # Mengatur font Inter SemiBold untuk judul
            font_judul = QFont("Inter SemiBold", 14)
            
            # DemiBold = SemiBold dalam istilah QFont
            # Memastikan ketebalan font benar-benar SemiBold 
            font_judul.setWeight(QFont.DemiBold)
                           
            # Menerapkan font ke label judul
            self.judul_label.setFont(font_judul)

            # Mengatur font Inter Regular untuk deskripsi
            font_deskripsi = QFont("Inter SemiBold", 11)
            font_deskripsi.setWeight(QFont.Normal)
            self.deskripsi_label.setFont(font_deskripsi)
                           
            /* Judul pengaturan: tebal, warna hitam gelap */
            QLabel#judul_label {
                font-size: 14px;
                font-weight: bold;
                color: #000000;
            }

            /* Deskripsi pengaturan: kecil, warna abu-abu */
            QLabel#deskripsi_label {
                font-size: 11px;
                color: #828282;
            }
        """)
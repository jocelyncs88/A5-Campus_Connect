# ==============================================================
# FILE: success_page.py
# TUGAS: Membuat halaman konfirmasi setelah event berhasil
#        dipublikasi, berisi ringkasan data event
# DIBUAT OLEH: UI/UX Component Builder 
# ==============================================================


# QWidget     = class dasar untuk semua komponen visual
# QVBoxLayout = layout vertikal (atas ke bawah)
# QHBoxLayout = layout horizontal (kiri ke kanan)
# QLabel      = komponen teks
# QPushButton = tombol yang bisa diklik
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton)

# Qt         = konstanta PyQt5 seperti Qt.AlignCenter
# pyqtSignal = sinyal komunikasi antar komponen
from PyQt5.QtCore import Qt, pyqtSignal

# QFont             = class untuk mengatur font
# QColor            = class untuk warna
# QGraphicsDropShadowEffect = efek bayangan
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


# ==============================================================
# CLASS SuccessPage
# Mewarisi QWidget artinya SuccessPage ADALAH halaman UI
# Halaman ini tampil setelah event berhasil dipublikasi
# Berisi ringkasan data event
# ==============================================================
class SuccessPage(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Dipancarkan saat user klik "Lihat Event"
    # main_window.py akan kembali ke homepage
    # Event belum tentu di acc user akan diberitau via email
    # setelah proses validasi admin selesai
    # ----------------------------------------------------------
    lihat_event_diklik = pyqtSignal()

    # Dipancarkan saat user klik "Buat Event Lain"
    # main_window.py akan kembali ke halaman form Add Event kosong
    buat_event_lain_diklik = pyqtSignal()


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek SuccessPage pertama kali dibuat
    #
    # Parameter:
    #   parent = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # Menyimpan data event yang baru dipublikasi
        # Akan diisi lewat fungsi set_data() dari main_window.py
        self.data_event = {}

        self.setObjectName("success_page")
        self.setup_ui()
        self.apply_style()

        # Menambahkan efek shadow pada card 
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 30))   # hitam transparan
        shadow.setOffset(0, 4)                  # sedikit ke bawah
        shadow.setBlurRadius(24)                # blur halus
        self.card.setGraphicsEffect(shadow)


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun tampilan halaman sukses
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout halaman menengahkan card ke tengah layar
        page_layout = QVBoxLayout()
        page_layout.setAlignment(Qt.AlignCenter)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # ---- CARD UTAMA ----
        # Card putih yang membungkus semua konten sukses
        self.card = QWidget()
        self.card.setObjectName("success_card")
        self.card.setFixedWidth(460)
        self.card.setMinimumHeight(500)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)


        # ---- ICON CENTANG ----

        # Lingkaran hijau muda dengan centang di tengahnya
        # Dibuat dari QLabel dengan border-radius 50% via QSS
        self.icon_container = QLabel("✓")
        self.icon_container.setObjectName("icon_container")
        self.icon_container.setAlignment(Qt.AlignCenter)

        # Ukuran tetap agar lingkaran sempurna
        self.icon_container.setFixedSize(72, 72)
        card_layout.addWidget(self.icon_container, alignment=Qt.AlignCenter)


        # ---- JUDUL SUKSES ----

        self.judul_label = QLabel("Event berhasil dikirim!")
        self.judul_label.setObjectName("judul_label")
        self.judul_label.setAlignment(Qt.AlignCenter)

        # Font Inter SemiBold ukuran 22 sesuai mockup
        font_judul = QFont("Inter SemiBold", 22)
        font_judul.setWeight(QFont.DemiBold)
        self.judul_label.setFont(font_judul)
        card_layout.addWidget(self.judul_label)


        # ---- TEKS PENJELASAN ----

        self.deskripsi_label = QLabel(
            "Event kamu sedang menunggu validasi admin."
            "Kami akan memberitahu melalui email setelah"
            "proses pemeriksaan selesai dilakukan."
        )
        self.deskripsi_label.setObjectName("deskripsi_label")
        self.deskripsi_label.setAlignment(Qt.AlignCenter)

        # setWordWrap agar teks panjang tidak terpotong
        self.deskripsi_label.setWordWrap(True)

        font_desk = QFont("Inter", 12)
        font_desk.setWeight(QFont.Normal)
        self.deskripsi_label.setFont(font_desk)
        card_layout.addWidget(self.deskripsi_label)


        # Jarak sebelum kotak info
        card_layout.addSpacing(8)


        # ---- KOTAK INFO EVENT ----
        # Berisi Nama Event, Tanggal, dan Status dalam kotak abu muda

        self.info_box = QWidget()
        self.info_box.setObjectName("info_box")

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setSpacing(10)

        # Baris Nama Event
        self.baris_nama = self._buat_baris_info("Nama Event", "-")
        info_layout.addLayout(self.baris_nama)

        # Baris Tanggal
        self.baris_tanggal = self._buat_baris_info("Tanggal", "-")
        info_layout.addLayout(self.baris_tanggal)

        # Baris Status
        self.baris_status = self._buat_baris_info("Status", "Menunggu Validasi")
        info_layout.addLayout(self.baris_status)

        self.info_box.setLayout(info_layout)
        card_layout.addWidget(self.info_box)


        # Jarak sebelum tombol
        card_layout.addSpacing(8)


        # ---- TOMBOL AKSI ----

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        # Tombol Lihat Event (outline)
        self.btn_lihat = QPushButton("Lihat Event")
        self.btn_lihat.setObjectName("btn_lihat")
        self.btn_lihat.setFixedHeight(48)

        font_btn = QFont("Inter Medium", 13)
        font_btn.setWeight(QFont.Medium)
        self.btn_lihat.setFont(font_btn)

        # Saat diklik → pancarkan sinyal ke main_window.py
        self.btn_lihat.clicked.connect(self.lihat_event_diklik.emit)

        # Tombol Buat Event Lain (teal gelap)
        self.btn_buat_lain = QPushButton("Buat Event Lain")
        self.btn_buat_lain.setObjectName("btn_buat_lain")
        self.btn_buat_lain.setFixedHeight(48)
        self.btn_buat_lain.setFont(font_btn)

        # Saat diklik → pancarkan sinyal ke main_window.py
        self.btn_buat_lain.clicked.connect(self.buat_event_lain_diklik.emit)

        btn_layout.addWidget(self.btn_lihat)
        btn_layout.addWidget(self.btn_buat_lain)
        card_layout.addLayout(btn_layout)

        self.card.setLayout(card_layout)
        page_layout.addWidget(self.card)
        self.setLayout(page_layout)


    # ----------------------------------------------------------
    # FUNGSI _buat_baris_info()
    # Fungsi helper untuk membuat satu baris di kotak info
    # Berisi label kiri (abu) dan nilai kanan (tebal/hitam)
    #
    # Parameter:
    #   label = teks di kiri, contoh: "Nama Event"
    #   nilai = teks di kanan, contoh: "Tech Seminar 2026"
    #
    # Return:
    #   QHBoxLayout berisi dua QLabel (kiri dan kanan)
    # ----------------------------------------------------------
    def _buat_baris_info(self, label, nilai):

        baris = QHBoxLayout()

        # Label kiri: abu-abu, Regular
        label_widget = QLabel(label)
        label_widget.setObjectName("info_label_kiri")
        font_kiri = QFont("Inter", 12)
        font_kiri.setWeight(QFont.Normal)
        label_widget.setFont(font_kiri)

        # Nilai kanan: hitam, Bold, rata kanan
        nilai_widget = QLabel(nilai)
        nilai_widget.setObjectName("info_label_kanan")
        font_kanan = QFont("Inter SemiBold", 12)
        font_kanan.setWeight(QFont.DemiBold)
        nilai_widget.setFont(font_kanan)
        nilai_widget.setAlignment(Qt.AlignRight)

        baris.addWidget(label_widget)
        baris.addWidget(nilai_widget)

        # Menyimpan referensi nilai_widget agar bisa diupdate
        # lewat fungsi set_data() nanti
        setattr(self, f"nilai_{label.lower().replace(' ', '_')}", nilai_widget)

        return baris


    # ----------------------------------------------------------
    # FUNGSI set_data()
    # Dipanggil dari main_window.py setelah event dipublikasi
    # Mengisi kotak info dengan data event yang baru dibuat
    #
    # Parameter:
    #   data = dictionary data event dari add_event_page.py
    #          berisi key: nama_event, tanggal, dll
    # ----------------------------------------------------------
    def set_data(self, data):

        # Simpan data untuk referensi
        self.data_event = data

        # Update teks di kotak info sesuai data event
        # getattr() = ambil atribut berdasarkan nama string
        self.nilai_nama_event.setText(data.get("nama_event", "-"))
        self.nilai_tanggal.setText(data.get("tanggal", "-"))
        self.nilai_status.setText(data.get("status", "Menunggu Validasi"))


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual sesuai mockup Figma
    # ----------------------------------------------------------
    def apply_style(self):

        self.setStyleSheet("""

            /* Halaman: background abu sangat muda */
            QWidget#success_page {
                background-color: #D2E6E5;
            }

            /* Card putih utama: sudut membulat, tanpa border */
            QWidget#success_card {
                background-color: white;
                border-radius: 16px;
                border: none;
            }

            /* Icon centang: lingkaran hijau muda */
            QLabel#icon_container {
                background-color: #EAF3DE;
                color: #1D9E75;
                border-radius: 36px;
                font-size: 28px;
                font-weight: bold;
            }

            /* Judul "Event berhasil dipublikasi!" */
            QLabel#judul_label {
                color: #1a1a1a;
                font-size: 22px;
            }

            /* Teks penjelasan: abu-abu, kecil */
            QLabel#deskripsi_label {
                color: #5F5E5A;
                font-size: 12px;
                line-height: 160%;
            }

            /* Kotak info event: background abu muda */
            QWidget#info_box {
                background-color: #F1EFE8;
                border-radius: 10px;
                border: none;
            }

            /* Label kiri di kotak info: abu */
            QLabel#info_label_kiri {
                color: #706F6C;
                font-size: 12px;
            }

            /* Nilai kanan di kotak info: hitam tebal */
            QLabel#info_label_kanan {
                color: #1a1a1a;
                font-size: 12px;
                font-weight: 600;
            }

            /* Tombol Lihat Event: outline abu */
            QPushButton#btn_lihat {
                background-color: white;
                color: #4A5568;
                border: 1px solid #CBD5E0;
                border-radius: 10px;
                font-size: 13px;
            }

            QPushButton#btn_lihat:hover {
                background-color: #F0F0F0;
            }

            /* Tombol Buat Event Lain: teal gelap */
            QPushButton#btn_buat_lain {
                background-color: #2D6A6A;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton#btn_buat_lain:hover {
                background-color: #3a7a7a;
            }
        """)
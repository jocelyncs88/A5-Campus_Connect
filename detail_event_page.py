# ==============================================================
# FILE: detail_event_page.py
# TUGAS: Membuat halaman detail event yang muncul saat
#        user klik kartu event di homepage
# DIBUAT OLEH: UI/UX Component Builder 
# ==============================================================


# QWidget      = class dasar untuk semua komponen visual
# QVBoxLayout  = layout vertikal (atas ke bawah)
# QHBoxLayout  = layout horizontal (kiri ke kanan)
# QLabel       = komponen teks/gambar
# QPushButton  = tombol yang bisa diklik
# QScrollArea  = area scroll jika konten panjang
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QScrollArea,
                              QSizePolicy, QGraphicsDropShadowEffect)

# Qt         = konstanta PyQt5
# pyqtSignal = sinyal komunikasi antar komponen
from PyQt5.QtCore import QSize, Qt, pyqtSignal

# QFont   = class untuk mengatur font
# QPixmap = class untuk menampilkan gambar
from PyQt5.QtGui import QFont, QPixmap, QColor, QIcon

import os
import requests


# ==============================================================
# CLASS DetailEventPage
# Mewarisi QWidget artinya DetailEventPage ADALAH halaman UI
# Menampilkan detail lengkap satu event yang dipilih user
# ==============================================================
class DetailEventPage(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Dipancarkan saat user klik tombol "← Back"
    # main_window.py akan kembali ke homepage
    # ----------------------------------------------------------
    kembali_diklik = pyqtSignal()


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # ----------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # Menyimpan data event yang sedang ditampilkan
        self.data_event = {}

        self.setObjectName("detail_event_page")
        self.setup_ui()
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun tampilan halaman detail event
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout utama halaman
        outer_layout = QVBoxLayout()
        # membuat konten sedikit turun dari atas
        outer_layout.setContentsMargins(40, 20, 40, 40)
        # jarak antar komponen
        outer_layout.setSpacing(0)

        # ==============================================
        # TOP BAR FLOATING
        # ==============================================

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # tombol back pakai icon gambar
        self.btn_back = QPushButton()
        self.btn_back.setObjectName("btn_back")

        # path gambar icon
        icon_path = os.path.join("assets", "arrow_back.png")

        # set icon
        self.btn_back.setIcon(QIcon(icon_path))

        # ukuran icon
        self.btn_back.setIconSize(QSize(28, 28))

        # ukuran tombol
        self.btn_back.setFixedSize(40, 40)

        # klik kembali ke homepage
        self.btn_back.clicked.connect(self.kembali_diklik.emit)

        top_layout.addWidget(self.btn_back)
        top_layout.addStretch()

        outer_layout.addLayout(top_layout)

        # kasih jarak ke bawah
        outer_layout.addSpacing(35)

        # ---- KONTEN UTAMA ----
        # Scroll area agar bisa discroll jika konten panjang

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        konten_widget = QWidget()
        konten_widget.setObjectName("konten_widget")
        konten_layout = QHBoxLayout(konten_widget)
        konten_layout.setContentsMargins(0, 20, 0, 0)
        konten_layout.setSpacing(70)
        konten_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)


        # ==============================================
        # BAGIAN KIRI: POSTER EVENT
        # ==============================================

        # Label untuk menampilkan gambar poster
        self.poster_label = QLabel()
        self.poster_label.setObjectName("poster_label")
        self.poster_label.setFixedSize(320, 450)
        self.poster_label.setScaledContents(True)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setText("No Image")

        # Shadow untuk poster
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        shadow.setBlurRadius(24)
        self.poster_label.setGraphicsEffect(shadow)

        konten_layout.addWidget(self.poster_label, stretch=0)


        # ==============================================
        # BAGIAN KANAN: INFO EVENT
        # ==============================================

        info_widget = QWidget()
        info_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(18)
        info_layout.setAlignment(Qt.AlignTop)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # ---- BADGE JENIS EVENT ----
        # Internal atau External
        self.badge_jenis = QLabel("External")
        self.badge_jenis.setObjectName("badge_external")
        self.badge_jenis.setFixedHeight(28)
        font_badge = QFont("Inter SemiBold", 11)
        font_badge.setWeight(QFont.DemiBold)
        self.badge_jenis.setFont(font_badge)
        self.badge_jenis.setAlignment(Qt.AlignCenter)
        self.badge_jenis.setFixedWidth(90)
        info_layout.addWidget(self.badge_jenis)


        # ---- NAMA EVENT ----
        self.nama_label = QLabel("Nama Event")
        self.nama_label.setObjectName("nama_label")
        self.nama_label.setWordWrap(True)
        font_nama = QFont("Inter", 40)
        font_nama.setWeight(QFont.Bold)
        self.nama_label.setFont(font_nama)
        info_layout.addWidget(self.nama_label)


        # ---- INFO LOKASI ----

        lokasi_layout = QHBoxLayout()
        lokasi_layout.setSpacing(12)

        self.icon_lokasi = QLabel()
        # load gambar icon lokasi
        lokasi_pixmap = QPixmap(os.path.join("assets", "place.png"))

        # resize icon
        lokasi_pixmap = lokasi_pixmap.scaled(
            22, 22,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.icon_lokasi.setPixmap(lokasi_pixmap)
        self.icon_lokasi.setFixedSize(24, 24)

        self.lokasi_label = QLabel("Lokasi belum tersedia")
        self.lokasi_label.setObjectName("info_label")
        self.lokasi_label.setWordWrap(True)
        font_info = QFont("Inter", 17)
        font_info.setWeight(QFont.Normal)
        self.lokasi_label.setFont(font_info)

        lokasi_layout.addWidget(self.icon_lokasi)
        lokasi_layout.addWidget(self.lokasi_label)
        lokasi_layout.addStretch()
        info_layout.addLayout(lokasi_layout)


        # ---- INFO TANGGAL & WAKTU ----

        waktu_layout = QHBoxLayout()
        waktu_layout.setSpacing(12)

        self.icon_waktu = QLabel()
        # load gambar icon waktu
        waktu_pixmap = QPixmap(os.path.join("assets", "clock.png"))

        # resize icon
        waktu_pixmap = waktu_pixmap.scaled(
            22, 22,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.icon_waktu.setPixmap(waktu_pixmap)
        self.icon_waktu.setFixedSize(24, 24)

        self.waktu_label = QLabel("Tanggal belum tersedia")
        self.waktu_label.setObjectName("info_label")
        self.waktu_label.setFont(font_info)
        waktu_layout.addWidget(self.icon_waktu)
        waktu_layout.addWidget(self.waktu_label)
        waktu_layout.addStretch()
        info_layout.addLayout(waktu_layout)


        # ---- INFO PENYELENGGARA ----

        penyelenggara_layout = QHBoxLayout()
        penyelenggara_layout.setSpacing(10)

        self.icon_penyelenggara = QLabel()
        home_pixmap = QPixmap(os.path.join("assets", "universitas.png"))

        home_pixmap = home_pixmap.scaled(
            22, 22,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.icon_penyelenggara.setPixmap(home_pixmap)
        self.icon_penyelenggara.setFixedSize(24, 24)

        self.penyelenggara_label = QLabel("Penyelenggara belum tersedia")
        self.penyelenggara_label.setObjectName("info_label")
        self.penyelenggara_label.setFont(font_info)
        penyelenggara_layout.addWidget(self.icon_penyelenggara)
        penyelenggara_layout.addWidget(self.penyelenggara_label)
        penyelenggara_layout.addStretch()
        info_layout.addLayout(penyelenggara_layout)

        # ---- INFO TIKET ----

        tiket_layout = QHBoxLayout()
        tiket_layout.setSpacing(12)
        self.icon_tiket = QLabel()
        # load gambar icon tiket
        tiket_pixmap = QPixmap(os.path.join("assets", "ticket.png"))

        # resize icon
        tiket_pixmap = tiket_pixmap.scaled(
            22, 22,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.icon_tiket.setPixmap(tiket_pixmap)
        self.icon_tiket.setFixedSize(24, 24)
        self.tiket_label = QLabel("Gratis")
        self.tiket_label.setObjectName("info_label")
        self.tiket_label.setFont(font_info)
        tiket_layout.addWidget(self.icon_tiket)
        tiket_layout.addWidget(self.tiket_label)
        tiket_layout.addStretch()
        info_layout.addLayout(tiket_layout)

        # ---- GARIS PEMISAH ----
        garis = QWidget()
        garis.setFixedHeight(1)
        garis.setObjectName("garis_pemisah")
        info_layout.addWidget(garis)
        info_layout.addSpacing(4)

        # ---- LABEL OVERVIEW ----
        self.label_overview = QLabel("Overview")
        self.label_overview.setObjectName("label_overview")
        font_overview = QFont("Inter", 26)
        font_overview.setWeight(QFont.Bold)
        self.label_overview.setFont(font_overview)
        info_layout.addWidget(self.label_overview)

        # ---- DESKRIPSI EVENT ----

        self.deskripsi_label = QLabel("Deskripsi belum tersedia")
        self.deskripsi_label.setObjectName("deskripsi_label")
        self.deskripsi_label.setWordWrap(True)
        font_desk = QFont("Inter", 17)
        self.deskripsi_label.setFont(font_desk)
        info_layout.addWidget(self.deskripsi_label)
        info_layout.addStretch()

        konten_layout.addWidget(info_widget, alignment=Qt.AlignTop)

        scroll.setWidget(konten_widget)
        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)

    # ----------------------------------------------------------
    # FUNGSI set_data()
    # Dipanggil dari main_window.py dengan data event dari database
    # Mengisi semua label dengan data event yang dipilih
    #
    # Parameter:
    #   data = dictionary data event dari database
    # ----------------------------------------------------------
    def set_data(self, data):

        # Simpan data untuk referensi
        self.data_event = data

        # ---- POSTER ----
        # Coba load dari path lokal dulu
        poster_path = data.get("gambar_poster", "")
        pixmap = None

        if poster_path:
            # Coba path lokal
            if os.path.exists(poster_path):
                pixmap = QPixmap(poster_path)

            # Coba load dari URL jika path lokal gagal
            elif poster_path.startswith(("http://", "https://")):
                try:
                    response = requests.get(poster_path, timeout=10)
                    if response.status_code == 200:
                        from PyQt5.QtCore import QByteArray
                        byte_array = QByteArray(response.content)
                        pixmap = QPixmap()
                        pixmap.loadFromData(byte_array)
                except Exception:
                    pixmap = None

        if pixmap and not pixmap.isNull():
            self.poster_label.setPixmap(pixmap)
            self.poster_label.setText("")
            self.poster_label.setStyleSheet("""
                QLabel {
                    border-radius: 12px;
                    border: none;
                    background-color: transparent;
                }
            """)
        else:
            self.poster_label.setText("No Image")
            self.poster_label.setStyleSheet("""
                QLabel {
                    background-color: #D2E6E5;
                    border-radius: 12px;
                    color: #5D6B6B;
                    font-size: 14px;
                }
            """)

        # ---- BADGE JENIS EVENT ----
        jenis_event = data.get("jenis_event", "External")
        self.badge_jenis.setText(jenis_event)
        # Update styling class berdasarkan jenis event
        if jenis_event.lower() == "internal":
            self.badge_jenis.setObjectName("badge_internal")
        else:
            self.badge_jenis.setObjectName("badge_external")

        # ---- NAMA EVENT ----
        self.nama_label.setText(data.get("nama_event", "Nama Event"))

        # ---- LOKASI ----
        lokasi = data.get("lokasi", "")
        self.lokasi_label.setText(lokasi if lokasi else "Lokasi belum tersedia")

        # ---- TANGGAL & WAKTU ----
        tanggal_waktu = data.get("tanggal_waktu", "")
        if not tanggal_waktu:
            tanggal = data.get("tanggal_display", "")
            waktu = data.get("waktu_display", "")
            tanggal_waktu = f"{tanggal} {waktu}".strip()
        self.waktu_label.setText(tanggal_waktu if tanggal_waktu else "Tanggal belum tersedia")

        # ---- PENYELENGGARA ----
        # Database menyimpan nama_eo, bukan penyelenggara
        penyelenggara = data.get("penyelenggara", "") or data.get("nama_eo", "")
        self.penyelenggara_label.setText(
            penyelenggara if penyelenggara else "Penyelenggara belum tersedia"
        )

        # ---- TIKET ----
        tipe_tiket = data.get("tipe_tiket", "Gratis")
        harga = data.get("harga_tiket", "0")
        if tipe_tiket.lower() in ("paid", "berbayar"):
            self.tiket_label.setText(f"Berbayar — Rp {harga}")
        else:
            self.tiket_label.setText("Gratis")

        # ---- DESKRIPSI ----
        deskripsi = data.get("deskripsi_singkat", "")
        self.deskripsi_label.setText(
            deskripsi if deskripsi else "Deskripsi belum tersedia"
        )


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # ----------------------------------------------------------
    def apply_style(self):

        self.setStyleSheet("""

            QWidget#detail_event_page {
                background-color: transparent;
            }

            /* Navbar */
            QWidget#detail_navbar {
                background-color: #D2E6E5;
                border-radius: 40px;
            }

            /* Tombol back */
            QPushButton#btn_back {
                background-color: transparent;
                border: none;
                padding: 0px;
            }

            QPushButton#btn_back:hover {
                background-color: rgba(0, 0, 0, 0.04);
                border-radius: 20px;
            }

            /* Konten widget */
            QWidget#konten_widget {
                background-color: transparent;
            }

            /* Nama event */
            QLabel#nama_label {
                color: #516465;
                font-size: 40px;
                font-weight: 700;
            }

            /* Garis pemisah */
            QWidget#garis_pemisah {
                background-color: #E5E7EB;
            }

            /* Label info */
            QLabel#info_label {
                color: #1a1a1a;
                font-size: 17px;
            }

            /* Badge jenis event */
            QLabel#badge_internal,
            QLabel#badge_external {
                color: #516465;
                background-color: #D2E6E5;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }

            /* Label Overview */
            QLabel#label_overview {
                color: #516465;
                font-size: 26px;
                font-weight: 700;
            }

            /* Deskripsi */
            QLabel#deskripsi_label {
                color: #1a1a1a;
                font-size: 17px;
                line-height: 1.6;
            }

            /* Poster placeholder */
            QLabel#poster_label {
                background-color: #D2E6E5;
                border-radius: 12px;
                color: #5D6B6B;
                font-size: 14px;
            }
     """)                        
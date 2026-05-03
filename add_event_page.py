# ==============================================================
# FILE: add_event_page.py
# TUGAS: Membuat halaman form Tambah Event Baru
# DIBUAT OLEH: UI/UX Component Builder
# ==============================================================


# QWidget      = class dasar untuk semua komponen visual
# QVBoxLayout  = layout vertikal (atas ke bawah)
# QHBoxLayout  = layout horizontal (kiri ke kanan)
# QLabel       = komponen teks
# QLineEdit    = input teks satu baris
# QPushButton  = tombol yang bisa diklik
# QComboBox    = dropdown pilihan
# QScrollArea  = area scroll jika konten panjang
# QMessageBox  = popup pesan error/info
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton,
                              QComboBox, QScrollArea, QMessageBox,
                              QSizePolicy)

# Qt         = konstanta PyQt5
# pyqtSignal = sinyal komunikasi antar komponen
from PyQt5.QtCore import Qt, pyqtSignal

# QFont  = class untuk mengatur font
# QColor = class untuk warna
from PyQt5.QtGui import QFont, QColor, QPixmap

# Import komponen toggle dan upload poster yang sudah dibuat
from toggle_widget import ToggleSwitch
from upload_widget import PosterUploadDialog

import os


# ==============================================================
# CLASS AddEventPage
# Mewarisi QWidget artinya AddEventPage ADALAH halaman UI
# Berisi form lengkap untuk menambah event baru
# ==============================================================
class AddEventPage(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Dipancarkan saat event berhasil dipublikasi
    # Membawa dictionary data event yang baru dibuat
    # Penerima sinyal (main_window.py) yang menyimpan ke database
    # ----------------------------------------------------------
    event_dipublikasi = pyqtSignal(dict)

    # Dipancarkan saat user klik tombol "Batal"
    # main_window.py akan kembali ke halaman homepage
    dibatalkan = pyqtSignal()


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # ----------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # Menyimpan path poster yang dipilih user
        # Kosong dulu sebelum user upload poster
        self.poster_path = ""

        self.setObjectName("add_event_page")
        self.setup_ui()
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun tampilan halaman form Add Event
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout terluar halaman
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(12)

        # ---- JUDUL DAN SUBJUDUL (di luar card) ----
        self.judul_label = QLabel("Tambah Event Baru")
        self.judul_label.setObjectName("judul_label")
        font_judul = QFont("Inter", 24)
        font_judul.setWeight(QFont.ExtraBold)
        self.judul_label.setFont(font_judul)
        outer_layout.addWidget(self.judul_label)

        self.sub_judul = QLabel("Isi detail event kamu dengan lengkap agar mudah ditemukan peserta")
        self.sub_judul.setObjectName("sub_judul")
        font_sub = QFont("Inter", 12)
        font_sub.setWeight(QFont.Normal)
        self.sub_judul.setFont(font_sub)
        outer_layout.addWidget(self.sub_judul)

        # ---- SATU CARD PUTIH (form kiri + poster kanan) ----
        self.card = QWidget()
        self.card.setObjectName("form_widget")

        # Membuat card mengisi seluruh ruang yang tersedia
        # agar tidak ada ruang kosong di bawah card
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ==============================================
        # BAGIAN KIRI: FORM INPUT
        # ==============================================
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        # ---- LABEL INFORMASI UTAMA ----
        self.label_info = QLabel("INFORMASI UTAMA")
        self.label_info.setObjectName("label_section")
        font_section = QFont("Inter SemiBold", 11)
        font_section.setWeight(QFont.DemiBold)
        self.label_info.setFont(font_section)
        form_layout.addWidget(self.label_info)

        garis = QWidget()
        garis.setFixedHeight(1)
        garis.setObjectName("garis_pemisah")
        form_layout.addWidget(garis)

        # ---- BARIS 1: NAMA EVENT + JENIS EVENT ----
        baris1_layout = QHBoxLayout()
        baris1_layout.setSpacing(16)

        nama_layout = QVBoxLayout()
        self.label_nama = QLabel("Nama Event *")
        self.label_nama.setObjectName("label_field")
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Masukkan nama event")
        self.input_nama.setObjectName("input_field")
        nama_layout.addWidget(self.label_nama)
        nama_layout.addWidget(self.input_nama)

        jenis_layout = QVBoxLayout()
        self.label_jenis = QLabel("Jenis Event *")
        self.label_jenis.setObjectName("label_field")

        # QComboBox = dropdown pilihan Internal/External
        self.input_jenis = QComboBox()
        self.input_jenis.setObjectName("input_combo")
        self.input_jenis.setFixedHeight(42)

        # Placeholder item pertama yang tidak bisa dipilih
        self.input_jenis.addItem("Masukkan jenis event")
        self.input_jenis.addItem("Internal")
        self.input_jenis.addItem("External")

        # Menonaktifkan item pertama (placeholder)
        # agar user tidak bisa memilih placeholder
        self.input_jenis.model().item(0).setEnabled(False)
        jenis_layout.addWidget(self.label_jenis)
        jenis_layout.addWidget(self.input_jenis)

        baris1_layout.addLayout(nama_layout)
        baris1_layout.addLayout(jenis_layout)
        form_layout.addLayout(baris1_layout)

        # ---- BARIS 2: DESKRIPSI EVENT + KATEGORI EVENT ----
        baris2_layout = QHBoxLayout()
        baris2_layout.setSpacing(16)

        deskripsi_layout = QVBoxLayout()
        self.label_deskripsi = QLabel("Deskripsi Event *")
        self.label_deskripsi.setObjectName("label_field")
        self.input_deskripsi = QLineEdit()
        self.input_deskripsi.setPlaceholderText("Masukkan deskripsi event")
        self.input_deskripsi.setObjectName("input_field")
        deskripsi_layout.addWidget(self.label_deskripsi)
        deskripsi_layout.addWidget(self.input_deskripsi)

        # Kategori Event (input teks biasa)
        kategori_layout = QVBoxLayout()
        self.label_kategori = QLabel("Kategori Event *")
        self.label_kategori.setObjectName("label_field")
        self.input_kategori = QLineEdit()

        # Placeholder menunjukkan contoh kategori yang bisa diisi
        self.input_kategori.setPlaceholderText("Seminar/Lomba/Workshop/Rekrutmen/dll")
        self.input_kategori.setObjectName("input_field")
        kategori_layout.addWidget(self.label_kategori)
        kategori_layout.addWidget(self.input_kategori)

        baris2_layout.addLayout(deskripsi_layout)
        baris2_layout.addLayout(kategori_layout)
        form_layout.addLayout(baris2_layout)

        # ---- LABEL WAKTU & TEMPAT ----
        self.label_waktu_tempat = QLabel("Waktu & Tempat")
        self.label_waktu_tempat.setObjectName("label_section")
        self.label_waktu_tempat.setFont(font_section)
        form_layout.addWidget(self.label_waktu_tempat)

        garis2 = QWidget()
        garis2.setFixedHeight(1)
        garis2.setObjectName("garis_pemisah")
        form_layout.addWidget(garis2)

        # ---- BARIS 3: TANGGAL + WAKTU ----
        baris3_layout = QHBoxLayout()
        baris3_layout.setSpacing(16)

        tanggal_layout = QVBoxLayout()
        self.label_tanggal = QLabel("Tanggal *")
        self.label_tanggal.setObjectName("label_field")
        self.input_tanggal = QLineEdit()
        self.input_tanggal.setPlaceholderText("05/04/2026")
        self.input_tanggal.setObjectName("input_field")
        tanggal_layout.addWidget(self.label_tanggal)
        tanggal_layout.addWidget(self.input_tanggal)

        waktu_layout = QVBoxLayout()
        self.label_waktu = QLabel("Waktu *")
        self.label_waktu.setObjectName("label_field")
        self.input_waktu = QLineEdit()
        self.input_waktu.setPlaceholderText("07:00 - 12:00")
        self.input_waktu.setObjectName("input_field")
        waktu_layout.addWidget(self.label_waktu)
        waktu_layout.addWidget(self.input_waktu)

        baris3_layout.addLayout(tanggal_layout)
        baris3_layout.addLayout(waktu_layout)
        form_layout.addLayout(baris3_layout)

        # ---- BARIS 4: LOKASI + NAMA KAMPUS ----
        baris4_layout = QHBoxLayout()
        baris4_layout.setSpacing(16)

        lokasi_layout = QVBoxLayout()
        self.label_lokasi = QLabel("Lokasi *")
        self.label_lokasi.setObjectName("label_field")
        self.input_lokasi = QLineEdit()
        self.input_lokasi.setPlaceholderText("Masukkan nama alamat event")
        self.input_lokasi.setObjectName("input_field")
        lokasi_layout.addWidget(self.label_lokasi)
        lokasi_layout.addWidget(self.input_lokasi)

        kampus_layout = QVBoxLayout()
        self.label_kampus = QLabel("Nama Kampus *")
        self.label_kampus.setObjectName("label_field")
        self.input_kampus = QLineEdit()
        self.input_kampus.setPlaceholderText("Masukkan nama kampus")
        self.input_kampus.setObjectName("input_field")
        kampus_layout.addWidget(self.label_kampus)
        kampus_layout.addWidget(self.input_kampus)

        baris4_layout.addLayout(lokasi_layout)
        baris4_layout.addLayout(kampus_layout)
        form_layout.addLayout(baris4_layout)

        # ---- TIPE TIKET (TOGGLE) ----
        tiket_layout = QHBoxLayout()

        self.label_tiket = QLabel("Tipe tiket *")
        self.label_tiket.setObjectName("label_field")

        # Toggle untuk memilih Gratis atau Berbayar
        # Menggunakan ToggleSwitch dari toggle_widget.py
        self.toggle_tiket = ToggleSwitch()

        # Default OFF = Gratis
        self.toggle_tiket.set_on(False)

        # Label status tiket (Gratis/Berbayar)
        self.label_status_tiket = QLabel("Gratis")
        self.label_status_tiket.setObjectName("label_status_tiket")

        # Saat toggle diubah, label status berubah
        # dan field harga tiket muncul/sembunyi
        self.toggle_tiket.toggled.connect(self.on_toggle_tiket)

        tiket_layout.addWidget(self.toggle_tiket)
        tiket_layout.addWidget(self.label_status_tiket)
        tiket_layout.addStretch()

        form_layout.addWidget(self.label_tiket)
        form_layout.addLayout(tiket_layout)

        # ---- HARGA TIKET (tersembunyi saat Gratis) ----
        self.harga_widget = QWidget()
        harga_layout = QVBoxLayout()
        harga_layout.setContentsMargins(0, 0, 0, 0)

        self.label_harga = QLabel("Harga tiket (Rp) *")
        self.label_harga.setObjectName("label_field")

        self.input_harga = QLineEdit()
        self.input_harga.setPlaceholderText("Masukkan harga tiket")
        self.input_harga.setObjectName("input_field")

        harga_layout.addWidget(self.label_harga)
        harga_layout.addWidget(self.input_harga)
        self.harga_widget.setLayout(harga_layout)

        # Sembunyikan dulu karena default Gratis
        self.harga_widget.hide()

        form_layout.addWidget(self.harga_widget)
        form_layout.addStretch()

        # ==============================================
        # BAGIAN KANAN: UPLOAD POSTER
        # ==============================================
        poster_layout = QVBoxLayout()
        poster_layout.setContentsMargins(0, 60, 0, 0)
        poster_layout.setSpacing(8)
        poster_layout.setAlignment(Qt.AlignTop)

        # Label "Poster Event"
        self.label_poster = QLabel("Poster Event")
        self.label_poster.setObjectName("label_field")
        font_poster = QFont("Inter SemiBold", 12)
        self.label_poster.setFont(font_poster)

        # Area kotak kecil preview poster
        # Saat diklik → buka dialog upload
        self.poster_preview = QWidget()
        self.poster_preview.setObjectName("poster_preview_area")
        self.poster_preview.setFixedSize(200, 280)

        poster_preview_layout = QVBoxLayout()
        poster_preview_layout.setAlignment(Qt.AlignCenter)
        poster_preview_layout.setSpacing(8)

        # Icon dan teks default sebelum ada gambar
        self.poster_preview_icon = QLabel("⬆")
        self.poster_preview_icon.setObjectName("poster_preview_icon")
        self.poster_preview_icon.setAlignment(Qt.AlignCenter)

        self.poster_preview_text = QLabel("Klik untuk\nupload poster")
        self.poster_preview_text.setObjectName("poster_preview_text")
        self.poster_preview_text.setAlignment(Qt.AlignCenter)

        # Label untuk menampilkan gambar setelah dipilih
        # Tersembunyi dulu sebelum ada gambar
        self.poster_preview_img = QLabel()
        self.poster_preview_img.setObjectName("poster_preview_img")
        self.poster_preview_img.setFixedSize(200, 280)
        self.poster_preview_img.setScaledContents(True)
        self.poster_preview_img.hide()

        poster_preview_layout.addWidget(self.poster_preview_icon)
        poster_preview_layout.addWidget(self.poster_preview_text)
        poster_preview_layout.addWidget(self.poster_preview_img)
        self.poster_preview.setLayout(poster_preview_layout)

        # Saat area poster diklik → buka dialog upload
        self.poster_preview.mousePressEvent = self.buka_dialog_upload

        poster_layout.addWidget(self.label_poster)
        poster_layout.addWidget(self.poster_preview)
        poster_layout.addStretch()

        # Garis pemisah antara form dan tombol batal/publikasi
        garis_bawah = QWidget()
        garis_bawah.setFixedHeight(1)
        garis_bawah.setObjectName("garis_pemisah")

        # ---- TOMBOL BATAL DAN PUBLIKASI (di dalam card) ----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        # Mendorong tombol ke kanan sesuai mockup
        btn_layout.addStretch()

        # Tombol Batal
        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setObjectName("btn_batal")
        self.btn_batal.setFixedSize(120, 45)
        font_btn = QFont("Inter Medium", 13)
        self.btn_batal.setFont(font_btn)

        # Saat diklik → pancarkan sinyal dibatalkan
        # main_window.py akan kembali ke homepage
        self.btn_batal.clicked.connect(self.dibatalkan.emit)

        # Tombol Publikasi Event
        self.btn_publikasi = QPushButton("✓  Dipublikasi!")
        self.btn_publikasi.setObjectName("btn_publikasi")
        self.btn_publikasi.setFixedSize(160, 45)
        self.btn_publikasi.setFont(font_btn)

        # Saat diklik → jalankan validasi dulu
        # Jika semua field terisi → pancarkan sinyal event_dipublikasi
        self.btn_publikasi.clicked.connect(self.publikasi_event)

        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_publikasi)

        # Gabungkan form kiri dan poster kanan ke dalam layout horizontal
        konten_layout = QHBoxLayout()
        konten_layout.setSpacing(48)
        konten_layout.addLayout(form_layout, stretch=2)
        konten_layout.addLayout(poster_layout, stretch=1)

        # Layout vertikal card: konten di atas, tombol di bawah
        # Tombol masuk ke dalam card putih sesuai mockup Figma
        card_inner_layout = QVBoxLayout()
        card_inner_layout.setContentsMargins(24, 24, 24, 24)
        card_inner_layout.setSpacing(16)
        card_inner_layout.addLayout(konten_layout)
        card_inner_layout.addSpacing(8)
        card_inner_layout.addWidget(garis_bawah)  # ← garis di sini sebelum tombol
        card_inner_layout.addLayout(btn_layout)

        self.card.setLayout(card_inner_layout)

        # Bungkus card dalam scroll area agar bisa discroll
        # jika konten melebihi tinggi layar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(self.card)

        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)

    # ----------------------------------------------------------
    # FUNGSI on_toggle_tiket()
    # Dipanggil saat toggle Tipe Tiket diubah
    # Menampilkan/menyembunyikan field Harga Tiket
    # ----------------------------------------------------------
    def on_toggle_tiket(self, is_on):

        if is_on:
            # Toggle ON = Berbayar
            # Tampilkan field harga tiket
            self.label_status_tiket.setText("Berbayar")
            self.harga_widget.show()
        else:
            # Toggle OFF = Gratis
            # Sembunyikan field harga tiket
            self.label_status_tiket.setText("Gratis")
            self.harga_widget.hide()


    # ----------------------------------------------------------
    # FUNGSI on_poster_dipilih()
    # Dipanggil saat user memilih gambar di upload_widget
    # Menyimpan path gambar ke self.poster_path
    # ----------------------------------------------------------
    def on_poster_dipilih(self, path):

        # Simpan path gambar yang dipilih
        # Akan disertakan saat event dipublikasi
        self.poster_path = path

        # Tampilkan preview gambar di area poster
        pixmap = QPixmap(path)
        self.poster_preview_img.setPixmap(pixmap)

        # Sembunyikan icon dan teks default
        self.poster_preview_icon.hide()
        self.poster_preview_text.hide()

        # Tampilkan preview gambar
        self.poster_preview_img.show()

    # ----------------------------------------------------------
    # FUNGSI buka_dialog_upload()
    # Dipanggil saat user klik area preview poster
    # Membuka dialog PosterUploadDialog
    # ----------------------------------------------------------
    def buka_dialog_upload(self, event):

        # Import di sini untuk menghindari circular import
        from upload_widget import PosterUploadDialog

        # Buat objek dialog upload
        dialog = PosterUploadDialog(self)

        # Hubungkan sinyal gambar_dipilih ke fungsi on_poster_dipilih
        dialog.gambar_dipilih.connect(self.on_poster_dipilih)

        # Tampilkan dialog — tunggu sampai ditutup
        dialog.exec_()

    # ----------------------------------------------------------
    # FUNGSI publikasi_event()
    # Dipanggil saat user klik tombol "Dipublikasi!"
    # Validasi semua field wajib sebelum publikasi
    # ----------------------------------------------------------
    def publikasi_event(self):

        # ---- VALIDASI SEMUA FIELD WAJIB ----

        # Cek apakah Jenis Event sudah dipilih
        # Index 0 = placeholder "Masukkan jenis event" yang tidak valid
        if self.input_jenis.currentIndex() == 0:
            self.tampilkan_error("Jenis Event belum dipilih!")
            return

        # Dictionary field wajib yang harus diisi
        # key = nama field, value = objek QLineEdit
        fields_wajib = {
            "Nama Event"      : self.input_nama,
            "Deskripsi Event" : self.input_deskripsi,
            "Kategori Event"  : self.input_kategori,
            "Tanggal"         : self.input_tanggal,
            "Waktu"           : self.input_waktu,
            "Lokasi"          : self.input_lokasi,
            "Nama Kampus"     : self.input_kampus,
        }

        # Loop semua field wajib
        # Jika ada yang kosong → tampilkan error dan berhenti
        for nama, field in fields_wajib.items():
            if not field.text().strip():
                self.tampilkan_error(f"{nama} belum diisi!")
                return

        # Cek harga tiket jika Berbayar
        if self.toggle_tiket.is_on():
            if not self.input_harga.text().strip():
                self.tampilkan_error("Harga tiket belum diisi!")
                return

        # ---- SEMUA VALIDASI LULUS ----
        # Kumpulkan semua data form ke dalam dictionary
        # Dictionary ini yang dikirim ke main_window.py
        data_event = {
            "nama_event"       : self.input_nama.text().strip(),
            "jenis_event"      : self.input_jenis.currentText(),
            "deskripsi_singkat": self.input_deskripsi.text().strip(),
            "kategori"         : self.input_kategori.text().strip(),
            "tanggal"          : self.input_tanggal.text().strip(),
            "waktu"            : self.input_waktu.text().strip(),
            "lokasi"           : self.input_lokasi.text().strip(),
            "penyelenggara"    : self.input_kampus.text().strip(),
            "tipe_tiket"       : "Berbayar" if self.toggle_tiket.is_on() else "Gratis",
            "harga_tiket"      : self.input_harga.text().strip() if self.toggle_tiket.is_on() else "0",
            "gambar_poster"    : self.poster_path,
            "status"           : "Menunggu Validasi",
            "source"           : "Manual",
        }

        # Pancarkan sinyal event_dipublikasi membawa data event
        # main_window.py yang menerima akan menyimpan ke database
        self.event_dipublikasi.emit(data_event)


    # ----------------------------------------------------------
    # FUNGSI tampilkan_error()
    # Menampilkan popup pesan error saat validasi gagal
    # ----------------------------------------------------------
    def tampilkan_error(self, pesan):

        # QMessageBox.warning = popup pesan peringatan
        QMessageBox.warning(
            self,
            "Form Belum Lengkap",  # judul popup
            pesan                  # isi pesan error
        )

    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual sesuai mockup Figma
    # ----------------------------------------------------------
    def apply_style(self):

        # Font Inter Bold untuk semua label field
        font_label = QFont("Inter", 12)
        font_label.setWeight(QFont.Bold)

        for label in [self.label_nama, self.label_jenis,
                      self.label_deskripsi, self.label_kategori,
                      self.label_tanggal, self.label_waktu,
                      self.label_lokasi, self.label_kampus,
                      self.label_tiket, self.label_harga,
                      self.label_poster]:
            label.setFont(font_label)

        # Font Inter Regular untuk placeholder/input
        font_input = QFont("Inter", 13)
        font_input.setWeight(QFont.Normal)

        for input_field in [self.input_nama, self.input_deskripsi,
                            self.input_kategori, self.input_tanggal,
                            self.input_waktu, self.input_lokasi,
                            self.input_kampus, self.input_harga]:
            input_field.setFont(font_input)

        # Font Inter Regular untuk dropdown
        self.input_jenis.setFont(font_input)

        self.setStyleSheet("""

            /* Halaman utama: background transparan */
            QWidget#add_event_page {
                background-color: transparent;
            }

            /* Judul halaman */
            QLabel#judul_label {
                color: #1A202C;
                font-size: 24px;
            }

            /* Sub judul */
            QLabel#sub_judul {
                color: #4A5568;
                font-size: 12px;
            }

            /* Container form: background putih, sudut membulat */
            QWidget#form_widget {
                background-color: white;
                border-radius: 12px;
                border: none;
            }

            /* Label section (INFORMASI UTAMA, Waktu & Tempat) */
            QLabel#label_section {
                color: #2D3748;
                font-size: 11px;
                letter-spacing: 1px;
            }

            /* Garis pemisah */
            QWidget#garis_pemisah {
                background-color: #E5E7EB;
            }

            /* Label field (Nama Event *, dll) */
            QLabel#label_field {
                color: #2D3748;
                font-size: 12px;
            }

            /* Input field */
            QLineEdit#input_field {
                background-color: white;
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                color: #000000;
            }

            /* Input field saat fokus */
            QLineEdit#input_field:focus {
                border: 1px solid #2D6A6A;
            }

            /* Placeholder text */
            QLineEdit#input_field[text=""] {
                color: #A0AEC0;
            }

            /* Dropdown Jenis Event */
            QComboBox#input_combo {
                background-color: white;
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                color: #1a1a1a;
            }

            QComboBox#input_combo:focus {
                border: 1px solid #2D6A6A;
            }

            QComboBox#input_combo::drop-down {
                border: none;
                width: 24px;
            }

            QComboBox#input_combo::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #5D6B6B;
                width: 0px;
                height: 0px;
            }

            QComboBox#input_combo QAbstractItemView {
                background-color: white;
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                selection-background-color: #D2E6E5;
                selection-color: #1a1a1a;
            }

            /* Label status tiket (Gratis/Berbayar) */
            QLabel#label_status_tiket {
                color: #747C86;
                font-size: 13px;
            }

            /* Tombol Batal */
            QPushButton#btn_batal {
                background-color: white;
                color: #4A5568;
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                font-size: 13px;
            }

            QPushButton#btn_batal:hover {
                background-color: #f0f0f0;
            }

            /* Tombol Dipublikasi */
            QPushButton#btn_publikasi {
                background-color: #2D6A6A;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton#btn_publikasi:hover {
                background-color: #3a7a7a;
            }

            /* Area preview poster: kotak putus-putus */
            QWidget#poster_preview_area {
                background-color: #F0F7F7;
                border: 2px dashed #B0CECE;
                border-radius: 8px;
            }

            /* Icon di area preview poster */
            QLabel#poster_preview_icon {
                font-size: 24px;
                color: #5D6B6B;
            }

            /* Teks di area preview poster */
            QLabel#poster_preview_text {
                font-size: 11px;
                color: #888888;
            }
        """)
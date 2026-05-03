# ==============================================================
# FILE: upload_widget.py
# TUGAS: Membuat komponen upload poster event berupa pop up dialog
#        berisi area klik upload, progress uploading,
#        dan preview gambar setelah berhasil
# DIBUAT OLEH: UI/UX Component Builder
# ==============================================================


# QDialog      = class untuk membuat pop up dialog
# QWidget      = class dasar untuk semua komponen visual
# QVBoxLayout  = layout vertikal (atas ke bawah)
# QHBoxLayout  = layout horizontal (kiri ke kanan)
# QLabel       = komponen teks/gambar
# QPushButton  = tombol yang bisa diklik
# QFileDialog  = dialog untuk memilih file dari komputer
# QProgressBar = komponen progress bar
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QFileDialog,
                              QProgressBar)

# pyqtSignal = sinyal komunikasi antar komponen
# Qt         = konstanta PyQt5
# QTimer     = timer untuk simulasi progress uploading
from PyQt5.QtCore import pyqtSignal, Qt, QTimer

# QPixmap = class untuk menampilkan gambar
# QFont   = class untuk mengatur font
# QColor  = class untuk warna
# QGraphicsDropShadowEffect = efek bayangan
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# os = library untuk mengakses sistem file
import os


# ==============================================================
# CLASS PosterUploadDialog
# Mewarisi QDialog artinya PosterUploadDialog ADALAH pop up dialog
# Muncul saat user klik area upload poster di Add Event Page
# Memiliki 3 state tampilan:
#   1. Default   = kotak kosong, belum ada gambar
#   2. Uploading = sedang proses upload (progress bar jalan)
#   3. Preview   = gambar berhasil diupload, tampil preview
# ==============================================================
class PosterUploadDialog(QDialog):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Dipancarkan saat user klik "Gunakan Foto Ini"
    # Membawa path gambar yang dipilih
    # Penerima sinyal (add_event_page.py) yang menyimpan path
    # ----------------------------------------------------------
    gambar_dipilih = pyqtSignal(str)


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek PosterUploadDialog dibuat
    #
    # Parameter:
    #   parent = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # Menyimpan path gambar yang dipilih user
        # Kosong dulu sebelum user memilih gambar
        self.selected_path = ""

        # Timer untuk simulasi progress uploading
        # Digunakan agar progress bar bergerak naik secara bertahap
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        # Menyimpan nilai progress saat ini (0-100)
        self.progress_value = 0

        # Menghilangkan tombol help (?) di title bar dialog
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        # Ukuran dialog
        self.setFixedWidth(420)

        self.setObjectName("upload_dialog")
        self.setup_ui()
        self.apply_style()

        # Menambahkan efek shadow pada dialog sesuai mockup Figma
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(20)
        self.setGraphicsEffect(shadow)


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun tampilan pop up dialog upload poster
    # Berisi 3 state yang bergantian ditampilkan
    # ----------------------------------------------------------
    def setup_ui(self):

        # Layout utama dialog
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)


        # ---- BARIS JUDUL + TOMBOL CLOSE ----

        judul_layout = QHBoxLayout()

        # Judul "Upload Poster Event"
        self.judul_label = QLabel("Upload Poster Event")
        self.judul_label.setObjectName("judul_label")
        font_judul = QFont("Inter SemiBold", 16)
        font_judul.setWeight(QFont.DemiBold)
        self.judul_label.setFont(font_judul)

        # Tombol X untuk menutup dialog
        # Saat diklik → dialog ditutup tanpa memilih gambar
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.clicked.connect(self.reject)

        judul_layout.addWidget(self.judul_label)
        judul_layout.addStretch()
        judul_layout.addWidget(self.btn_close)
        layout.addLayout(judul_layout)


        # ==============================================
        # STATE 1: DEFAULT
        # Kotak putus-putus kosong, belum ada gambar
        # ==============================================

        # Widget kotak area upload
        self.upload_area = QWidget()
        self.upload_area.setObjectName("upload_area")
        self.upload_area.setFixedHeight(200)

        # Layout dalam area upload
        area_layout = QVBoxLayout()
        area_layout.setAlignment(Qt.AlignCenter)
        area_layout.setSpacing(8)

        # Icon upload (tanda panah ke atas)
        self.icon_label = QLabel("⬆")
        self.icon_label.setObjectName("icon_label")
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Teks utama area upload
        self.upload_text = QLabel("Klik untuk upload poster")
        self.upload_text.setObjectName("upload_text")
        self.upload_text.setAlignment(Qt.AlignCenter)

        # Teks keterangan format file yang diterima
        self.format_text = QLabel("PNG, JPG maks 5MB")
        self.format_text.setObjectName("format_text")
        self.format_text.setAlignment(Qt.AlignCenter)

        # Teks keterangan rasio yang direkomendasikan
        self.rasio_text = QLabel("Rasio potrait direkomendasikan")
        self.rasio_text.setObjectName("rasio_text")
        self.rasio_text.setAlignment(Qt.AlignCenter)

        area_layout.addWidget(self.icon_label)
        area_layout.addWidget(self.upload_text)
        area_layout.addWidget(self.format_text)
        area_layout.addWidget(self.rasio_text)
        self.upload_area.setLayout(area_layout)

        # Membuat area upload bisa diklik oleh user
        # Saat diklik → fungsi buka_file_dialog() dipanggil
        self.upload_area.mousePressEvent = self.buka_file_dialog

        layout.addWidget(self.upload_area)


        # ==============================================
        # STATE 2: UPLOADING
        # Progress bar berjalan, nama file tampil
        # Tersembunyi dulu, muncul setelah file dipilih
        # ==============================================

        # Widget container untuk state uploading
        self.uploading_widget = QWidget()
        uploading_layout = QVBoxLayout()
        uploading_layout.setSpacing(6)
        uploading_layout.setContentsMargins(0, 0, 0, 0)

        # Icon upload saat sedang proses
        self.uploading_icon = QLabel("⬆")
        self.uploading_icon.setObjectName("uploading_icon")
        self.uploading_icon.setAlignment(Qt.AlignCenter)

        # Nama file yang sedang diupload
        self.uploading_filename = QLabel()
        self.uploading_filename.setObjectName("uploading_filename")
        self.uploading_filename.setAlignment(Qt.AlignCenter)

        # Layout horizontal untuk progress bar dan persentase
        progress_layout = QHBoxLayout()

        # Progress bar yang bergerak dari 0% ke 100%
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        # Label persentase di sebelah kanan progress bar
        self.progress_persen = QLabel("0%")
        self.progress_persen.setObjectName("progress_persen")
        self.progress_persen.setFixedWidth(35)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_persen)

        # Teks "Mengupload..." sebagai status proses
        self.uploading_status = QLabel("Mengupload...")
        self.uploading_status.setObjectName("uploading_status")
        self.uploading_status.setAlignment(Qt.AlignCenter)

        # Teks "Jangan tutup halaman ini" saat uploading
        self.uploading_info = QLabel("Jangan tutup halaman ini")
        self.uploading_info.setObjectName("uploading_info")
        self.uploading_info.setAlignment(Qt.AlignCenter)

        uploading_layout.addWidget(self.uploading_icon)
        uploading_layout.addWidget(self.uploading_filename)
        uploading_layout.addLayout(progress_layout)
        uploading_layout.addWidget(self.uploading_status)
        uploading_layout.addWidget(self.uploading_info)
        self.uploading_widget.setLayout(uploading_layout)

        # Sembunyikan dulu — muncul setelah file dipilih
        self.uploading_widget.hide()
        layout.addWidget(self.uploading_widget)


        # ==============================================
        # STATE 3: PREVIEW
        # Gambar tampil, status "Berhasil diupload"
        # Tersembunyi dulu, muncul setelah upload selesai
        # ==============================================

        # Widget container untuk state preview
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(6)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        # Status berhasil diupload (centang hijau)
        self.status_label = QLabel("✓ Berhasil diupload")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignLeft)

        # Label untuk menampilkan preview gambar
        self.preview_label = QLabel()
        self.preview_label.setObjectName("preview_label")
        self.preview_label.setFixedHeight(200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(True)

        # Layout horizontal untuk nama file dan ukuran file
        file_info_layout = QHBoxLayout()

        # Nama file di kiri
        self.file_name_label = QLabel()
        self.file_name_label.setObjectName("file_info_label")

        # Ukuran file di kanan
        self.file_size_label = QLabel()
        self.file_size_label.setObjectName("file_info_label")
        self.file_size_label.setAlignment(Qt.AlignRight)

        file_info_layout.addWidget(self.file_name_label)
        file_info_layout.addWidget(self.file_size_label)

        preview_layout.addWidget(self.status_label)
        preview_layout.addWidget(self.preview_label)
        preview_layout.addLayout(file_info_layout)
        self.preview_widget.setLayout(preview_layout)

        # Sembunyikan dulu — muncul setelah upload selesai
        self.preview_widget.hide()
        layout.addWidget(self.preview_widget)


        # ---- TOMBOL AKSI ----

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # Tombol Batal — menutup dialog tanpa memilih gambar
        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setObjectName("btn_batal")

        # Saat diklik → tutup dialog (reject = tutup tanpa hasil)
        self.btn_batal.clicked.connect(self.reject)

        # Tombol Upload — disabled dulu sebelum ada gambar
        # Teksnya berubah sesuai state
        self.btn_upload = QPushButton("Upload")
        self.btn_upload.setObjectName("btn_upload")

        # Disabled dulu karena belum ada gambar yang dipilih
        self.btn_upload.setEnabled(False)
        self.btn_upload.clicked.connect(self.gunakan_foto)

        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_upload)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


    # ----------------------------------------------------------
    # FUNGSI buka_file_dialog()
    # Dipanggil saat user klik area upload (state Default)
    # Membuka dialog untuk memilih file gambar dari komputer
    # ----------------------------------------------------------
    def buka_file_dialog(self, event):

        # QFileDialog.getOpenFileName = membuka dialog pilih file
        # Hanya menampilkan file PNG dan JPG sesuai mockup
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih Poster Event",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )

        # Jika user memilih file (tidak klik Cancel)
        if file_path:

            # Cek ukuran file maksimal 5MB
            # os.path.getsize() = ambil ukuran file dalam bytes
            # 5 * 1024 * 1024 = 5MB dalam bytes
            ukuran = os.path.getsize(file_path)
            if ukuran > 5 * 1024 * 1024:
                self.upload_text.setText("❌ File terlalu besar! Maks 5MB")
                return

            # Simpan path gambar yang dipilih
            self.selected_path = file_path

            # Langsung masuk ke state Uploading
            self.tampilkan_uploading(file_path)


    # ----------------------------------------------------------
    # FUNGSI tampilkan_uploading()
    # Menampilkan state Uploading setelah file dipilih
    # Progress bar berjalan dari 0% ke 100%
    # ----------------------------------------------------------
    def tampilkan_uploading(self, file_path):

        # Sembunyikan state Default
        self.upload_area.hide()

        # Tampilkan nama file yang sedang diupload
        nama_file = os.path.basename(file_path)
        self.uploading_filename.setText(nama_file)

        # Ganti teks tombol jadi "Mengupload..."
        self.btn_upload.setText("Mengupload...")
        self.btn_upload.setEnabled(False)

        # Reset progress ke 0 sebelum mulai
        self.progress_value = 0
        self.progress_bar.setValue(0)
        self.progress_persen.setText("0%")

        # Tampilkan state Uploading
        self.uploading_widget.show()

        # Mulai timer untuk menggerakkan progress bar
        # Setiap 30ms progress naik sedikit — terlihat smooth
        self.timer.start(30)


    # ----------------------------------------------------------
    # FUNGSI update_progress()
    # Dipanggil otomatis oleh timer setiap 30ms
    # Menaikkan nilai progress bar secara bertahap
    # ----------------------------------------------------------
    def update_progress(self):

        # Naikkan progress sebesar 2 setiap 30ms
        self.progress_value += 2

        # Update tampilan progress bar dan label persentase
        self.progress_bar.setValue(self.progress_value)
        self.progress_persen.setText(f"{self.progress_value}%")

        # Jika progress sudah mencapai 100% → upload selesai
        if self.progress_value >= 100:

            # Hentikan timer
            self.timer.stop()

            # Masuk ke state Preview
            self.tampilkan_preview()


    # ----------------------------------------------------------
    # FUNGSI tampilkan_preview()
    # Menampilkan state Preview setelah upload selesai
    # Gambar tampil beserta status "Berhasil diupload"
    # ----------------------------------------------------------
    def tampilkan_preview(self):

        # Sembunyikan state Uploading
        self.uploading_widget.hide()

        # Load gambar ke QPixmap dan tampilkan di preview_label
        pixmap = QPixmap(self.selected_path)
        self.preview_label.setPixmap(pixmap)

        # Tampilkan nama file dan ukuran file
        nama_file = os.path.basename(self.selected_path)
        ukuran_mb = os.path.getsize(self.selected_path) / (1024 * 1024)
        self.file_name_label.setText(nama_file)
        self.file_size_label.setText(f"{ukuran_mb:.1f} MB")

        # Tampilkan state Preview
        self.preview_widget.show()

        # Aktifkan tombol dan ganti teksnya
        self.btn_upload.setEnabled(True)
        self.btn_upload.setText("Gunakan Foto Ini ✓")

        # Ganti tombol Batal menjadi Ganti Foto
        # Saat diklik → kembali ke state Default
        self.btn_batal.setText("Ganti Foto")
        self.btn_batal.clicked.disconnect()
        self.btn_batal.clicked.connect(self.ganti_foto)


    # ----------------------------------------------------------
    # FUNGSI ganti_foto()
    # Dipanggil saat user klik "Ganti Foto"
    # Kembali ke state Default
    # ----------------------------------------------------------
    def ganti_foto(self):

        # Sembunyikan state Preview
        self.preview_widget.hide()

        # Tampilkan kembali state Default
        self.upload_area.show()

        # Reset tombol ke kondisi awal
        self.btn_batal.setText("Batal")
        self.btn_batal.clicked.disconnect()
        self.btn_batal.clicked.connect(self.reject)
        self.btn_upload.setText("Upload")
        self.btn_upload.setEnabled(False)

        # Reset path gambar
        self.selected_path = ""


    # ----------------------------------------------------------
    # FUNGSI gunakan_foto()
    # Dipanggil saat user klik "Gunakan Foto Ini"
    # Memancarkan sinyal gambar_dipilih membawa path gambar
    # lalu menutup dialog
    # ----------------------------------------------------------
    def gunakan_foto(self):

        # Pastikan ada gambar yang dipilih sebelum emit sinyal
        if self.selected_path:

            # Pancarkan sinyal membawa path gambar
            # add_event_page.py yang menerima sinyal ini
            self.gambar_dipilih.emit(self.selected_path)

            # Tutup dialog dengan status accepted
            # accepted = user berhasil memilih gambar
            self.accept()


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual sesuai mockup Figma
    # ----------------------------------------------------------
    def apply_style(self):

        # Font Inter SemiBold untuk judul
        font_semibold = QFont("Inter SemiBold", 16)
        font_semibold.setWeight(QFont.DemiBold)
        self.judul_label.setFont(font_semibold)

        # Font Inter Medium untuk teks utama
        font_medium = QFont("Inter Medium", 12)
        font_medium.setWeight(QFont.Medium)
        for widget in [self.upload_text, self.uploading_status,
                       self.uploading_info, self.file_name_label,
                       self.file_size_label, self.btn_batal,
                       self.btn_upload, self.uploading_filename]:
            widget.setFont(font_medium)

        # Font Inter Regular untuk teks keterangan kecil
        font_regular = QFont("Inter", 11)
        font_regular.setWeight(QFont.Normal)
        for widget in [self.format_text, self.rasio_text]:
            widget.setFont(font_regular)

        # Font Inter Bold untuk persentase dan status berhasil
        font_bold = QFont("Inter", 12)
        font_bold.setWeight(QFont.Bold)
        for widget in [self.progress_persen, self.status_label]:
            widget.setFont(font_bold)

        self.setStyleSheet("""

            /* Dialog utama: background putih, sudut membulat */
            QDialog#upload_dialog {
                background-color: white;
                border-radius: 16px;
                border: none;
            }

            /* Judul: Inter SemiBold, hitam */
            QLabel#judul_label {
                color: #000000;
                font-size: 16px;
            }

            /* Tombol close X */
            QPushButton#btn_close {
                background-color: #f0f0f0;
                color: #5D6B6B;
                border: none;
                border-radius: 14px;
                font-size: 12px;
            }

            QPushButton#btn_close:hover {
                background-color: #e0e0e0;
            }

            /* Area upload default: kotak putus-putus */
            QWidget#upload_area {
                background-color: #F0F7F7;
                border: 2px dashed #B0CECE;
                border-radius: 8px;
            }

            /* Icon upload */
            QLabel#icon_label {
                font-size: 28px;
                color: #5D6B6B;
            }

            /* Icon saat uploading */
            QLabel#uploading_icon {
                font-size: 28px;
                color: #2D6A6A;
            }

            /* Teks utama area upload */
            QLabel#upload_text {
                font-size: 13px;
                color: #3a5555;
            }

            /* Teks format file */
            QLabel#format_text {
                font-size: 11px;
                color: #888888;
            }

            /* Teks rasio */
            QLabel#rasio_text {
                font-size: 11px;
                color: #888888;
            }

            /* Nama file saat uploading */
            QLabel#uploading_filename {
                font-size: 12px;
                color: #2D6A6A;
            }

            /* Persentase progress */
            QLabel#progress_persen {
                font-size: 12px;
                color: #2D6A6A;
            }

            /* Teks Mengupload... */
            QLabel#uploading_status {
                font-size: 12px;
                color: #2D6A6A;
            }

            /* Teks jangan tutup halaman */
            QLabel#uploading_info {
                font-size: 11px;
                color: #888888;
            }

            /* Status berhasil diupload: hijau */
            QLabel#status_label {
                font-size: 12px;
                color: #2D6A6A;
            }

            /* Info nama file dan ukuran */
            QLabel#file_info_label {
                font-size: 11px;
                color: #888888;
            }

            /* Tombol Batal/Ganti Foto: outline */
            QPushButton#btn_batal {
                background-color: white;
                color: #5D6B6B;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
            }

            QPushButton#btn_batal:hover {
                background-color: #f0f0f0;
            }

            /* Tombol Upload/Gunakan Foto: teal gelap */
            QPushButton#btn_upload {
                background-color: #2D6A6A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
            }

            QPushButton#btn_upload:hover {
                background-color: #3a7a7a;
            }

            /* Tombol disabled sebelum ada gambar */
            QPushButton#btn_upload:disabled {
                background-color: #CCCCCC;
                color: white;
            }

            /* Progress bar */
            QProgressBar#progress_bar {
                border: none;
                border-radius: 4px;
                background-color: #e0e0e0;
                height: 8px;
            }

            /* Warna isi progress bar */
            QProgressBar#progress_bar::chunk {
                background-color: #2D6A6A;
                border-radius: 4px;
            }
        """)
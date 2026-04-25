# ==============================================================
# FILE: card_widget.py
# TUGAS: Membuat blueprint/template untuk SATU kartu event
# yang akan ditampilkan berulang di homepage Campus Connect
# DIBUAT OLEH: UI/UX Component Builder (Tania)
# ==============================================================


# QWidget     = class dasar untuk semua komponen visual di PyQt5
# QLabel      = komponen untuk menampilkan teks atau gambar
# QVBoxLayout = pengatur tata letak vertikal (atas ke bawah)
# QSizePolicy = mengatur kebijakan ukuran komponen
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy

# QPixmap      = class khusus untuk menyimpan dan menampilkan data gambar
# QFont        = class untuk mengatur jenis dan ukuran font
# QFontDatabase = class untuk mendaftarkan font dari file .ttf
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase

# QByteArray = format data bytes yang dimengerti oleh Qt/PyQt5
# pyqtSignal = cara membuat "tombol bel" untuk komunikasi antar komponen
# Qt         = berisi konstanta seperti Qt.AlignCenter untuk perataan
from PyQt5.QtCore import QByteArray, pyqtSignal, Qt

# os = library bawaan Python untuk mengakses sistem file
# digunakan untuk mencari lokasi folder fonts secara otomatis
import os


# ==============================================================
# CLASS EventCard
# Mewarisi QWidget artinya EventCard ADALAH sebuah komponen UI
# Setiap kali satu kartu event dibuat, satu objek class ini dibuat
# Contoh: ada 5 event → ada 5 objek EventCard berbeda di memori
# ==============================================================
class EventCard(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL CLASS
    # Sinyal dideklarasikan di level class, bukan di dalam fungsi
    # Ini adalah "tombol bel" yang dipencet saat kartu diklik user
    #
    # pyqtSignal(str) artinya sinyal ini membawa 1 data bertipe string
    # Data yang dibawa adalah event_id kartu yang diklik
    # Nanti main_window.py akan "mendengarkan" sinyal ini
    # ----------------------------------------------------------
    diklik = pyqtSignal(str)


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek baru dibuat dengan EventCard(data)
    #
    # Parameter:
    #   self       = referensi ke objek itu sendiri (wajib ada)
    #   event_data = dictionary berisi semua info 1 event
    #   parent     = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, event_data, parent=None):

        # Wajib memanggil konstruktor QWidget terlebih dahulu
        # Menginisialisasi semua fitur bawaan QWidget ke objek ini
        super().__init__(parent)

        # Memberi nama objek "event_card" agar bisa ditarget QSS
        # Mirip seperti id="event_card" di HTML
        self.setObjectName("event_card")

        # Menyimpan seluruh dictionary event_data sebagai atribut objek
        # Bisa diakses dari fungsi manapun dalam class ini
        self.event_data = event_data

        # Mengambil event_id dari dictionary, default "" jika tidak ada
        # Disimpan tersendiri agar mudah diakses saat kartu diklik
        self.event_id = event_data.get("event_id", "")

        # Mencari lokasi absolut folder tempat file card_widget.py berada
        # os.path.abspath(__file__) = path lengkap file ini
        # os.path.dirname() = ambil foldernya saja (bukan nama filenya)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Mendaftarkan font Inter Medium dari file .ttf ke aplikasi
        # os.path.join() = menggabungkan path folder + subfolder + nama file
        # Setelah didaftarkan, font bisa dipakai di QFont("Inter Medium")
        QFontDatabase.addApplicationFont(os.path.join(base_dir, "assets", "Inter-Medium.ttf"))

        # Mendaftarkan font Inter Regular (untuk deskripsi event)
        QFontDatabase.addApplicationFont(os.path.join(base_dir, "assets", "Inter-Regular.ttf"))

        # Mendaftarkan font Inter SemiBold (untuk badge Internal/External)
        QFontDatabase.addApplicationFont(os.path.join(base_dir, "assets", "Inter-SemiBold.ttf"))

        # Memanggil fungsi untuk membangun semua elemen tampilan kartu
        self.setup_ui()

        # Memanggil fungsi untuk mengatur gaya visual (warna, border, dll)
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Bertugas membangun semua elemen visual di dalam kartu
    # Dipanggil sekali saat objek pertama kali dibuat
    #
    # Urutan elemen dari atas ke bawah:
    #   1. Gambar poster (rasio 1:1, 220x220px)
    #   2. Badge jenis event (menumpuk di atas gambar)
    #   3. Nama event (Inter Medium 20px)
    #   4. Deskripsi singkat (Inter Regular 16px)
    # ----------------------------------------------------------
    def setup_ui(self):

        # Membuat layout vertikal sebagai susunan utama kartu
        layout = QVBoxLayout()

        # Jarak 6 piksel antar elemen dalam layout
        layout.setSpacing(6)

        # Margin: atas=0, kiri=0, kanan=0, bawah=12
        # Bawah diberi jarak 12px agar ada napas di bawah kartu
        layout.setContentsMargins(0, 0, 0, 12)


        # ---- BAGIAN 1: GAMBAR POSTER (rasio 1:1) ----

        # Membuat QLabel sebagai bingkai gambar poster
        # Tidak ada teks placeholder karena warna abu sudah cukup
        self.poster_label = QLabel()

        # Mengunci ukuran gambar 220x220 piksel (rasio 1:1 sesuai Figma)
        self.poster_label.setFixedSize(220, 220)

        # Gambar otomatis menyesuaikan ukuran label tanpa pecah
        self.poster_label.setScaledContents(True)

        # Memberi nama objek untuk ditarget QSS
        self.poster_label.setObjectName("poster_label")

        # Meratakan konten ke tengah label
        self.poster_label.setAlignment(Qt.AlignCenter)

        # Warna abu sebagai placeholder saat gambar belum selesai didownload
        # border-radius: 8px agar sudut gambar membulat
        self.poster_label.setStyleSheet("background-color: #e0e0e0; border-radius: 8px;")


        # ---- BAGIAN 2: BADGE INTERNAL/EXTERNAL ----
        # Badge ditaruh di ATAS gambar (overlay) pojok kiri atas

        # Mengambil nilai "jenis_event" dari dictionary
        # Nilainya "Internal" atau "External" sesuai Data Contract
        jenis = self.event_data.get("jenis_event", "")

        # Membuat label badge dengan self.poster_label sebagai parent
        # Ini yang membuat badge bisa ditaruh di atas gambar (overlay)
        self.badge_label = QLabel(jenis, self.poster_label)

        # Memberi nama objek untuk ditarget QSS
        self.badge_label.setObjectName("badge_label")

        # Mengatur font badge: Inter SemiBold ukuran 18 sesuai Figma
        font_badge = QFont("Inter SemiBold", 18)
        self.badge_label.setFont(font_badge)

        # Menyesuaikan lebar badge mengikuti panjang teksnya
        self.badge_label.adjustSize()

        # Mengunci tinggi badge menjadi 28 piksel
        self.badge_label.setFixedHeight(28)

        # Margin dalam badge: 8px kiri-kanan agar teks tidak mepet
        self.badge_label.setContentsMargins(8, 0, 8, 0)

        # Meratakan teks badge ke tengah
        self.badge_label.setAlignment(Qt.AlignCenter)

        # Memindahkan badge ke posisi x=8, y=8 dari pojok kiri atas gambar
        # Hasilnya badge menumpuk di atas gambar pojok kiri atas
        self.badge_label.move(8, 8)

        # Memastikan badge terlihat (ditampilkan di atas gambar)
        self.badge_label.show()

        # Menambahkan poster (beserta badge overlay) ke layout utama
        layout.addWidget(self.poster_label)


        # ---- BAGIAN 3 & 4: AREA TEKS BAWAH GAMBAR ----

        # Membuat widget kosong sebagai wadah teks nama dan deskripsi
        # Dipisah dari gambar agar margin bisa diatur berbeda
        text_widget = QWidget()

        # Memberi nama objek untuk ditarget QSS
        text_widget.setObjectName("text_widget")

        # Layout vertikal khusus untuk area teks
        text_layout = QVBoxLayout()

        # Jarak 4 piksel antara nama event dan deskripsi
        text_layout.setSpacing(4)

        # Margin area teks: kiri=12, atas=8, kanan=12, bawah=0
        # Memberi jarak agar teks tidak mepet ke tepi kartu
        text_layout.setContentsMargins(12, 8, 12, 0)


        # ---- NAMA EVENT ----

        # Mengambil nilai "nama_event" dari dictionary
        nama = self.event_data.get("nama_event", "")

        # Memotong nama jika lebih dari 25 karakter agar tampilan konsisten
        # Karakter ke-26 dst diganti "..." sebagai tanda ada teks yang dipotong
        if len(nama) > 25:
            nama = nama[:25] + "..."

        # Membuat label nama event
        self.nama_label = QLabel(nama)

        # Memberi nama objek untuk ditarget QSS
        self.nama_label.setObjectName("nama_label")

        # Mengatur font nama: Inter Medium ukuran 20 sesuai Figma
        font_nama = QFont("Inter Medium", 20)
        self.nama_label.setFont(font_nama)

        # Word wrap agar nama panjang tidak terpotong, turun ke baris berikutnya
        self.nama_label.setWordWrap(True)

        # Tinggi maksimal 60px agar semua kartu punya tinggi yang konsisten
        self.nama_label.setMaximumHeight(60)

        # Menambahkan nama event ke layout teks
        text_layout.addWidget(self.nama_label)


        # ---- DESKRIPSI SINGKAT ----

        # Mengambil nilai "deskripsi_singkat" dari dictionary
        # Maksimal 50-70 karakter sesuai Data Contract
        deskripsi = self.event_data.get("deskripsi_singkat", "")

        # Memotong deskripsi jika lebih dari 35 karakter
        if len(deskripsi) > 35:
            deskripsi = deskripsi[:35] + "..."

        # Membuat label deskripsi
        self.deskripsi_label = QLabel(deskripsi)

        # Memberi nama objek untuk ditarget QSS
        self.deskripsi_label.setObjectName("deskripsi_label")

        # Mengatur font deskripsi: Inter Regular ukuran 16 sesuai Figma
        font_deskripsi = QFont("Inter", 16)
        self.deskripsi_label.setFont(font_deskripsi)

        # Word wrap untuk deskripsi yang mungkin agak panjang
        self.deskripsi_label.setWordWrap(True)

        # Tinggi maksimal 50px agar konsisten antar kartu
        self.deskripsi_label.setMaximumHeight(50)

        # Menambahkan deskripsi ke layout teks
        text_layout.addWidget(self.deskripsi_label)

        # Menerapkan layout teks ke text_widget
        text_widget.setLayout(text_layout)

        # Menambahkan text_widget ke layout utama kartu
        # Posisinya di bawah gambar poster
        layout.addWidget(text_widget)

        # Menerapkan layout utama ke widget kartu ini
        self.setLayout(layout)

        # Mengunci lebar kartu sama dengan lebar gambar (220px)
        # Agar semua kartu punya lebar yang seragam
        self.setFixedWidth(220)


    # ----------------------------------------------------------
    # FUNGSI set_poster()
    # Dipanggil dari LUAR oleh worker_thread.py
    # setelah proses download gambar selesai
    #
    # Parameter:
    #   image_bytes = data gambar mentah dalam format bytes
    # ----------------------------------------------------------
    def set_poster(self, image_bytes):

        # Mengubah bytes biasa menjadi QByteArray
        # Format yang dibutuhkan PyQt5 untuk membaca data gambar
        byte_array = QByteArray(image_bytes)

        # Membuat objek QPixmap kosong sebagai wadah gambar
        pixmap = QPixmap()

        # Memuat data gambar dari QByteArray ke dalam pixmap
        # Mengembalikan True jika berhasil, False jika data rusak
        success = pixmap.loadFromData(byte_array)

        if success:
            # Hapus styling placeholder abu setelah gambar berhasil dimuat
            # Hanya sisakan border-radius agar sudut gambar tetap membulat
            self.poster_label.setStyleSheet("border-radius: 8px;")

            # Pasang gambar ke poster_label
            # Teks/warna placeholder akan hilang diganti gambar asli
            self.poster_label.setPixmap(pixmap)
        else:
            # Jika gambar gagal dimuat (URL rusak, bukan file gambar, dll)
            # Tampilkan teks pengganti agar user tahu ada masalah
            self.poster_label.setText("Gambar tidak tersedia")


    # ----------------------------------------------------------
    # FUNGSI mousePressEvent()
    # Override fungsi bawaan QWidget
    # Dipanggil OTOMATIS saat user mengklik kartu ini
    # ----------------------------------------------------------
    def mousePressEvent(self, event):

        # Memancarkan sinyal 'diklik' sambil membawa event_id kartu ini
        # main_window.py yang sudah connect() akan menerima event_id ini
        # dan membuka halaman detail event yang diklik
        self.diklik.emit(self.event_id)


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual menggunakan QSS (Qt Style Sheet)
    # QSS sintaksnya mirip CSS web
    # ----------------------------------------------------------
    def apply_style(self):

        # setStyleSheet() menerima string QSS
        # """ """ untuk string multi-baris di Python
        self.setStyleSheet("""

            /* Kartu utama: sudut membulat, border tipis */
            QWidget#event_card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }

            /* Saat mouse diarahkan ke kartu: border sedikit gelap */
            QWidget#event_card:hover {
                border: 1px solid #a0a0a0;
            }

            /* Area teks bawah gambar: transparan tanpa border */
            QWidget#text_widget {
                background: transparent;
                border: none;
            }

            /* Semua QLabel: transparan tanpa border sebagai default */
            QLabel {
                background: transparent;
                border: none;
            }

            /* Nama event: warna hitam, font diatur via QFont di setup_ui */
            QLabel#nama_label {
                color: #1a1a1a;
                border: none;
                background: transparent;
            }

            /* Deskripsi: warna abu-abu, font diatur via QFont di setup_ui */
            QLabel#deskripsi_label {
                color: #666666;
                border: none;
                background: transparent;
            }

            /* Badge Internal/External */
            /* Warna abu #828282 sesuai Figma, teks putih */
            /* Font diatur via QFont di setup_ui */
            QLabel#badge_label {
                color: white;
                background-color: #828282;
                border-radius: 4px;
                border: none;
                padding: 0px 4px;
            }
        """)
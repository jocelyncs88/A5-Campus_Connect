# ==============================================================
# FILE: card_widget.py
# TUGAS: Membuat blueprint/template untuk SATU kartu event
# yang akan ditampilkan berulang di homepage Campus Connect
# DIBUAT OLEH: UI/UX Component Builder 
# ==============================================================


# QWidget  = class dasar untuk semua komponen visual di PyQt5
#            Kita "mewarisi" ini agar EventCard bisa ditampilkan di layar
# QLabel   = komponen untuk menampilkan teks atau gambar
# QVBoxLayout = pengatur tata letak vertikal (elemen disusun dari atas ke bawah)
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

# QPixmap  = class khusus untuk menyimpan dan menampilkan data gambar
from PyQt5.QtGui import QPixmap

# QByteArray = format data bytes yang dimengerti oleh Qt/PyQt5
# pyqtSignal = cara membuat "tombol bel" untuk komunikasi antar komponen
from PyQt5.QtCore import QByteArray, pyqtSignal


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
    #   self       = referensi ke objek itu sendiri (wajib ada di setiap method)
    #   event_data = dictionary Python berisi semua info 1 event
    #                contoh: {"event_id": "001", "nama_event": "Sparta Festival", ...}
    #   parent     = komponen induk di PyQt5 (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, event_data, parent=None):

        # Wajib memanggil konstruktor QWidget terlebih dahulu
        # Ini menginisialisasi semua fitur bawaan QWidget ke objek ini
        # Tanpa baris ini, kartu tidak bisa ditampilkan di layar
        super().__init__(parent)

        # Menyimpan seluruh dictionary event_data sebagai atribut objek
        # Dengan self.event_data, dictionary ini bisa diakses
        # dari fungsi manapun di dalam class ini
        # Contoh akses: self.event_data.get("nama_event")
        self.event_data = event_data

        # Mengambil nilai event_id dari dictionary dan menyimpannya
        # sebagai atribut tersendiri agar mudah diakses saat kartu diklik
        # .get("event_id", "") artinya: ambil nilai key "event_id",
        # jika key tidak ditemukan, gunakan string kosong "" sebagai default
        self.event_id = event_data.get("event_id", "")

        # Memanggil fungsi setup_ui() untuk membangun semua elemen tampilan
        # Dipisah dari __init__ agar kode lebih terorganisir:
        # __init__ hanya mengurus inisialisasi, setup_ui mengurus tampilan
        self.setup_ui()

        # Memanggil fungsi apply_style() untuk mengatur gaya visual
        # Dipisah agar perubahan desain tidak mengganggu logika setup_ui
        self.apply_style()


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Bertugas membangun semua elemen visual di dalam kartu
    # Dipanggil sekali saat objek pertama kali dibuat
    #
    # Urutan elemen dari atas ke bawah:
    #   1. Gambar poster (placeholder dulu)
    #   2. Badge jenis event (Internal/External)
    #   3. Nama event (teks tebal)
    #   4. Deskripsi singkat (teks abu-abu)
    #   5. Tanggal waktu
    # ----------------------------------------------------------
    def setup_ui(self):

        # Membuat objek layout vertikal
        # Layout ini yang mengatur posisi semua elemen di dalam kartu
        # QVBoxLayout = Vertical Box Layout = elemen tersusun dari atas ke bawah
        layout = QVBoxLayout()

        # Mengatur jarak antara satu elemen dengan elemen berikutnya
        # Nilai 8 berarti ada jarak 8 piksel antar elemen
        layout.setSpacing(8)

        # Mengatur jarak antara isi kartu dengan tepi kartu (margin)
        # Format: setContentsMargins(kiri, atas, kanan, bawah)
        # Semua sisi diberi jarak 12 piksel agar isi tidak menempel ke tepi
        layout.setContentsMargins(12, 12, 12, 12)


        # ---- BAGIAN 1: GAMBAR POSTER ----

        # Membuat QLabel kosong sebagai "bingkai" untuk gambar poster
        # Teks "Memuat gambar..." tampil sebagai placeholder
        # sementara worker_thread.py belum selesai mendownload gambar aslinya
        self.poster_label = QLabel("Memuat gambar...")

        # Mengunci ukuran area gambar menjadi tepat 200x150 piksel
        # setFixedSize memastikan ukuran tidak berubah meskipun teks/gambar berbeda
        # self.poster_label agar bisa diakses dari fungsi set_poster() nanti
        self.poster_label.setFixedSize(200, 150)

        # Mengaktifkan fitur agar gambar otomatis menyesuaikan ukuran label
        # Tanpa ini, gambar berukuran besar akan meluap keluar bingkai
        self.poster_label.setScaledContents(True)

        # Menambahkan poster_label ke dalam layout
        # Setelah ini, poster akan muncul di posisi paling atas kartu
        layout.addWidget(self.poster_label)


        # ---- BAGIAN 2: BADGE JENIS EVENT ----

        # Mengambil nilai "jenis_event" dari dictionary event_data
        # Nilainya hanya 2 kemungkinan: "Internal" atau "External"
        # Jika key tidak ada di dictionary, gunakan string kosong
        jenis = self.event_data.get("jenis_event", "")

        # Membuat label dengan teks jenis event yang sudah diambil
        self.badge_label = QLabel(jenis)

        # Memberi nama objek "badge_label" agar bisa ditarget oleh QSS
        # di fungsi apply_style() — mirip seperti id="" di HTML
        self.badge_label.setObjectName("badge_label")

        # Menambahkan badge ke layout (muncul di bawah poster)
        layout.addWidget(self.badge_label)


        # ---- BAGIAN 3: NAMA EVENT ----

        # Mengambil nilai "nama_event" dari dictionary
        # Ini adalah judul utama acara yang tampil tebal di kartu
        nama = self.event_data.get("nama_event", "")

        # Membuat label dengan teks nama event
        self.nama_label = QLabel(nama)

        # Memberi nama objek untuk ditarget QSS (font tebal, ukuran lebih besar)
        self.nama_label.setObjectName("nama_label")

        # Mengaktifkan word wrap agar teks panjang tidak terpotong
        # melainkan dilanjutkan ke baris berikutnya secara otomatis
        self.nama_label.setWordWrap(True)

        # Menambahkan ke layout (muncul di bawah badge)
        layout.addWidget(self.nama_label)


        # ---- BAGIAN 4: DESKRIPSI SINGKAT ----

        # Mengambil nilai "deskripsi_singkat" dari dictionary
        # Maksimal 50-70 karakter
        # Jika data dari scraping tidak ada deskripsi_singkat,
        # ambil dari potongan awal deskripsi_lengkap (dilakukan di db_manager)
        deskripsi = self.event_data.get("deskripsi_singkat", "")

        # Membuat label deskripsi dengan teks yang sudah diambil
        self.deskripsi_label = QLabel(deskripsi)

        # Memberi nama objek untuk ditarget QSS (warna abu-abu, ukuran kecil)
        self.deskripsi_label.setObjectName("deskripsi_label")

        # Mengaktifkan word wrap untuk deskripsi yang mungkin lebih panjang
        self.deskripsi_label.setWordWrap(True)

        # Menambahkan ke layout (muncul di bawah nama event)
        layout.addWidget(self.deskripsi_label)


        # ---- BAGIAN 5: TANGGAL WAKTU ----

        # Mengambil nilai "tanggal_waktu" dari dictionary
        # Format ISO "YYYY-MM-DD HH:MM"
        tanggal = self.event_data.get("tanggal_waktu", "")

        # Membuat label tanggal (tidak perlu ObjectName karena styling default)
        self.tanggal_label = QLabel(tanggal)

        # Menambahkan ke layout (muncul paling bawah di dalam kartu)
        layout.addWidget(self.tanggal_label)


        # Menerapkan layout yang sudah berisi semua elemen ke widget kartu ini
        # Tanpa baris ini, semua addWidget() di atas tidak akan tampil
        self.setLayout(layout)


    # ----------------------------------------------------------
    # FUNGSI set_poster()
    # Dipanggil dari LUAR class ini, yaitu oleh worker_thread.py
    # setelah proses download gambar poster selesai
    #
    # Parameter:
    #   image_bytes = data gambar mentah dalam format bytes
    #                 (hasil dari response.content di worker_thread)
    #
    # Alasan dipisah dari setup_ui():
    #   Karena gambar tidak langsung tersedia saat kartu dibuat
    #   Download gambar butuh waktu, dilakukan di background oleh worker_thread
    # ----------------------------------------------------------
    def set_poster(self, image_bytes):

        # Mengubah bytes biasa menjadi QByteArray
        # Qt/PyQt5 membutuhkan format QByteArray, bukan bytes Python biasa
        # untuk bisa membaca data gambar
        byte_array = QByteArray(image_bytes)

        # Membuat objek QPixmap kosong sebagai wadah gambar
        # QPixmap adalah format gambar yang dioptimalkan untuk ditampilkan di layar
        pixmap = QPixmap()

        # Memuat data dari QByteArray ke dalam pixmap
        # loadFromData() mengembalikan True jika berhasil, False jika data rusak
        # Hasilnya disimpan di variabel success untuk pengecekan di bawah
        success = pixmap.loadFromData(byte_array)

        # Pengecekan apakah gambar berhasil dimuat
        if success:
            # Jika berhasil: pasang gambar ke poster_label
            # Teks placeholder "Memuat gambar..." akan hilang diganti gambar
            self.poster_label.setPixmap(pixmap)
        else:
            # Jika gagal (URL rusak, file bukan gambar, dll):
            # Tampilkan teks pengganti agar user tau ada masalah
            self.poster_label.setText("Gambar tidak tersedia")


    # ----------------------------------------------------------
    # FUNGSI mousePressEvent()
    # Ini adalah OVERRIDE dari fungsi bawaan QWidget
    #
    # Dipanggil OTOMATIS oleh PyQt5 setiap kali user mengklik widget ini
    # Tidak perlu memanggil fungsi ini secara manual
    #
    # Parameter:
    #   event = objek MouseEvent dari PyQt5 (berisi info klik: posisi, tombol, dll)
    #           tidak menggunakan isinya, tapi parameter ini wajib ada
    # ----------------------------------------------------------
    def mousePressEvent(self, event):

        # Memancarkan sinyal 'diklik' sambil membawa event_id kartu ini
        # .emit() = "menekan tombol bel" dan mengirimkan data
        #
        # Siapapun yang sudah connect() ke sinyal ini akan menerima event_id
        # Main_window.py yang akan membuka halaman detail
        # Contoh di main_window.py: kartu.diklik.connect(self.buka_detail)
        self.diklik.emit(self.event_id)


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual kartu menggunakan QSS (Qt Style Sheet)
    # QSS = versi CSS yang dipakai PyQt5, sintaksnya sangat mirip CSS web
    #
    # Dipisah dari setup_ui() agar:
    # - Perubahan desain tidak mengubah logika/struktur komponen
    # - Kode lebih mudah dibaca
    # - bisa mengubah warna/font tanpa menyentuh logika
    # ----------------------------------------------------------
    def apply_style(self):

        # setStyleSheet() menerima string berisi aturan QSS
        # Tanda """ """ untuk string multi-baris di Python
        self.setStyleSheet("""

            /* Gaya untuk widget kartu utama (seluruh area kartu) */
            /* Ini seperti CSS untuk <div> kartu di HTML */
            QWidget {
                background-color: white;   /* warna latar putih */
                border-radius: 12px;       /* sudut membulat 12px */
                border: 1px solid #e0e0e0; /* garis tepi abu-abu tipis */
            }

            /* Gaya saat mouse diarahkan ke atas kartu (hover effect) */
            /* Memberikan feedback visual ke user bahwa kartu bisa diklik */
            QWidget:hover {
                border: 1px solid #a0a0a0; /* garis tepi sedikit lebih gelap */
            }

            /* Gaya khusus untuk label nama event */
            /* QLabel#nama_label = targetkan QLabel dengan objectName "nama_label" */
            /* Mirip seperti CSS: label#nama_label { } */
            QLabel#nama_label {
                font-size: 13px;        /* ukuran font sedikit lebih besar */
                font-weight: bold;      /* teks tebal */
                color: #1a1a1a;         /* warna hampir hitam */
                border: none;           /* hapus border warisan dari QWidget di atas */
            }

            /* Gaya untuk label deskripsi singkat */
            QLabel#deskripsi_label {
                font-size: 11px;        /* font lebih kecil dari nama */
                color: #666666;         /* warna abu-abu untuk teks sekunder */
                border: none;
            }

            /* Gaya untuk badge jenis event (Internal/External) */
            QLabel#badge_label {
                font-size: 10px;           /* font kecil seperti badge/tag */
                color: white;              /* teks putih di atas background biru */
                background-color: #4a90d9; /* background biru */
                border-radius: 4px;        /* sudut sedikit membulat seperti pill */
                padding: 2px 6px;          /* jarak dalam badge: 2px atas-bawah, 6px kiri-kanan */
                border: none;
            }
        """)
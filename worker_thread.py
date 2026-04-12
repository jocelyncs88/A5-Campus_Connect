# ==============================================================
# FILE: worker_thread.py
# TUGAS: Mengelola semua operasi berat yang berjalan di background
#        agar tampilan UI tidak freeze saat proses sedang berjalan
# DIBUAT OLEH: UI/UX Component Builder 
# ISI FILE INI: 2 class thread
#   1. PosterDownloader = download gambar poster dari internet
#   2. ScraperThread    = menjalankan scraper.py di background
# ==============================================================


# QThread     = class dasar untuk membuat thread baru di PyQt5
#               Thread = jalur kerja terpisah dari UI utama
# pyqtSignal  = cara membuat "sinyal" untuk komunikasi antar thread
from PyQt5.QtCore import QThread, pyqtSignal

# requests = library Python untuk melakukan HTTP request ke internet
# Digunakan untuk mendownload gambar poster dari URL
# Perlu diinstall dulu: pip install requests
import requests


# ==============================================================
# Tugasnya: mendownload SATU gambar poster dari internet
# Mewarisi QThread sehingga proses download berjalan di background
#
# Tread terpisah karena download gambar bisa memakan waktu 
# beberapa detik.
# Jika dilakukan di main thread, UI akan freeze sampai selesai.
# ==============================================================
class PosterDownloader(QThread):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Sinyal dideklarasikan di level class, sebelum __init__
    # ----------------------------------------------------------

    # Sinyal yang dipancarkan saat download BERHASIL
    #   str   = event_id, untuk tahu kartu mana yang harus dipasangi gambar
    #   bytes = data gambar mentah hasil download (isi file gambarnya)
    finished = pyqtSignal(str, bytes)

    # Sinyal yang dipancarkan saat download GAGAL
    #   str = event_id, untuk tahu kartu mana yang gagal
    #   str = pesan error yang menjelaskan penyebab kegagalan
    error = pyqtSignal(str, str)


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil saat objek PosterDownloader baru dibuat
    #
    #   event_id = pengenal unik event (misal: "sparta_001")
    #              digunakan untuk tahu kartu mana yang diupdate
    #   url      = alamat internet gambar poster
    #              (misal: "https://example.com/poster.jpg")
    # ----------------------------------------------------------
    def __init__(self, event_id, url):

        # Wajib memanggil konstruktor QThread terlebih dahulu
        # Menginisialisasi semua fitur bawaan QThread ke objek ini
        super().__init__()

        # Menyimpan event_id sebagai atribut objek
        # Digunakan nanti di fungsi run() saat memancarkan sinyal
        self.event_id = event_id

        # Menyimpan URL gambar sebagai atribut objek
        # Digunakan nanti di fungsi run() saat melakukan request
        self.url = url


    # ----------------------------------------------------------
    # Fungsi WAJIB di setiap class yang mewarisi QThread
    # Isi fungsi ini yang berjalan di thread terpisah
    #
    # PENTING: Jangan panggil run() secara manual!
    # Untuk memulai thread, gunakan .start() dari luar
    # PyQt5 akan otomatis memanggil run() di thread baru
    # ----------------------------------------------------------
    def run(self):

        # try-except untuk menangkap error agar program tidak crash
        # Semua proses download dibungkus di sini
        try:

            # Melakukan HTTP GET request ke URL gambar
            # requests.get() = meminta data dari alamat internet
            # timeout=10 = berhenti paksa jika server tidak merespons
            #              dalam 10 detik (mencegah menunggu selamanya)
            response = requests.get(self.url, timeout=10)

            # Memeriksa apakah server merespons dengan status sukses
            # Kode sukses = 200, kode error = 404 (tidak ada), 500 (server error)
            # raise_for_status() akan memunculkan exception jika status error
            # sehingga langsung loncat ke blok except di bawah
            response.raise_for_status()

            # Jika sampai di sini berarti download berhasil
            # response.content = isi file gambar dalam format bytes
            # Disimpan ke variabel untuk dikirim lewat sinyal
            # finished.emit() = "menekan bel" tanda download selesai
            # sambil membawa event_id dan data gambar
            self.finished.emit(self.event_id, response.content)

        # Menangkap error khusus: koneksi terlalu lama
        # Terjadi jika server tidak merespons dalam 10 detik
        except requests.exceptions.Timeout:
            # Memancarkan sinyal error dengan pesan yang mudah dimengerti
            self.error.emit(self.event_id, "Timeout: koneksi lambat")

        # Menangkap error khusus: tidak bisa terhubung ke internet
        # Terjadi jika WiFi/internet mati atau URL tidak valid
        except requests.exceptions.ConnectionError:
            self.error.emit(self.event_id, "Tidak ada koneksi internet")

        # Menangkap semua jenis error lain yang tidak terduga
        # Exception as e = menyimpan detail error ke variabel e
        # str(e) = mengubah objek error menjadi teks yang bisa dibaca
        except Exception as e:
            self.error.emit(self.event_id, f"Error: {str(e)}")


# ==============================================================
# Tugasnya: menjalankan proses scraping website di background
# Mewarisi QThread sehingga proses scraping tidak membekukan UI
#
# Tread terpisah karna Scraping = mengambil data dari website, 
# bisa memakan waktu lama tergantung kecepatan internet dan 
# banyaknya data yang diambil
#  Tanpa thread, UI akan freeze total selama scraping berlangsung
# ==============================================================
class ScraperThread(QThread):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # ----------------------------------------------------------

    # Sinyal saat scraping BERHASIL selesai
    # List = daftar dictionary hasil scraping
    #        contoh: [{"nama_event": "...", "tanggal": "..."}, {...}]
    # Diterima oleh main_window.py untuk ditampilkan sebagai kartu-kartu
    selesai = pyqtSignal(list)

    # Sinyal untuk mengirim update status proses scraping
    # Bisa ditampilkan di UI sebagai teks "Sedang mengambil data..."
    # str = pesan status, contoh: "Menghubungi server..."
    progress = pyqtSignal(str)

    # Sinyal jika scraping GAGAL
    # str = pesan error penyebab kegagalan
    error = pyqtSignal(str)


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    #   scraper_func = fungsi dari scraper.py yang akan dijalankan
    #                  dikirim sebagai parameter agar ScraperThread
    # ----------------------------------------------------------
    def __init__(self, scraper_func):

        # Wajib memanggil konstruktor QThread
        super().__init__()

        # Menyimpan fungsi scraper sebagai atribut objek
        # Contoh penggunaan dari luar:
        #   from scraper import ambil_semua_event
        #   thread = ScraperThread(ambil_semua_event)
        self.scraper_func = scraper_func


    # ----------------------------------------------------------
    # FUNGSI run()
    # Berjalan di thread terpisah saat .start() dipanggil
    # Menjalankan fungsi scraper dan mengirim hasilnya ke main_window
    # ----------------------------------------------------------
    def run(self):

        # Membungkus semua proses dengan try-except
        try:

            # Memancarkan sinyal progress untuk update status di UI
            # main_window bisa menampilkan teks ini di label status
            self.progress.emit("Menghubungi server...")

            # Menjalankan fungsi scraper yang dikirim saat pembuatan objek
            # self.scraper_func() = memanggil fungsi tersebut
            # Fungsi scraper akan mengembalikan list of dictionary
            # contoh hasil: [{"nama_event": "Sparta", ...}, {...}]
            # Proses ini yang paling lama — bisa beberapa detik
            hasil = self.scraper_func()

            # Memancarkan progress lagi setelah scraping selesai
            self.progress.emit("Scraping selesai!")

            # Memancarkan sinyal selesai sambil membawa list hasil scraping
            # main_window.py yang menerima sinyal ini akan:
            #   1. Menyimpan data ke database lewat db_manager.py
            #   2. Membuat kartu-kartu EventCard dari data tersebut
            self.selesai.emit(hasil)

        # Menangkap semua jenis error yang mungkin terjadi saat scraping
        # Contoh: website target down, struktur HTML berubah, timeout, dll
        except Exception as e:
            # Memancarkan sinyal error dengan pesan detail
            # f"..." = f-string untuk menyisipkan variabel ke dalam teks
            # str(e) = mengubah objek error menjadi teks yang bisa dibaca
            self.error.emit(f"Scraping gagal: {str(e)}")
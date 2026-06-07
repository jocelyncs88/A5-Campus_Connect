# ==============================================================
# FILE: toggle_widget.py
# TUGAS: Membuat komponen tombol toggle ON/OFF
#        yang digunakan di halaman Settings
# DIBUAT OLEH: UI/UX Component Builder 
# ==============================================================


# QWidget     = class dasar untuk semua komponen visual di PyQt5
from PyQt5.QtWidgets import QWidget

# pyqtSignal      = cara membuat sinyal komunikasi antar komponen
# Qt              = berisi konstanta seperti Qt.NoPen
from PyQt5.QtCore import pyqtSignal, Qt

# QColor   = class untuk merepresentasikan warna
# QPainter = class untuk menggambar bentuk secara manual di widget
# QPen     = class untuk mengatur garis/outline gambar
# QBrush   = class untuk mengatur warna isi/fill gambar
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush


# ==============================================================
# CLASS ToggleSwitch
# Mewarisi QWidget artinya ToggleSwitch ADALAH komponen UI
# Komponen ini menggambar tombol toggle ON/OFF secara manual
# menggunakan QPainter — berbeda dengan tombol biasa (QPushButton)
# ==============================================================
class ToggleSwitch(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Sinyal ini dipancarkan setiap kali toggle diklik
    # Membawa nilai True (ON) atau False (OFF)
    # Diterima oleh setting_item_widget.py untuk tau status toggle
    # ----------------------------------------------------------
    toggled = pyqtSignal(bool)


    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek ToggleSwitch pertama kali dibuat
    #
    # Parameter:
    #   parent = komponen induk (default None = berdiri sendiri)
    # ----------------------------------------------------------
    def __init__(self, parent=None):

        # Wajib memanggil konstruktor QWidget terlebih dahulu
        # Menginisialisasi semua fitur bawaan QWidget ke objek ini
        super().__init__(parent)

        # Ukuran default toggle. Paint event dibuat dinamis,
        # jadi komponen ini tetap bisa diperbesar di halaman tertentu.
        self.setFixedSize(44, 24)

        # Menyimpan status toggle saat ini
        # False = OFF (default saat pertama dibuat)
        # True  = ON
        self._is_on = False


    # ----------------------------------------------------------
    # FUNGSI is_on()
    # Mengembalikan status toggle saat ini
    # Dipanggil dari luar untuk mengecek apakah toggle ON atau OFF
    #
    # Return:
    #   True  = toggle sedang ON
    #   False = toggle sedang OFF
    # ----------------------------------------------------------
    def is_on(self):

        # Mengembalikan nilai atribut _is_on
        return self._is_on


    # ----------------------------------------------------------
    # FUNGSI set_on()
    # Mengatur status toggle dari luar tanpa perlu diklik user
    # Dipanggil oleh setting_item_widget.py saat pertama dibuat
    # untuk menentukan status awal toggle (ON atau OFF)
    #
    # Parameter:
    #   value = True untuk ON, False untuk OFF
    # ----------------------------------------------------------
    def set_on(self, value):

        # Menyimpan nilai baru ke atribut _is_on
        self._is_on = value

        # Memaksa widget untuk menggambar ulang tampilannya
        # Tanpa ini tampilan toggle tidak akan berubah meski _is_on sudah berubah
        self.update()


    # ----------------------------------------------------------
    # FUNGSI mousePressEvent()
    # Override fungsi bawaan QWidget
    # Dipanggil OTOMATIS saat user mengklik toggle ini
    #
    # Parameter:
    #   event = objek MouseEvent dari PyQt5 (wajib ada tapi tidak dipakai)
    # ----------------------------------------------------------
    def mousePressEvent(self, event):

        # Membalik status toggle saat diklik
        # Kalau ON → jadi OFF, kalau OFF → jadi ON
        # "not" = membalik nilai boolean (True→False, False→True)
        self._is_on = not self._is_on

        # Memancarkan sinyal toggled sambil membawa status terbaru dari user
        # setting_item_widget.py yang menerima sinyal ini akan
        # meneruskannya ke main_window.py
        self.toggled.emit(self._is_on)

        # Memaksa widget menggambar ulang dengan status yang baru
        self.update()


    # ----------------------------------------------------------
    # FUNGSI paintEvent()
    # Override fungsi bawaan QWidget
    # Dipanggil OTOMATIS oleh PyQt5 setiap kali widget perlu digambar
    # atau digambar ulang (setelah update() dipanggil)
    #
    # Disini tampilan toggle digambar secara manual
    # menggunakan QPainter bukan pake QSS seperti biasanya
    #
    # Parameter:
    #   event = objek PaintEvent dari PyQt5 (wajib ada tapi tidak dipakai)
    # ----------------------------------------------------------
    def paintEvent(self, event):

        # QPainter(self) = "aku mau menggambar di widget ini"
        painter = QPainter(self)

        # Mengaktifkan Antialiasing agar tepi gambar terlihat halus
        # Tanpa ini tepi lingkaran dan sudut membulat akan terlihat kasar/bergerigi
        painter.setRenderHint(QPainter.Antialiasing)


        # ---- GAMBAR BACKGROUND TOGGLE ----

        # Menentukan warna background berdasarkan status toggle
        if self._is_on:
            # Toggle ON → warna teal gelap 
            painter.setBrush(QBrush(QColor("#2D6A6A")))
        else:
            # Toggle OFF → warna abu 
            painter.setBrush(QBrush(QColor("#888780")))

        # Menghilangkan garis tepi/outline background toggle
        # Qt.NoPen = tidak ada garis tepi sama sekali
        painter.setPen(Qt.NoPen)

        # Menggambar persegi panjang dengan sudut membulat sebagai background.
        # Ukuran mengikuti ukuran widget agar toggle bisa diperbesar
        # tanpa mengubah class lain.
        w = self.width()
        h = self.height()
        radius = h / 2
        painter.drawRoundedRect(0, 0, w, h, radius, radius)


        # ---- GAMBAR LINGKARAN PUTIH ----

        # Mengatur warna knob menjadi putih
        painter.setBrush(QBrush(QColor("white")))

        margin = max(2, int(h * 0.10))
        knob = h - (margin * 2)
        y = margin
        x = w - knob - margin if self._is_on else margin
        painter.drawEllipse(x, y, knob, knob)
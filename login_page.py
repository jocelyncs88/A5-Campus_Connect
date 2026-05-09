# ==============================================================
# FILE: login_page.py
# TUGAS: Membuat halaman login untuk Event Organizer
# DIBUAT OLEH: UI/UX Component Builder 
# ==============================================================


# QWidget      = class dasar untuk semua komponen visual
# QVBoxLayout  = layout vertikal (atas ke bawah)
# QHBoxLayout  = layout horizontal (kiri ke kanan)
# QLabel       = komponen teks
# QLineEdit    = input teks satu baris
# QPushButton  = tombol yang bisa diklik
# QFrame       = komponen garis pemisah
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton,
                              QFrame, QSizePolicy,
                              QGraphicsDropShadowEffect)

# Qt         = konstanta PyQt5
# pyqtSignal = sinyal komunikasi antar komponen
# QUrl       = untuk membuka link
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QUrl

# QFont  = class untuk mengatur font
# QDesktopServices = untuk membuka aplikasi eksternal (WhatsApp)
from PyQt5.QtGui import QFont, QDesktopServices, QPixmap, QIcon, QColor

import os


# ==============================================================
# CLASS LoginPage
# Mewarisi QWidget artinya LoginPage ADALAH halaman UI
# Berisi form login untuk Event Organizer
# ==============================================================
class LoginPage(QWidget):

    # ----------------------------------------------------------
    # DEKLARASI SINYAL
    # Dipancarkan saat user klik tombol "Continue"
    # Membawa email dan password yang diinput user
    # Penerima sinyal (main_window.py) yang mengecek ke database
    # ----------------------------------------------------------
    login_diklik = pyqtSignal(str, str)  # email, password
    kembali_diklik = pyqtSignal()

    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil OTOMATIS saat objek LoginPage pertama kali dibuat
    # ----------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("login_page")

        # Menyimpan status apakah password sedang terlihat atau tidak
        # False = tersembunyi (default), True = terlihat
        self.password_visible = False

        self.setup_ui()
        self.apply_style()

        # Menambahkan efek shadow pada card
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(24)
        self.card.setGraphicsEffect(shadow)


    # ----------------------------------------------------------
    # FUNGSI setup_ui()
    # Membangun tampilan halaman login
    # ----------------------------------------------------------
    def setup_ui(self):

        # Outer layout untuk menengahkan konten ke tengah layar
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.setAlignment(Qt.AlignCenter)

        # Card putih yang membungkus semua konten login
        self.card = QWidget()
        self.card.setObjectName("login_card")
        self.card.setFixedWidth(420)

        # Inner layout untuk konten login
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 36, 32, 36)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignCenter)

        # ---- JUDUL "Login" ----

        self.judul_label = QLabel("Login")
        self.judul_label.setObjectName("judul_label")
        self.judul_label.setAlignment(Qt.AlignCenter)

        font_judul = QFont("Inter Bold", 32)
        font_judul.setWeight(QFont.Bold)
        self.judul_label.setFont(font_judul)

        main_layout.addWidget(self.judul_label)
        main_layout.addSpacing(12)


        # ---- TEKS "Do you already have an account..." ----

        self.teks_akun = QLabel("Do you already have an account for Event Organizer?")
        self.teks_akun.setObjectName("teks_akun")
        self.teks_akun.setAlignment(Qt.AlignCenter)
        self.teks_akun.setWordWrap(True)

        font_akun = QFont("Inter SemiBold", 14)
        font_akun.setWeight(QFont.DemiBold)
        self.teks_akun.setFont(font_akun)

        main_layout.addWidget(self.teks_akun)
        main_layout.addSpacing(6)


        # ---- TEKS "Enter your email to continue" ----

        self.teks_sub = QLabel("Enter your email to continue")
        self.teks_sub.setObjectName("teks_sub")
        self.teks_sub.setAlignment(Qt.AlignCenter)

        font_sub = QFont("Inter", 12)
        font_sub.setWeight(QFont.Normal)
        self.teks_sub.setFont(font_sub)

        main_layout.addWidget(self.teks_sub)
        main_layout.addSpacing(28)


        # ---- FORM INPUT (email + password + tombol) ----

        font_input = QFont("Inter", 14)
        font_input.setWeight(QFont.Normal)

        font_label = QFont("Inter SemiBold", 11)
        font_label.setWeight(QFont.DemiBold)

        font_btn = QFont("Inter Medium", 14)
        font_btn.setWeight(QFont.Medium)


        # ---- LABEL EMAIL + ICON DARI ASSETS ----

        # Layout horizontal untuk icon + teks "Email"
        email_label_layout = QHBoxLayout()
        email_label_layout.setSpacing(6)
        email_label_layout.setContentsMargins(0, 0, 0, 0)

        # Icon email dari file assets/email.png
        icon_email = QLabel()
        email_icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "email.png"
        )
        if os.path.exists(email_icon_path):
            icon_email.setPixmap(
                QPixmap(email_icon_path).scaled(
                    16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        else:
            icon_email.setText("✉")

        # Teks "Email"
        teks_email = QLabel("Email")
        teks_email.setObjectName("label_field")
        teks_email.setFont(font_label)

        email_label_layout.addWidget(icon_email)
        email_label_layout.addWidget(teks_email)
        email_label_layout.addStretch()

        main_layout.addLayout(email_label_layout)
        main_layout.addSpacing(6)


        # ---- INPUT EMAIL ----

        self.input_email = QLineEdit()
        self.input_email.setObjectName("input_field")
        self.input_email.setPlaceholderText("email@domain.com")
        self.input_email.setFixedHeight(48)
        self.input_email.setFont(font_input)
        main_layout.addWidget(self.input_email)
        main_layout.addSpacing(16)


        # ---- LABEL PASSWORD + ICON ----

        self.label_password = QLabel("🔒  Password")
        self.label_password.setObjectName("label_field")
        self.label_password.setFont(font_label)
        main_layout.addWidget(self.label_password)
        main_layout.addSpacing(6)


        # ---- INPUT PASSWORD + TOMBOL MATA ----

        # Widget container untuk input password dan tombol mata
        password_widget = QWidget()
        password_widget.setObjectName("password_widget")

        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        # Input password
        self.input_password = QLineEdit()
        self.input_password.setObjectName("input_password")
        self.input_password.setPlaceholderText("Password")
        self.input_password.setFixedHeight(48)
        self.input_password.setFont(font_input)

        # Menyembunyikan teks password dengan titik-titik
        self.input_password.setEchoMode(QLineEdit.Password)

        # Tombol mata untuk show/hide password
        self.btn_mata = QPushButton()
        self.btn_mata.setIcon(QIcon("assets/eye_outline.png"))
        self.btn_mata.setIconSize(QSize(20, 20))
        self.btn_mata.setObjectName("btn_mata")
        self.btn_mata.setFixedSize(48, 48)
        self.btn_mata.setCursor(Qt.PointingHandCursor)

        # Saat diklik → toggle show/hide password
        self.btn_mata.clicked.connect(self.toggle_password)

        password_layout.addWidget(self.input_password)
        password_layout.addWidget(self.btn_mata)
        password_widget.setLayout(password_layout)
        main_layout.addWidget(password_widget)
        main_layout.addSpacing(6)


        # ---- TEKS "Forgot password?" ----

        self.teks_lupa = QLabel("Forgot password?")
        self.teks_lupa.setObjectName("teks_lupa")
        self.teks_lupa.setAlignment(Qt.AlignRight)
        self.teks_lupa.setCursor(Qt.PointingHandCursor)
        font_lupa = QFont("Inter", 12)
        font_lupa.setWeight(QFont.Normal)
        self.teks_lupa.setFont(font_lupa)
        main_layout.addWidget(self.teks_lupa)
        main_layout.addSpacing(20)


        # ---- TOMBOL CONTINUE ----

        self.btn_continue = QPushButton("Continue")
        self.btn_continue.setObjectName("btn_continue")
        self.btn_continue.setFixedHeight(48)
        self.btn_continue.setCursor(Qt.PointingHandCursor)
        self.btn_continue.setFont(font_btn)

        # Saat diklik → jalankan fungsi on_continue_diklik
        self.btn_continue.clicked.connect(self.on_continue_diklik)
        main_layout.addWidget(self.btn_continue)
        main_layout.addSpacing(10)


        # ---- TOMBOL KEMBALI KE HOMEPAGE ----

        self.btn_kembali = QPushButton("← Kembali ke Homepage")
        self.btn_kembali.setObjectName("btn_kembali")
        self.btn_kembali.setFixedHeight(48)
        self.btn_kembali.setCursor(Qt.PointingHandCursor)
        self.btn_kembali.setFont(font_btn)

        # Saat diklik → sinyal untuk kembali ke homepage
        self.btn_kembali.clicked.connect(self.on_kembali_diklik)
        main_layout.addWidget(self.btn_kembali)
        main_layout.addSpacing(20)


        # ---- GARIS + TEKS "Don't have an account yet?" ----

        garis_layout = QHBoxLayout()
        garis_layout.setSpacing(8)

        # Garis kiri
        garis_kiri = QFrame()
        garis_kiri.setFrameShape(QFrame.HLine)
        garis_kiri.setObjectName("garis_pemisah")

        # Teks di tengah garis
        self.teks_belum_akun = QLabel("Don't have an account yet?")
        self.teks_belum_akun.setObjectName("teks_belum_akun")
        self.teks_belum_akun.setAlignment(Qt.AlignCenter)

        font_belum = QFont("Inter", 11)
        font_belum.setWeight(QFont.Normal)
        self.teks_belum_akun.setFont(font_belum)

        # Garis kanan
        garis_kanan = QFrame()
        garis_kanan.setFrameShape(QFrame.HLine)
        garis_kanan.setObjectName("garis_pemisah")

        garis_layout.addWidget(garis_kiri)
        garis_layout.addWidget(self.teks_belum_akun)
        garis_layout.addWidget(garis_kanan)
        main_layout.addLayout(garis_layout)
        main_layout.addSpacing(12)


        # ---- TOMBOL CONTACT US (WhatsApp) ----

        self.btn_contact = QPushButton()
        self.btn_contact.setObjectName("btn_contact")
        self.btn_contact.setFixedHeight(48)
        self.btn_contact.setCursor(Qt.PointingHandCursor)
        self.btn_contact.setFont(font_btn)

        # Cek apakah icon WhatsApp tersedia di folder assets
        wa_icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "whatsapp.png"
        )
        if os.path.exists(wa_icon_path):
            self.btn_contact.setIcon(QIcon(wa_icon_path))
            self.btn_contact.setText("  Contact us")
        else:
            self.btn_contact.setText("📱  Contact us")

        # Saat diklik → buka WhatsApp
        self.btn_contact.clicked.connect(self.buka_whatsapp)
        main_layout.addWidget(self.btn_contact)
        main_layout.addSpacing(10)


        # ---- TEKS "Contact admin to register..." ----

        self.teks_admin = QLabel("Contact admin to register as an Event Organizer")
        self.teks_admin.setObjectName("teks_admin")
        self.teks_admin.setAlignment(Qt.AlignCenter)

        # WordWrap agar teks tidak terpotong
        self.teks_admin.setWordWrap(True)

        font_admin = QFont("Inter", 11)
        font_admin.setWeight(QFont.Normal)
        self.teks_admin.setFont(font_admin)

        main_layout.addWidget(self.teks_admin)

        # Terapkan layout ke card
        self.card.setLayout(main_layout)

        # Tambahkan card ke outer layout
        outer_layout.addWidget(self.card)
        self.setLayout(outer_layout)


    # ----------------------------------------------------------
    # FUNGSI toggle_password()
    # Dipanggil saat user klik tombol mata
    # Menampilkan atau menyembunyikan teks password
    # ----------------------------------------------------------
    def toggle_password(self):
        if self.password_visible:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_mata.setIcon(QIcon("assets/eye_outline.png"))
            self.password_visible = False
        else:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_mata.setIcon(QIcon("assets/eye_filled.png"))
            self.password_visible = True


    # ----------------------------------------------------------
    # FUNGSI on_continue_diklik()
    # Dipanggil saat user klik tombol "Continue"
    # Mengambil email dan password lalu memancarkan sinyal
    # ----------------------------------------------------------
    def on_continue_diklik(self):

        # Mengambil teks dari input email dan password
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()

        # Validasi sederhana: tidak boleh kosong
        if not email or not password:
            return

        # Memancarkan sinyal ke main_window.py
        self.login_diklik.emit(email, password)


    # ----------------------------------------------------------
    # FUNGSI on_kembali_diklik()
    # Dipanggil saat user klik tombol "Kembali ke Homepage"
    # ----------------------------------------------------------
    def on_kembali_diklik(self):
        self.kembali_diklik.emit()


    # ----------------------------------------------------------
    # FUNGSI buka_whatsapp()
    # Dipanggil saat user klik tombol "Contact us"
    # Membuka WhatsApp dengan nomor admin
    # ----------------------------------------------------------
    def buka_whatsapp(self):

        # Nomor WhatsApp dalam format internasional
        # 62 = kode negara Indonesia
        nomor = "6289663143826"

        # Membuka WhatsApp via link resmi wa.me
        url = QUrl(f"https://wa.me/{nomor}")
        QDesktopServices.openUrl(url)


    # ----------------------------------------------------------
    # FUNGSI apply_style()
    # Mengatur tampilan visual
    # ----------------------------------------------------------
    def apply_style(self):

        self.setStyleSheet("""

            /* Halaman login: background transparan */
            QWidget#login_page {
                background-color: transparent;
            }

            /* Card putih */
            QWidget#login_card {
                background-color: white;
                border-radius: 20px;
                border: none;
            }

            /* Judul Login */
            QLabel#judul_label {
                color: #516465;
                font-size: 32px;
            }

            /* Teks "Do you already..." */
            QLabel#teks_akun {
                color: #516465;
                font-size: 14px;
            }

            /* Teks "Enter your email to continue" */
            QLabel#teks_sub {
                color: #5D6B6B;
                font-size: 12px;
            }

            /* Label Email dan Password */
            QLabel#label_field {
                color: #5F5E5A;
                font-size: 12px;
            }

            /* Input email */
            QLineEdit#input_field {
                background-color: white;
                border: 1px solid #CBD5E0;
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1a1a1a;
            }

            QLineEdit#input_field:focus {
                border: 1.5px solid #2D6A6A;
            }

            /* Input password */
            QLineEdit#input_password {
                background-color: white;
                border: 1.5px solid #CBD5E0;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-right: none;
                padding: 10px 14px;
                font-size: 14px;
                color: #1a1a1a;
            }

            QLineEdit#input_password:focus {
                border: 1.5px solid #2D6A6A;
                border-right: none;
            }

            /* Tombol mata show/hide password */
            QPushButton#btn_mata {
                background-color: white;
                border: 1px solid #CBD5E0;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-left: none;
                color: #888780;
            }

            QPushButton#btn_mata:hover {
                background-color: #D2E6E5;
            }

            /* Teks Forgot password? */
            QLabel#teks_lupa {
                color: #2D6A6A;
                font-size: 12px;
            }

            /* Tombol Continue */
            QPushButton#btn_continue {
                background-color: #2D6A6A;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
            }

            QPushButton#btn_continue:hover {
                background-color: #3a7a7a;
            }

            QPushButton#btn_continue:pressed {
                background-color: #1a5a5a;
            }

            /* Tombol Kembali ke Homepage */
            QPushButton#btn_kembali {
                background-color: transparent;
                color: #5D6B6B;
                border: 1.5px solid #CBD5E0;
                border-radius: 10px;
                font-size: 14px;
            }

            QPushButton#btn_kembali:hover {
                background-color: #D2E6E5;
            }

            /* Garis pemisah */
            QFrame#garis_pemisah {
                color: #CBD5E0;
            }

            /* Teks "Don't have an account yet?" */
            QLabel#teks_belum_akun {
                color: #5D6B6B;
                font-size: 12px;
            }

            /* Tombol Contact us */
            QPushButton#btn_contact {
                background-color: #2D6A6A;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
            }

            QPushButton#btn_contact:hover {
                background-color: #3a7a7a;
            }

            QPushButton#btn_contact:pressed {
                background-color: #1a5a5a;
            }

            /* Teks "Contact admin..." */
            QLabel#teks_admin {
                color: #5D6B6B;
                font-size: 12px;
            }
        """)
# ==============================================================
# FILE: settings/account_window.py
# TUGAS: Membangun panel "Account Settings" beserta sub-panel
#        edit untuk setiap field (Name, Bio, Email, Contact)
# BAGIAN DARI: Halaman Settings Campus Connect
# DIBUAT OLEH: UI/UX Designer (fitur-Settings)
#
# CARA PAKAI dari settings_window.py:
#   from settings.account_window import AccountPanel
#   panel = AccountPanel(user_data=user_data, stacked_widget=self.stacked_widget)
#   stacked_widget.addWidget(panel)  # masuk ke index 0
# ==============================================================

import sys
import os

# Tambahkan folder root (parent dari folder settings/) ke sys.path
# agar Python bisa menemukan toggle_widget dan setting_item_widget
# yang berada di root project, bukan di dalam folder settings/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# ==============================================================
# KONSTANTA WARNA
# Disalin dari main_window.py agar tampilan konsisten
# di seluruh aplikasi Campus Connect
#
# CATATAN: Jika tim sepakat membuat constants.py di root,
# konstanta ini bisa diimport dari sana dan dihapus dari sini
# ==============================================================
COLOR_GRAY_LIGHT   = "#D2E6E5"   # Warna background input dan elemen panel kiri
COLOR_TEAL_DARK    = "#516465"   # Warna teks gelap dan avatar
COLOR_TEXT_PRIMARY = "#5D6B6B"   # Warna teks utama (abu kehijauan)
COLOR_TEXT_MUTED   = "#9AABAB"   # Warna teks sekunder / placeholder
COLOR_DIVIDER      = "#D2E6E5"   # Warna garis pembatas antar baris


# ==============================================================
# KONSTANTA ROLE USER
# Disalin dari settings_window.py agar logika role bisa dipakai
# di dalam panel ini tanpa harus import dari file lain
# ==============================================================
ROLE_ORGANIZER = "organizer"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"


# ==============================================================
# CLASS AccountPanel
# Mewarisi QWidget (bukan QDialog) karena panel ini adalah
# komponen yang dimasukkan ke dalam QStackedWidget milik
# settings_window.py — bukan jendela mandiri
#
# Bertanggung jawab atas:
#   - Tampilan utama Account Settings (foto, name, bio, email, contact)
#   - Sub-panel edit untuk setiap field (buka_panel_edit)
#   - Menyimpan perubahan ke user_data dan refresh tampilan
# ==============================================================
class AccountPanel(QWidget):

    # ----------------------------------------------------------
    # FUNGSI __init__ (Konstruktor)
    # Dipanggil saat settings_window.py membuat panel Account
    #
    # Parameter:
    #   user_data      = dictionary data user yang sedang login
    #                    contoh: {
    #                       "nama": "Event Organizer",
    #                       "bio": "Music Festival",
    #                       "email": "eventorganizer@gmail.com",
    #                       "kontak": "+6281-3456-7898",
    #                       "role": "organizer",
    #                       "inisial": "EO"
    #                    }
    #   stacked_widget = referensi ke QStackedWidget milik settings_window.py
    #                    diperlukan agar panel ini bisa menambah/menghapus
    #                    sub-panel edit dari stacked_widget
    #   parent         = komponen induk (default None)
    # ----------------------------------------------------------
    def __init__(self, user_data=None, stacked_widget=None, parent=None):
        super().__init__(parent)

        # Menyimpan data user agar bisa diakses semua fungsi di class ini
        # Fallback ke data kosong jika tidak ada data yang dikirim
        self.user_data = user_data or {
            "nama"   : "",
            "bio"    : "",
            "email"  : "",
            "kontak" : "",
            "role"   : ROLE_UMUM,
            "inisial": ""
        }

        # Mengambil role untuk keperluan logika pesan per field
        # (Email dan Contact punya teks keterangan berbeda per role)
        self.role = self.user_data.get("role", ROLE_UMUM)

        # Menyimpan referensi ke stacked_widget milik settings_window.py
        # Digunakan oleh buka_panel_edit() dan tutup_panel_edit()
        # untuk menambah/menghapus sub-panel edit
        self.stacked_widget = stacked_widget

        # Referensi ke sub-panel edit yang sedang aktif
        # Digunakan tutup_panel_edit() untuk menghapusnya dari stacked_widget
        self.panel_edit_aktif = None

        # Background transparan agar gradient dari settings_window.py terlihat
        self.setStyleSheet("background: transparent;")

        # Membangun tampilan utama Account Settings
        self._render_account()


    # ----------------------------------------------------------
    # FUNGSI _render_account()
    # Membangun tampilan utama panel Account Settings:
    #   - Judul "Account Settings"
    #   - Sub-judul "Basic info"
    #   - Baris foto profil
    #   - Baris Name, Bio, Email, Contact
    #
    # Dipisah dari __init__ agar bisa dipanggil ulang oleh
    # simpan_edit() untuk me-refresh tampilan setelah data berubah
    # ----------------------------------------------------------
    def _render_account(self):

        # Hapus layout lama jika ada (untuk keperluan refresh setelah simpan)
        # Ini mencegah widget lama menumpuk saat _render_account dipanggil ulang
        if self.layout():
            # Hapus semua widget di layout lama sebelum membuat yang baru
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(0)

        # ---- Judul halaman ----
        lbl_judul = QLabel("Account Settings")
        lbl_judul.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLOR_TEXT_PRIMARY};
            margin-bottom: 24px;
        """)
        layout.addWidget(lbl_judul)
        layout.addSpacing(20)

        # ---- Sub-judul "Basic info" ----
        lbl_basic = QLabel("Basic info")
        lbl_basic.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLOR_TEXT_PRIMARY};
            margin-bottom: 12px;
        """)
        layout.addWidget(lbl_basic)
        layout.addSpacing(10)

        # ---- Garis pembatas atas ----
        layout.addWidget(self._buat_divider())

        # ---- Baris Profile Picture ----
        layout.addWidget(self._buat_baris_foto())
        layout.addWidget(self._buat_divider())

        # ---- Baris-baris info ----
        # Jika field kosong, tampilkan teks placeholder abu-abu
        # agar user tahu field tersebut bisa diisi
        fields = [
            ("Name",    self.user_data.get("nama")   or "add name"),
            ("Bio",     self.user_data.get("bio")    or "add bio"),
            ("Email",   self.user_data.get("email")  or "add email"),
            ("Contact", self.user_data.get("kontak") or "add contact"),
        ]

        for field_label, field_value in fields:
            layout.addWidget(self._buat_baris_info(field_label, field_value))
            layout.addWidget(self._buat_divider())

        layout.addStretch()


    # ----------------------------------------------------------
    # FUNGSI _buat_baris_foto()
    # Membangun baris foto profil:
    #   kiri   = label "Profile picture"
    #   tengah = avatar lingkaran berisi inisial
    #   kanan  = tombol "Upload new picture" + "Remove"
    #
    # Return: QWidget baris siap pakai
    # ----------------------------------------------------------
    def _buat_baris_foto(self):
        baris = QWidget()
        baris.setStyleSheet("background: transparent;")
        baris.setFixedHeight(80)

        layout = QHBoxLayout(baris)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label nama field di kiri
        lbl_field = QLabel("Profile picture")
        lbl_field.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_field.setFixedWidth(220)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Avatar lingkaran berisi inisial user
        # Jika belum ada inisial, tampilkan "add photo" sebagai petunjuk
        inisial = self.user_data.get("inisial", "")
        avatar = QLabel(inisial if inisial else "add\nphoto")
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {COLOR_TEAL_DARK};
            color: white;
            font-weight: bold;
            font-size: {"13px" if inisial else "8px"};
            border-radius: 24px;
        """)

        # Kolom kanan: Upload dan Remove
        action_col = QWidget()
        action_col.setStyleSheet("background: transparent;")
        action_layout = QVBoxLayout(action_col)
        action_layout.setContentsMargins(12, 0, 0, 0)
        action_layout.setSpacing(2)

        btn_upload = QLabel("Upload new picture")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px;")

        # Warna merah untuk aksi yang bersifat destruktif
        btn_remove = QLabel("Remove")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setStyleSheet("color: #E05C5C; font-size: 12px;")

        action_layout.addWidget(btn_upload)
        action_layout.addWidget(btn_remove)

        layout.addWidget(lbl_field)
        layout.addSpacerItem(spacer)
        layout.addWidget(avatar)
        layout.addWidget(action_col)

        return baris


    # ----------------------------------------------------------
    # FUNGSI _buat_baris_info()
    # Template untuk satu baris info yang bisa diklik untuk edit
    # Isi (kiri ke kanan): nama field | nilai | tombol panah
    #
    # Parameter:
    #   field_label = nama field, contoh: "Name", "Email"
    #   field_value = nilai saat ini atau placeholder "add name"
    #
    # Return: QWidget baris siap pakai
    # ----------------------------------------------------------
    def _buat_baris_info(self, field_label, field_value):
        baris = QWidget()
        baris.setStyleSheet("background: transparent;")
        baris.setFixedHeight(56)
        baris.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(baris)
        layout.setContentsMargins(0, 0, 0, 0)

        # Nama field di kiri (warna muted)
        lbl_field = QLabel(field_label)
        lbl_field.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        lbl_field.setFixedWidth(220)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Nilai field di kanan
        # Jika masih placeholder ("add name" dll), tampilkan dengan warna muted
        # Jika sudah diisi user, tampilkan dengan warna primary
        is_placeholder = field_value.startswith("add ")
        lbl_value = QLabel(field_value)
        lbl_value.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED if is_placeholder else COLOR_TEXT_PRIMARY}; font-size: 13px;"
        )
        lbl_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Tombol panah — menggunakan default argument di lambda
        # untuk menghindari closure issue (semua tombol memanggil field yang sama)
        btn_arrow = QPushButton()
        btn_arrow.setIcon(QIcon("assets/next.png"))
        btn_arrow.setIconSize(QSize(16, 16))
        btn_arrow.setCursor(Qt.PointingHandCursor)
        btn_arrow.setStyleSheet("background: transparent; border: none;")
        btn_arrow.clicked.connect(
            lambda checked, f=field_label: self.buka_panel_edit(f)
        )

        layout.addWidget(lbl_field)
        layout.addSpacerItem(spacer)
        layout.addWidget(lbl_value)
        layout.addWidget(btn_arrow)

        return baris


    # ----------------------------------------------------------
    # FUNGSI _buat_divider()
    # Membuat garis tipis horizontal sebagai pemisah antar baris
    #
    # Return: QFrame siap pakai
    # ----------------------------------------------------------
    def _buat_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(
            f"color: {COLOR_DIVIDER}; background-color: {COLOR_DIVIDER};"
        )
        line.setFixedHeight(1)
        return line


    # ==========================================================
    # ---- SUB-PANEL EDIT ----
    # Ditampilkan saat user mengklik tombol panah di baris info
    # Dimasukkan ke stacked_widget sebagai halaman baru (bukan popup)
    # ==========================================================


    # ----------------------------------------------------------
    # FUNGSI buka_panel_edit()
    # Membuat sub-panel edit untuk field tertentu dan menampilkannya
    # di stacked_widget menggantikan panel Account sementara
    #
    # Perbedaan tampilan per field:
    #   Name    → QLineEdit, batas 30 karakter (soft: warning merah)
    #   Bio     → QTextEdit kotak besar, batas 160 karakter (hard: ditolak)
    #   Email   → QLineEdit, tanpa batas, pesan berbeda per role
    #   Contact → QLineEdit + prefix "+62 |", tanpa batas, pesan berbeda per role
    #
    # Parameter:
    #   field = nama field yang akan diedit ("Name", "Bio", "Email", "Contact")
    # ----------------------------------------------------------
    def buka_panel_edit(self, field):

        panel_edit = QWidget()
        panel_edit.setStyleSheet("background: transparent;")

        # Layout utama: konten di atas, bottom bar (Cancel/Save) di bawah
        root = QVBoxLayout(panel_edit)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- AREA KONTEN ATAS ----
        konten = QWidget()
        konten.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(konten)
        layout.setContentsMargins(50, 40, 50, 20)
        layout.setSpacing(12)

        # Judul sub-panel berbeda dari nama field untuk Email dan Contact
        # agar lebih deskriptif dan sesuai mockup Figma
        judul_map = {
            "Name"   : "Name",
            "Bio"    : "Bio",
            "Email"  : "Add an email",
            "Contact": "Add phone",
        }
        lbl_judul = QLabel(judul_map.get(field, field))
        lbl_judul.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLOR_TEXT_PRIMARY};
        """)
        layout.addWidget(lbl_judul)

        # ---- TEKS KETERANGAN ----
        # Email dan Contact: berbeda per role (EO vs mahasiswa/umum)
        # Name dan Bio: sama untuk semua role
        if field == "Email":
            if self.role == ROLE_ORGANIZER:
                teks_ket = ("Enter a professional email address for audiences to send "
                            "formal inquiries and event booking requests. Make sure this "
                            "email is active so you don't miss formal inquiries and "
                            "booking requests.")
            else:
                teks_ket = ("Enter your email address to receive important notifications, "
                            "e-tickets, and updates from event organizers. Please enter a "
                            "valid email address to ensure your e-tickets and event "
                            "notifications are delivered successfully.")

        elif field == "Contact":
            if self.role == ROLE_ORGANIZER:
                teks_ket = ("Add a phone number so audiences can easily reach out to "
                            "book your events or ask for collaborations. Please ensure "
                            "your phone number is correct to avoid missing potential "
                            "booking inquiries from your audience.")
            else:
                teks_ket = ("Add your phone number so event organizers can contact you "
                            "regarding event updates or registration details. Double-check "
                            "your number to ensure organizers can reach you for important "
                            "event updates.")

        elif field == "Name":
            teks_ket = "Your name can only be changed once every 30 days"

        else:  # Bio
            teks_ket = "You can edit your bio anytime."

        lbl_ket = QLabel(teks_ket)
        lbl_ket.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_MUTED};")
        lbl_ket.setWordWrap(True)
        layout.addWidget(lbl_ket)
        layout.addSpacing(16)

        # ---- BATAS KARAKTER ----
        # Name = 30 (soft: masih bisa ketik tapi muncul warning merah)
        # Bio  = 160 (hard: karakter baru ditolak, notif sementara muncul)
        # Email & Contact = None (tidak dibatasi)
        batas = {"Name": 30, "Bio": 160}.get(field, None)

        # ---- WIDGET INPUT ----
        # Bio → QTextEdit (kotak multi-baris)
        # Lainnya → QLineEdit (satu baris) di dalam frame dengan tombol clear
        input_widget = None

        if field == "Bio":
            # QTextEdit untuk Bio agar user bisa tulis beberapa kalimat
            input_widget = QTextEdit()
            input_widget.setPlaceholderText("My account is all about....")
            # Pre-fill dengan nilai bio yang sudah ada sebelumnya
            input_widget.setText(self.user_data.get("bio", ""))
            input_widget.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {COLOR_GRAY_LIGHT};
                    border-radius: 16px;
                    border: 2px solid transparent;
                    padding: 16px;
                    font-size: 14px;
                    color: #333333;
                }}
            """)
            input_widget.setFixedHeight(180)
            layout.addWidget(input_widget)

            # Counter karakter di bawah kanan kotak Bio
            lbl_counter = QLabel(f"0/{batas}")
            lbl_counter.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
            lbl_counter.setAlignment(Qt.AlignRight)
            layout.addWidget(lbl_counter)

        else:
            # QFrame sebagai container input + tombol clear
            # agar border bisa diubah warnanya saat Name melebihi batas
            input_frame = QFrame()
            input_frame.setObjectName("input_frame")
            input_frame.setStyleSheet(f"""
                QFrame#input_frame {{
                    background-color: {COLOR_GRAY_LIGHT};
                    border-radius: 12px;
                    border: 2px solid transparent;
                }}
            """)
            input_frame.setFixedHeight(56)

            frame_layout = QHBoxLayout(input_frame)
            frame_layout.setContentsMargins(16, 0, 12, 0)
            frame_layout.setSpacing(8)

            # Khusus Contact: tambahkan prefix "+62 |" di kiri input
            # sesuai mockup Figma (nomor Indonesia)
            if field == "Contact":
                lbl_prefix = QLabel("+62  |")
                lbl_prefix.setStyleSheet(f"""
                    color: {COLOR_TEXT_PRIMARY};
                    font-size: 14px;
                    font-weight: bold;
                    padding-right: 4px;
                """)
                frame_layout.addWidget(lbl_prefix)

            # Placeholder teks sesuai field
            placeholder = {
                "Name"   : "Add your preferred name",
                "Email"  : "Enter your email",
                "Contact": "Enter phone number",
            }.get(field, f"Edit {field}")

            input_widget = QLineEdit()
            input_widget.setPlaceholderText(placeholder)
            input_widget.setStyleSheet("""
                QLineEdit {
                    background: transparent;
                    border: none;
                    font-size: 14px;
                    color: #333333;
                }
            """)

            # Pre-fill dengan nilai lama yang sudah ada
            # key_map memetakan nama field (Inggris) ke key user_data (Indonesia)
            key_map = {"Name": "nama", "Email": "email", "Contact": "kontak"}
            input_widget.setText(self.user_data.get(key_map.get(field, ""), ""))

            # Tombol clear untuk menghapus seluruh teks sekaligus
            btn_clear = QPushButton()
            btn_clear.setIcon(QIcon("assets/cancel.png"))
            btn_clear.setIconSize(QSize(20, 20))
            btn_clear.setCursor(Qt.PointingHandCursor)
            btn_clear.setFixedSize(24, 24)
            btn_clear.setStyleSheet("background: transparent; border: none;")
            btn_clear.clicked.connect(lambda: input_widget.clear())

            frame_layout.addWidget(input_widget)
            frame_layout.addWidget(btn_clear)
            layout.addWidget(input_frame)

            # Counter dan warning hanya untuk Name (soft limit)
            if batas:
                lbl_counter = QLabel(f"0/{batas}")
                lbl_counter.setStyleSheet(
                    f"font-size: 12px; color: {COLOR_TEXT_MUTED};"
                )
                lbl_counter.setAlignment(Qt.AlignRight)
                layout.addWidget(lbl_counter)

                # Warning permanen (muncul di bawah counter saat lewat batas)
                lbl_warning = QWidget()
                lbl_warning.setStyleSheet("background: transparent;")
                w_layout = QHBoxLayout(lbl_warning)
                w_layout.setContentsMargins(0, 0, 0, 0)
                w_layout.setSpacing(6)
                w_icon = QLabel()
                w_icon.setPixmap(QIcon("assets/warning.png").pixmap(QSize(14, 14)))
                w_text = QLabel("Character limit reached")
                w_text.setStyleSheet("font-size: 12px; color: #E05C5C;")
                w_layout.addWidget(w_icon)
                w_layout.addWidget(w_text)
                w_layout.addStretch()
                lbl_warning.setVisible(False)
                layout.addWidget(lbl_warning)

        layout.addStretch()
        root.addWidget(konten, stretch=1)

        # ---- BOTTOM BAR: Cancel | notif sementara | Save ----
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(64)
        bottom_bar.setStyleSheet(
            f"background: transparent; border-top: 1px solid {COLOR_DIVIDER};"
        )

        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(50, 0, 50, 0)

        # Tombol Cancel: kembali ke Account Settings tanpa menyimpan
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 15px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ color: {COLOR_TEAL_DARK}; }}
        """)
        btn_cancel.clicked.connect(self.tutup_panel_edit)

        # Notifikasi sementara di tengah bottom bar
        # Hanya dipakai untuk Bio (hard limit) — muncul 2 detik lalu hilang
        lbl_notif_tengah = QLabel("Character limit exceeded")
        lbl_notif_tengah.setStyleSheet("font-size: 12px; color: #E05C5C;")
        lbl_notif_tengah.setAlignment(Qt.AlignCenter)
        lbl_notif_tengah.setVisible(False)

        def tampil_notif_sementara():
            # Tampilkan notif tengah selama 2 detik lalu sembunyikan otomatis
            lbl_notif_tengah.setVisible(True)
            QTimer.singleShot(2000, lambda: lbl_notif_tengah.setVisible(False))

        # Tombol Save: disabled dan transparan saat input kosong,
        # aktif merah pekat saat ada input yang valid
        btn_save = QPushButton("Save")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setEnabled(False)
        btn_save.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(220, 50, 50, 0.35);
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
        """)
        btn_save.clicked.connect(
            lambda: self.simpan_edit(
                field,
                input_widget.toPlainText() if field == "Bio" else input_widget.text()
            )
        )

        bottom_layout.addWidget(btn_cancel)
        bottom_layout.addStretch()
        bottom_layout.addWidget(lbl_notif_tengah)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_save)
        root.addWidget(bottom_bar)

        # ---- LOGIKA REAL-TIME SAAT USER MENGETIK ----
        def on_text_changed():
            # Ambil teks dari widget yang sesuai
            text = input_widget.toPlainText() if field == "Bio" else input_widget.text()
            jumlah = len(text)

            if field == "Bio":
                # Hard limit: potong teks jika melebihi batas
                # blockSignals mencegah infinite loop saat setPlainText dipanggil
                if jumlah > batas:
                    input_widget.blockSignals(True)
                    input_widget.setPlainText(text[:batas])
                    cursor = input_widget.textCursor()
                    cursor.movePosition(cursor.End)
                    input_widget.setTextCursor(cursor)
                    input_widget.blockSignals(False)
                    tampil_notif_sementara()
                    jumlah = batas

                # Counter merah saat tepat di batas, abu-abu jika masih aman
                if jumlah == batas:
                    lbl_counter.setText(
                        f"<span style='color:#E05C5C;'>{jumlah}</span>/{batas}"
                    )
                    lbl_counter.setTextFormat(Qt.RichText)
                else:
                    lbl_counter.setText(f"{jumlah}/{batas}")
                    lbl_counter.setTextFormat(Qt.PlainText)
                    lbl_counter.setStyleSheet(
                        f"font-size: 12px; color: {COLOR_TEXT_MUTED};"
                    )

            else:
                # Soft limit untuk Name: bisa ketik melebihi batas
                # tapi Save dinonaktifkan dan muncul warning merah
                if batas and jumlah > batas:
                    lbl_counter.setText(
                        f"<span style='color:#E05C5C;'>{jumlah}</span>/{batas}"
                    )
                    lbl_counter.setTextFormat(Qt.RichText)
                    input_frame.setStyleSheet(f"""
                        QFrame#input_frame {{
                            background-color: {COLOR_GRAY_LIGHT};
                            border-radius: 12px;
                            border: 2px solid #E05C5C;
                        }}
                    """)
                    lbl_warning.setVisible(True)
                    btn_save.setEnabled(False)
                    btn_save.setStyleSheet("""
                        QPushButton {
                            background: transparent;
                            color: rgba(220, 50, 50, 0.35);
                            font-size: 15px;
                            font-weight: bold;
                            border: none;
                        }
                    """)
                    return  # Langsung return, tidak perlu cek Save di bawah

                elif batas:
                    # Kembali normal jika jumlah karakter sudah di bawah batas
                    lbl_counter.setText(f"{jumlah}/{batas}")
                    lbl_counter.setTextFormat(Qt.PlainText)
                    lbl_counter.setStyleSheet(
                        f"font-size: 12px; color: {COLOR_TEXT_MUTED};"
                    )
                    input_frame.setStyleSheet(f"""
                        QFrame#input_frame {{
                            background-color: {COLOR_GRAY_LIGHT};
                            border-radius: 12px;
                            border: 2px solid transparent;
                        }}
                    """)
                    lbl_warning.setVisible(False)

            # Aktifkan Save hanya jika ada teks dan tidak melebihi batas
            if jumlah > 0:
                btn_save.setEnabled(True)
                btn_save.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #CC0000;
                        font-size: 15px;
                        font-weight: bold;
                        border: none;
                    }
                    QPushButton:hover { color: #990000; }
                """)
            else:
                btn_save.setEnabled(False)
                btn_save.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: rgba(220, 50, 50, 0.35);
                        font-size: 15px;
                        font-weight: bold;
                        border: none;
                    }
                """)

        # Hubungkan sinyal textChanged ke on_text_changed
        # QTextEdit: sinyal tanpa argumen
        # QLineEdit: sinyal membawa string, di-ignore dengan lambda _
        if field == "Bio":
            input_widget.textChanged.connect(on_text_changed)
        else:
            input_widget.textChanged.connect(lambda _: on_text_changed())

        # Masukkan sub-panel edit ke stacked_widget dan tampilkan
        self.stacked_widget.addWidget(panel_edit)
        self.stacked_widget.setCurrentWidget(panel_edit)
        self.panel_edit_aktif = panel_edit


    # ----------------------------------------------------------
    # FUNGSI tutup_panel_edit()
    # Dipanggil saat user klik "Cancel" di sub-panel edit
    # Kembali ke panel Account Settings dan hapus sub-panel dari memori
    # ----------------------------------------------------------
    def tutup_panel_edit(self):

        # Kembali ke panel Account (index 0 di stacked_widget)
        self.stacked_widget.setCurrentWidget(self)

        # Hapus sub-panel edit dari stacked_widget agar tidak menumpuk
        # Setiap klik panah membuat panel_edit baru,
        # jadi panel lama harus dihapus agar memori tetap bersih
        if self.panel_edit_aktif:
            self.stacked_widget.removeWidget(self.panel_edit_aktif)
            self.panel_edit_aktif.deleteLater()
            self.panel_edit_aktif = None


    # ----------------------------------------------------------
    # FUNGSI simpan_edit()
    # Dipanggil saat user klik "Save" di sub-panel edit
    # Menyimpan nilai baru ke user_data lalu refresh tampilan Account
    #
    # Parameter:
    #   field      = nama field yang diedit ("Name", "Bio", dll)
    #   nilai_baru = teks yang dimasukkan user
    # ----------------------------------------------------------
    def simpan_edit(self, field, nilai_baru):

        # Mapping nama field tampilan (Inggris) ke key user_data (Indonesia)
        field_ke_key = {
            "Name"   : "nama",
            "Bio"    : "bio",
            "Email"  : "email",
            "Contact": "kontak",
        }

        # Simpan nilai baru ke dictionary user_data
        key = field_ke_key.get(field)
        if key:
            self.user_data[key] = nilai_baru

        # Tutup sub-panel edit terlebih dahulu
        self.tutup_panel_edit()

        # Refresh tampilan Account agar nilai baru langsung terlihat
        # tanpa perlu menutup dan membuka ulang Settings
        self._render_account()


# ==============================================================
# BLOK TESTING MANDIRI
# Jalankan file ini langsung untuk preview panel Account:
#   python settings/account_window.py
#
# Karena AccountPanel butuh stacked_widget, di sini kita bungkus
# dengan QDialog sederhana sebagai simulasi settings_window.py
# ==============================================================
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Simulasi jendela settings sebagai container
    dialog = QDialog()
    dialog.setWindowTitle("Account Settings - Preview")
    dialog.setFixedSize(680, 620)
    dialog.setStyleSheet("""
        QDialog {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #BDD7D8, stop:0.5 #D6E6E6,
                stop:0.75 #D2E6E5, stop:1 #F7CBCA
            );
        }
    """)

    # Simulasi stacked_widget sebagai container panel
    stacked = QStackedWidget(dialog)
    stacked.setGeometry(0, 0, 680, 620)
    stacked.setStyleSheet("background: transparent;")

    # Data dummy untuk testing — ganti role untuk test tampilan berbeda
    user_dummy = {
        "nama"   : "",
        "bio"    : "",
        "email"  : "",
        "kontak" : "",
        "role"   : ROLE_UMUM,
        "inisial": ""
    }

    panel = AccountPanel(user_data=user_dummy, stacked_widget=stacked)
    stacked.addWidget(panel)
    stacked.setCurrentWidget(panel)

    dialog.show()
    sys.exit(app.exec_())

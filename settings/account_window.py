# ==============================================================
# FILE: settings/account_window.py
# ==============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

COLOR_GRAY_LIGHT   = "#D2E6E5"
COLOR_TEAL_DARK    = "#516465"
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_TEXT_MUTED   = "#9AABAB"
COLOR_DIVIDER      = "#D2E6E5"
COLOR_AVATAR_DEFAULT = "#EEAAAA"

ROLE_ORGANIZER = "organizer"
ROLE_MAHASISWA = "mahasiswa"
ROLE_UMUM      = "umum"

# Resolve assets path relative to this file
_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSETS_DIR = os.path.join(_BASE_DIR, "assets")

def _asset(name):
    return os.path.join(_ASSETS_DIR, name)


class AccountPanel(QWidget):

    def __init__(self, user_data=None, stacked_widget=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {
            "nama": "", "bio": "", "email": "", "kontak": "",
            "role": ROLE_UMUM, "inisial": ""
        }
        self.role = self.user_data.get("role", ROLE_UMUM)
        self.stacked_widget = stacked_widget
        self.panel_edit_aktif = None
        self.foto_profil = self.user_data.get("foto_profil", None)
        self.setStyleSheet("background: transparent;")
        self._render_account()

    # ----------------------------------------------------------
    def _render_account(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.layout())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        # Margin sama dengan notifications_window: (50, 40, 50, 40)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(0)

        # ── JUDUL ── (hanya ini yang dipertahankan sesuai permintaan)
        lbl_judul = QLabel("Account Settings")
        lbl_judul.setStyleSheet(f"""
            font-size: 55px;
            font-weight: bold;
            color: {COLOR_TEAL_DARK};
        """)
        layout.addWidget(lbl_judul)
        layout.addSpacing(30)

        # ── AVATAR (176x176) di tengah ──
        layout.addWidget(self._buat_avatar_center())
        layout.addSpacing(8)

        # ── TEKS "Change photo" ──
        lbl_change = QLabel("Change photo")
        lbl_change.setAlignment(Qt.AlignHCenter)
        lbl_change.setStyleSheet("color: black; font-size: 25px;")
        lbl_change.setCursor(Qt.PointingHandCursor)
        lbl_change.mousePressEvent = lambda e: self._upload_foto()
        layout.addWidget(lbl_change)
        layout.addSpacing(30)

        # ── GARIS ATAS ──
        layout.addWidget(self._buat_divider())

        # ── BARIS INFO ──
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
        outer.addWidget(scroll)

    # ----------------------------------------------------------
    def _buat_avatar_center(self):
        """Avatar 176x176 dengan icon camera di tengah, centered secara horizontal."""
        AVATAR_SIZE = 176

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(wrapper)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addStretch()

        # Container avatar + camera icon (overlay)
        avatar_container = QWidget()
        avatar_container.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        avatar_container.setStyleSheet("background: transparent;")
        avatar_container.setCursor(Qt.PointingHandCursor)

        # Avatar background lingkaran
        lbl_avatar = QLabel(avatar_container)
        lbl_avatar.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        lbl_avatar.setAlignment(Qt.AlignCenter)

        if self.foto_profil:
            # Foto ada: tampilkan foto dengan blur 75%
            pixmap_bulat = self._pixmap_ke_lingkaran_blur(self.foto_profil, AVATAR_SIZE)
            lbl_avatar.setPixmap(pixmap_bulat)
            lbl_avatar.setStyleSheet(f"border-radius: {AVATAR_SIZE//2}px;")
        else:
            # Default: warna pink #EEAAAA
            lbl_avatar.setStyleSheet(f"""
                background-color: {COLOR_AVATAR_DEFAULT};
                border-radius: {AVATAR_SIZE//2}px;
            """)

        # Icon camera di tengah (overlay)
        lbl_camera = QLabel(avatar_container)
        lbl_camera.setAlignment(Qt.AlignCenter)
        cam_icon_path = _asset("camera.png")
        if os.path.exists(cam_icon_path):
            cam_pixmap = QPixmap(cam_icon_path).scaled(
                60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            lbl_camera.setPixmap(cam_pixmap)
        else:
            lbl_camera.setText("📷")
            lbl_camera.setStyleSheet("font-size: 40px; color: white;")
        lbl_camera.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        lbl_camera.setStyleSheet("background: transparent;")

        # Klik seluruh container → upload foto
        avatar_container.mousePressEvent = lambda e: self._upload_foto()

        h_layout.addWidget(avatar_container)
        h_layout.addStretch()
        return wrapper

    # ----------------------------------------------------------
    def _upload_foto(self):
        """Buka file dialog → CropDialog → simpan hasil crop."""
        # Pastikan parent widget sudah ditampilkan sebelum buka dialog
        # untuk menghindari forced close
        try:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Pilih Foto Profil",
                "",
                "Gambar (*.png *.jpg *.jpeg *.webp *.bmp)"
            )
        except Exception:
            return

        if not path:
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Gagal", "File gambar tidak valid.")
            return

        try:
            dialog = CropDialog(pixmap, parent=self)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                hasil_crop = dialog.get_cropped_pixmap()
                if hasil_crop and not hasil_crop.isNull():
                    self.foto_profil = hasil_crop
                    self.user_data["foto_profil"] = hasil_crop
                    self._render_account()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal membuka crop dialog:\n{e}")

    def _hapus_foto(self):
        self.foto_profil = None
        self.user_data["foto_profil"] = None
        self._render_account()

    @staticmethod
    def _pixmap_ke_lingkaran(pixmap, size):
        scaled = pixmap.scaled(
            size, size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        if scaled.width() != size or scaled.height() != size:
            x = (scaled.width()  - size) // 2
            y = (scaled.height() - size) // 2
            scaled = scaled.copy(x, y, size, size)

        hasil = QPixmap(size, size)
        hasil.fill(Qt.transparent)

        painter = QPainter(hasil)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        return hasil

    @staticmethod
    def _pixmap_ke_lingkaran_blur(pixmap, size):
        """Pixmap lingkaran dengan opacity 25% (75% blur) agar tidak tabrakan dengan icon camera."""
        scaled = pixmap.scaled(
            size, size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        if scaled.width() != size or scaled.height() != size:
            x = (scaled.width()  - size) // 2
            y = (scaled.height() - size) // 2
            scaled = scaled.copy(x, y, size, size)

        hasil = QPixmap(size, size)
        hasil.fill(Qt.transparent)

        painter = QPainter(hasil)
        painter.setRenderHint(QPainter.Antialiasing)
        # Clip lingkaran
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        # Gambar foto dengan opacity 25% (75% blur/transparan)
        painter.setOpacity(0.25)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        return hasil

    # ----------------------------------------------------------
    def _buat_baris_info(self, field_label, field_value):
        baris = QWidget()
        baris.setStyleSheet("background: transparent;")
        baris.setFixedHeight(56)
        baris.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(baris)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Label kiri: Name / Bio / Email / Contact (warna #828282, size 25)
        lbl_field = QLabel(field_label)
        lbl_field.setStyleSheet("color: #828282; font-size: 25px;")
        lbl_field.setFixedWidth(180)

        # Nilai field di kanan (warna hitam, size 25)
        is_placeholder = field_value.startswith("add ")
        lbl_value = QLabel(field_value)
        lbl_value.setStyleSheet(
            f"color: {'#828282' if is_placeholder else 'black'}; font-size: 25px;"
        )
        lbl_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Tombol panah (W=16 H=12, warna hitam)
        btn_arrow = QPushButton()
        icon_path = _asset("next.png")
        if os.path.exists(icon_path):
            btn_arrow.setIcon(QIcon(icon_path))
        btn_arrow.setIconSize(QSize(16, 12))
        btn_arrow.setCursor(Qt.PointingHandCursor)
        btn_arrow.setFixedSize(28, 28)
        btn_arrow.setStyleSheet("background: transparent; border: none;")
        btn_arrow.clicked.connect(
            lambda checked, f=field_label: self.buka_panel_edit(f)
        )

        layout.addWidget(lbl_field)
        layout.addWidget(lbl_value, stretch=1)
        layout.addSpacing(8)
        layout.addWidget(btn_arrow)

        # Klik baris → buka edit
        baris.mousePressEvent = lambda e, f=field_label: self.buka_panel_edit(f)

        return baris

    # ----------------------------------------------------------
    def _buat_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(
            f"color: {COLOR_DIVIDER}; background-color: {COLOR_DIVIDER};"
        )
        line.setFixedHeight(1)
        return line

    # ----------------------------------------------------------
    def buka_panel_edit(self, field):
        panel_edit = QWidget()
        panel_edit.setStyleSheet("background: transparent;")

        root = QVBoxLayout(panel_edit)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        konten = QWidget()
        konten.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(konten)
        layout.setContentsMargins(50, 40, 50, 20)
        layout.setSpacing(12)

        judul_map = {
            "Name": "Name", "Bio": "Bio",
            "Email": "Add an email", "Contact": "Add phone",
        }
        lbl_judul = QLabel(judul_map.get(field, field))
        lbl_judul.setStyleSheet(f"""
            font-size: 28px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};
        """)
        layout.addWidget(lbl_judul)

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
        else:
            teks_ket = "You can edit your bio anytime."

        lbl_ket = QLabel(teks_ket)
        lbl_ket.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_MUTED};")
        lbl_ket.setWordWrap(True)
        layout.addWidget(lbl_ket)
        layout.addSpacing(16)

        batas = {"Name": 30, "Bio": 160}.get(field, None)
        input_widget = None

        if field == "Bio":
            input_widget = QTextEdit()
            input_widget.setPlaceholderText("My account is all about....")
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

            lbl_counter = QLabel(f"0/{batas}")
            lbl_counter.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
            lbl_counter.setAlignment(Qt.AlignRight)
            layout.addWidget(lbl_counter)

        else:
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

            if field == "Contact":
                lbl_prefix = QLabel("+62  |")
                lbl_prefix.setStyleSheet(f"""
                    color: {COLOR_TEXT_PRIMARY}; font-size: 14px;
                    font-weight: bold; padding-right: 4px;
                """)
                frame_layout.addWidget(lbl_prefix)

            placeholder = {
                "Name": "Add your preferred name",
                "Email": "Enter your email",
                "Contact": "Enter phone number",
            }.get(field, f"Edit {field}")

            input_widget = QLineEdit()
            input_widget.setPlaceholderText(placeholder)
            input_widget.setStyleSheet("""
                QLineEdit {
                    background: transparent; border: none;
                    font-size: 14px; color: #333333;
                }
            """)
            key_map = {"Name": "nama", "Email": "email", "Contact": "kontak"}
            input_widget.setText(self.user_data.get(key_map.get(field, ""), ""))

            btn_clear = QPushButton()
            cancel_path = _asset("cancel.png")
            if os.path.exists(cancel_path):
                btn_clear.setIcon(QIcon(cancel_path))
            btn_clear.setIconSize(QSize(20, 20))
            btn_clear.setCursor(Qt.PointingHandCursor)
            btn_clear.setFixedSize(24, 24)
            btn_clear.setStyleSheet("background: transparent; border: none;")
            btn_clear.clicked.connect(lambda: input_widget.clear())

            frame_layout.addWidget(input_widget)
            frame_layout.addWidget(btn_clear)
            layout.addWidget(input_frame)

            if batas:
                lbl_counter = QLabel(f"0/{batas}")
                lbl_counter.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
                lbl_counter.setAlignment(Qt.AlignRight)
                layout.addWidget(lbl_counter)

                lbl_warning = QWidget()
                lbl_warning.setStyleSheet("background: transparent;")
                w_layout = QHBoxLayout(lbl_warning)
                w_layout.setContentsMargins(0, 0, 0, 0)
                w_layout.setSpacing(6)
                w_icon = QLabel()
                warning_path = _asset("warning.png")
                if os.path.exists(warning_path):
                    w_icon.setPixmap(QIcon(warning_path).pixmap(QSize(14, 14)))
                w_text = QLabel("Character limit reached")
                w_text.setStyleSheet("font-size: 12px; color: #E05C5C;")
                w_layout.addWidget(w_icon)
                w_layout.addWidget(w_text)
                w_layout.addStretch()
                lbl_warning.setVisible(False)
                layout.addWidget(lbl_warning)

        layout.addStretch()
        root.addWidget(konten, stretch=1)

        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(64)
        bottom_bar.setStyleSheet(
            f"background: transparent; border-top: 1px solid {COLOR_DIVIDER};"
        )
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(50, 0, 50, 0)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLOR_TEXT_PRIMARY};
                font-size: 15px; font-weight: bold; border: none;
            }}
            QPushButton:hover {{ color: {COLOR_TEAL_DARK}; }}
        """)
        btn_cancel.clicked.connect(self.tutup_panel_edit)

        lbl_notif_tengah = QLabel("Character limit exceeded")
        lbl_notif_tengah.setStyleSheet("font-size: 12px; color: #E05C5C;")
        lbl_notif_tengah.setAlignment(Qt.AlignCenter)
        lbl_notif_tengah.setVisible(False)

        def tampil_notif_sementara():
            lbl_notif_tengah.setVisible(True)
            QTimer.singleShot(2000, lambda: lbl_notif_tengah.setVisible(False))

        btn_save = QPushButton("Save")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setEnabled(False)
        btn_save.setStyleSheet("""
            QPushButton {
                background: transparent; color: rgba(220, 50, 50, 0.35);
                font-size: 15px; font-weight: bold; border: none;
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

        def on_text_changed():
            text = input_widget.toPlainText() if field == "Bio" else input_widget.text()
            jumlah = len(text)

            if field == "Bio":
                if jumlah > batas:
                    input_widget.blockSignals(True)
                    input_widget.setPlainText(text[:batas])
                    cursor = input_widget.textCursor()
                    cursor.movePosition(cursor.End)
                    input_widget.setTextCursor(cursor)
                    input_widget.blockSignals(False)
                    tampil_notif_sementara()
                    jumlah = batas

                if jumlah == batas:
                    lbl_counter.setText(f"<span style='color:#E05C5C;'>{jumlah}</span>/{batas}")
                    lbl_counter.setTextFormat(Qt.RichText)
                else:
                    lbl_counter.setText(f"{jumlah}/{batas}")
                    lbl_counter.setTextFormat(Qt.PlainText)
                    lbl_counter.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
            else:
                if batas and jumlah > batas:
                    lbl_counter.setText(f"<span style='color:#E05C5C;'>{jumlah}</span>/{batas}")
                    lbl_counter.setTextFormat(Qt.RichText)
                    input_frame.setStyleSheet(f"""
                        QFrame#input_frame {{
                            background-color: {COLOR_GRAY_LIGHT};
                            border-radius: 12px; border: 2px solid #E05C5C;
                        }}
                    """)
                    lbl_warning.setVisible(True)
                    btn_save.setEnabled(False)
                    btn_save.setStyleSheet("""
                        QPushButton {
                            background: transparent; color: rgba(220, 50, 50, 0.35);
                            font-size: 15px; font-weight: bold; border: none;
                        }
                    """)
                    return
                elif batas:
                    lbl_counter.setText(f"{jumlah}/{batas}")
                    lbl_counter.setTextFormat(Qt.PlainText)
                    lbl_counter.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
                    input_frame.setStyleSheet(f"""
                        QFrame#input_frame {{
                            background-color: {COLOR_GRAY_LIGHT};
                            border-radius: 12px; border: 2px solid transparent;
                        }}
                    """)
                    lbl_warning.setVisible(False)

            if jumlah > 0:
                btn_save.setEnabled(True)
                btn_save.setStyleSheet("""
                    QPushButton {
                        background: transparent; color: #CC0000;
                        font-size: 15px; font-weight: bold; border: none;
                    }
                    QPushButton:hover { color: #990000; }
                """)
            else:
                btn_save.setEnabled(False)
                btn_save.setStyleSheet("""
                    QPushButton {
                        background: transparent; color: rgba(220, 50, 50, 0.35);
                        font-size: 15px; font-weight: bold; border: none;
                    }
                """)

        if field == "Bio":
            input_widget.textChanged.connect(on_text_changed)
        else:
            input_widget.textChanged.connect(lambda _: on_text_changed())

        self.stacked_widget.addWidget(panel_edit)
        self.stacked_widget.setCurrentWidget(panel_edit)
        self.panel_edit_aktif = panel_edit

    # ----------------------------------------------------------
    def tutup_panel_edit(self):
        self.stacked_widget.setCurrentWidget(self)
        if self.panel_edit_aktif:
            self.stacked_widget.removeWidget(self.panel_edit_aktif)
            self.panel_edit_aktif.deleteLater()
            self.panel_edit_aktif = None

    def simpan_edit(self, field, nilai_baru):
        field_ke_key = {
            "Name": "nama", "Bio": "bio", "Email": "email", "Contact": "kontak",
        }
        key = field_ke_key.get(field)
        if key:
            self.user_data[key] = nilai_baru
        self.tutup_panel_edit()
        self._render_account()


# ==============================================================
# CLASS CropDialog
# ==============================================================
class CropDialog(QDialog):

    def __init__(self, pixmap_asli, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crop Foto Profil")
        self.setFixedSize(700, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        self.setStyleSheet(f"""
            QDialog {{ background-color: #2B3535; }}
            QLabel {{ color: white; background: transparent; }}
            QPushButton {{
                border-radius: 8px; font-size: 14px;
                font-weight: bold; padding: 8px 24px;
            }}
            QSlider::groove:horizontal {{
                height: 4px; background: #516465; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                width: 16px; height: 16px; margin: -6px 0;
                background: white; border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLOR_GRAY_LIGHT}; border-radius: 2px;
            }}
        """)

        self._pixmap_asli = pixmap_asli
        self._hasil_crop  = None
        self._kunci_rasio = True
        self._rasio_w = 1
        self._rasio_h = 1

        CANVAS_W, CANVAS_H = 460, 400
        self._canvas_w = CANVAS_W
        self._canvas_h = CANVAS_H

        self._skala_min  = min(CANVAS_W / pixmap_asli.width(),
                               CANVAS_H / pixmap_asli.height())
        self._skala_max  = self._skala_min * 5.0
        self._skala      = self._skala_min
        self._img_x = 0.0
        self._img_y = 0.0

        default_size = min(200, CANVAS_W - 20, CANVAS_H - 20)
        self._crop_x = (CANVAS_W - default_size) / 2
        self._crop_y = (CANVAS_H - default_size) / 2
        self._crop_w = float(default_size)
        self._crop_h = float(default_size)

        self._drag_mode   = None
        self._drag_origin = QPoint()
        self._drag_crop_snapshot = None
        self._drag_img_snapshot  = None

        self._build_ui()
        self._refresh_canvas()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        kiri = QVBoxLayout()
        kiri.setSpacing(8)

        lbl_petunjuk = QLabel("Geser kotak untuk memilih area foto  •  Scroll untuk zoom")
        lbl_petunjuk.setStyleSheet("font-size: 12px; color: #9AABAB;")
        lbl_petunjuk.setAlignment(Qt.AlignCenter)
        kiri.addWidget(lbl_petunjuk)

        self._canvas = QLabel()
        self._canvas.setFixedSize(self._canvas_w, self._canvas_h)
        self._canvas.setStyleSheet("background: #1A2323; border-radius: 8px;")
        self._canvas.setAlignment(Qt.AlignCenter)
        self._canvas.installEventFilter(self)
        self._canvas.setMouseTracking(True)
        kiri.addWidget(self._canvas)

        zoom_row = QHBoxLayout()
        lbl_zoom = QLabel("Zoom")
        lbl_zoom.setStyleSheet("font-size: 12px; color: #9AABAB; min-width:36px;")
        self._slider_zoom = QSlider(Qt.Horizontal)
        self._slider_zoom.setRange(0, 400)
        self._slider_zoom.setValue(0)
        self._slider_zoom.setFixedWidth(260)
        self._slider_zoom.valueChanged.connect(self._on_slider_zoom)
        zoom_row.addWidget(lbl_zoom)
        zoom_row.addWidget(self._slider_zoom)
        zoom_row.addStretch()
        kiri.addLayout(zoom_row)
        root.addLayout(kiri)

        kanan = QVBoxLayout()
        kanan.setSpacing(12)
        kanan.setAlignment(Qt.AlignTop)

        lbl_preview_title = QLabel("Preview")
        lbl_preview_title.setStyleSheet("font-size: 13px; font-weight: bold;")
        lbl_preview_title.setAlignment(Qt.AlignCenter)
        kanan.addWidget(lbl_preview_title)

        self._lbl_preview = QLabel()
        self._lbl_preview.setFixedSize(120, 120)
        self._lbl_preview.setAlignment(Qt.AlignCenter)
        self._lbl_preview.setStyleSheet("border-radius: 60px; background-color: #516465;")
        kanan.addWidget(self._lbl_preview, alignment=Qt.AlignHCenter)
        kanan.addSpacing(12)

        lbl_rasio = QLabel("Crop ratio")
        lbl_rasio.setStyleSheet("font-size: 12px; color: #9AABAB;")
        lbl_rasio.setAlignment(Qt.AlignCenter)
        kanan.addWidget(lbl_rasio)

        rasio_row = QHBoxLayout()
        rasio_row.setSpacing(6)
        self._btn_11   = QPushButton("1 : 1")
        self._btn_free = QPushButton("Free")
        for btn in (self._btn_11, self._btn_free):
            btn.setFixedWidth(70)
            btn.setFixedHeight(30)
        self._btn_11.setStyleSheet(self._style_tombol_rasio(aktif=True))
        self._btn_free.setStyleSheet(self._style_tombol_rasio(aktif=False))
        self._btn_11.clicked.connect(lambda: self._set_rasio(1, 1))
        self._btn_free.clicked.connect(lambda: self._set_rasio(0, 0))
        rasio_row.addWidget(self._btn_11)
        rasio_row.addWidget(self._btn_free)
        kanan.addLayout(rasio_row)
        kanan.addStretch()

        self._btn_confirm = QPushButton("Confirm")
        self._btn_confirm.setFixedHeight(40)
        self._btn_confirm.setStyleSheet(f"""
            QPushButton {{ background-color: {COLOR_TEAL_DARK}; color: white; }}
            QPushButton:hover {{ background-color: #3E4F50; }}
        """)
        self._btn_confirm.clicked.connect(self._on_confirm)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton { background-color: #3E4F50; color: white; }
            QPushButton:hover { background-color: #516465; }
        """)
        btn_cancel.clicked.connect(self.reject)

        kanan.addWidget(self._btn_confirm)
        kanan.addWidget(btn_cancel)
        root.addLayout(kanan)

    @staticmethod
    def _style_tombol_rasio(aktif):
        if aktif:
            return f"""
                QPushButton {{
                    background-color: {COLOR_TEAL_DARK}; color: white;
                    border-radius: 6px; font-size: 12px; font-weight: bold;
                }}
            """
        return """
            QPushButton {
                background-color: #3E4F50; color: #9AABAB;
                border-radius: 6px; font-size: 12px;
            }
            QPushButton:hover { color: white; }
        """

    def _set_rasio(self, w, h):
        self._kunci_rasio = (w > 0 and h > 0)
        self._rasio_w = w
        self._rasio_h = h
        if self._kunci_rasio:
            sisi = min(self._crop_w, self._crop_h)
            self._crop_w = sisi
            self._crop_h = sisi
            self._btn_11.setStyleSheet(self._style_tombol_rasio(True))
            self._btn_free.setStyleSheet(self._style_tombol_rasio(False))
        else:
            self._btn_11.setStyleSheet(self._style_tombol_rasio(False))
            self._btn_free.setStyleSheet(self._style_tombol_rasio(True))
        self._refresh_canvas()

    def _refresh_canvas(self):
        kanvas = QPixmap(self._canvas_w, self._canvas_h)
        kanvas.fill(QColor("#1A2323"))

        p = QPainter(kanvas)
        p.setRenderHint(QPainter.Antialiasing)

        img_w = int(self._pixmap_asli.width()  * self._skala)
        img_h = int(self._pixmap_asli.height() * self._skala)
        scaled_img = self._pixmap_asli.scaled(
            img_w, img_h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        p.drawPixmap(int(self._img_x), int(self._img_y), scaled_img)

        cx, cy = int(self._crop_x), int(self._crop_y)
        cw, ch = int(self._crop_w), int(self._crop_h)
        overlay_color = QColor(0, 0, 0, 140)
        p.fillRect(0,  0,           self._canvas_w, cy,            overlay_color)
        p.fillRect(0,  cy + ch,     self._canvas_w, self._canvas_h, overlay_color)
        p.fillRect(0,  cy,          cx, ch,                         overlay_color)
        p.fillRect(cx + cw, cy,     self._canvas_w, ch,             overlay_color)

        pen = QPen(QColor("white"), 2, Qt.SolidLine)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRect(cx, cy, cw, ch)

        pen_grid = QPen(QColor(255, 255, 255, 80), 1, Qt.DotLine)
        p.setPen(pen_grid)
        for i in (1, 2):
            p.drawLine(cx + cw * i // 3, cy, cx + cw * i // 3, cy + ch)
            p.drawLine(cx, cy + ch * i // 3, cx + cw, cy + ch * i // 3)

        pen_handle = QPen(QColor("white"), 3, Qt.SolidLine)
        p.setPen(pen_handle)
        L = 10
        corners = [
            (cx,      cy,      L,  0,  0,  L),
            (cx + cw, cy,     -L,  0,  0,  L),
            (cx,      cy + ch, L,  0,  0, -L),
            (cx + cw, cy + ch,-L,  0,  0, -L),
        ]
        for hx, hy, dx1, dy1, dx2, dy2 in corners:
            p.drawLine(hx, hy, hx + dx1, hy + dy1)
            p.drawLine(hx, hy, hx + dx2, hy + dy2)

        p.end()
        self._canvas.setPixmap(kanvas)
        self._update_preview()

    def _update_preview(self):
        rel_x = self._crop_x - self._img_x
        rel_y = self._crop_y - self._img_y
        src_x = rel_x / self._skala
        src_y = rel_y / self._skala
        src_w = self._crop_w / self._skala
        src_h = self._crop_h / self._skala

        src_x = max(0.0, min(src_x, self._pixmap_asli.width()  - 1))
        src_y = max(0.0, min(src_y, self._pixmap_asli.height() - 1))
        src_w = max(1.0, min(src_w, self._pixmap_asli.width()  - src_x))
        src_h = max(1.0, min(src_h, self._pixmap_asli.height() - src_y))

        crop_pix = self._pixmap_asli.copy(int(src_x), int(src_y), int(src_w), int(src_h))
        preview = AccountPanel._pixmap_ke_lingkaran(crop_pix, 120)
        self._lbl_preview.setPixmap(preview)
        self._lbl_preview.setStyleSheet("border-radius: 60px; background: transparent;")

    def _on_slider_zoom(self, nilai):
        import math
        t = nilai / 400.0
        skala_baru = self._skala_min * (self._skala_max / self._skala_min) ** t
        cx_center = self._canvas_w / 2
        cy_center = self._canvas_h / 2
        rasio = skala_baru / self._skala
        self._img_x = cx_center - rasio * (cx_center - self._img_x)
        self._img_y = cy_center - rasio * (cy_center - self._img_y)
        self._skala = skala_baru
        self._clamp_img()
        self._refresh_canvas()

    def wheelEvent(self, event):
        pos_global = event.globalPos()
        pos_canvas = self._canvas.mapFromGlobal(pos_global)
        if not self._canvas.rect().contains(pos_canvas):
            return
        delta = event.angleDelta().y()
        faktor = 1.12 if delta > 0 else (1 / 1.12)
        skala_baru = max(self._skala_min, min(self._skala_max, self._skala * faktor))
        rasio = skala_baru / self._skala
        self._img_x = pos_canvas.x() - rasio * (pos_canvas.x() - self._img_x)
        self._img_y = pos_canvas.y() - rasio * (pos_canvas.y() - self._img_y)
        self._skala = skala_baru
        self._clamp_img()
        import math
        if self._skala_max > self._skala_min:
            t = math.log(self._skala / self._skala_min) / math.log(self._skala_max / self._skala_min)
        else:
            t = 0.0
        self._slider_zoom.blockSignals(True)
        self._slider_zoom.setValue(int(t * 400))
        self._slider_zoom.blockSignals(False)
        self._refresh_canvas()

    def eventFilter(self, obj, event):
        if obj is not self._canvas:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._drag_origin = event.pos()
            mode = self._detect_handle(event.pos())
            self._drag_mode = mode
            self._drag_crop_snapshot = (self._crop_x, self._crop_y,
                                        self._crop_w, self._crop_h)
            self._drag_img_snapshot  = (self._img_x, self._img_y)
            return True
        elif event.type() == QEvent.MouseMove:
            if self._drag_mode:
                self._do_drag(event.pos())
            else:
                cur = self._cursor_untuk_mode(self._detect_handle(event.pos()))
                self._canvas.setCursor(cur)
            return True
        elif event.type() == QEvent.MouseButtonRelease:
            self._drag_mode = None
            return True

        return super().eventFilter(obj, event)

    def _detect_handle(self, pos):
        x, y = pos.x(), pos.y()
        cx, cy = self._crop_x, self._crop_y
        cw, ch = self._crop_w, self._crop_h
        TOL = 14

        def dekat(a, b): return abs(a - b) < TOL

        if dekat(x, cx)      and dekat(y, cy):      return "resize_tl"
        if dekat(x, cx + cw) and dekat(y, cy):      return "resize_tr"
        if dekat(x, cx)      and dekat(y, cy + ch): return "resize_bl"
        if dekat(x, cx + cw) and dekat(y, cy + ch): return "resize_br"
        if dekat(x, cx)      and cy < y < cy + ch:  return "resize_l"
        if dekat(x, cx + cw) and cy < y < cy + ch:  return "resize_r"
        if dekat(y, cy)      and cx < x < cx + cw:  return "resize_t"
        if dekat(y, cy + ch) and cx < x < cx + cw:  return "resize_b"
        if cx < x < cx + cw and cy < y < cy + ch:   return "move_crop"
        return "pan_img"

    @staticmethod
    def _cursor_untuk_mode(mode):
        mapping = {
            "move_crop": Qt.SizeAllCursor, "pan_img": Qt.OpenHandCursor,
            "resize_tl": Qt.SizeFDiagCursor, "resize_br": Qt.SizeFDiagCursor,
            "resize_tr": Qt.SizeBDiagCursor, "resize_bl": Qt.SizeBDiagCursor,
            "resize_l":  Qt.SizeHorCursor,   "resize_r":  Qt.SizeHorCursor,
            "resize_t":  Qt.SizeVerCursor,   "resize_b":  Qt.SizeVerCursor,
        }
        return mapping.get(mode, Qt.ArrowCursor)

    def _do_drag(self, pos):
        dx = pos.x() - self._drag_origin.x()
        dy = pos.y() - self._drag_origin.y()
        ox, oy, ow, oh = self._drag_crop_snapshot
        MIN_SIZE = 40

        if self._drag_mode == "move_crop":
            nx = max(0.0, min(ox + dx, self._canvas_w - ow))
            ny = max(0.0, min(oy + dy, self._canvas_h - oh))
            self._crop_x, self._crop_y = nx, ny

        elif self._drag_mode == "pan_img":
            ix, iy = self._drag_img_snapshot
            self._img_x = ix + dx
            self._img_y = iy + dy
            self._clamp_img()

        elif self._drag_mode in ("resize_tl", "resize_tr", "resize_bl", "resize_br",
                                  "resize_l", "resize_r", "resize_t", "resize_b"):
            nx, ny, nw, nh = ox, oy, ow, oh
            if "l" in self._drag_mode:
                nw = max(MIN_SIZE, ow - dx); nx = ox + ow - nw
            if "r" in self._drag_mode:
                nw = max(MIN_SIZE, ow + dx)
            if "t" in self._drag_mode:
                nh = max(MIN_SIZE, oh - dy); ny = oy + oh - nh
            if "b" in self._drag_mode:
                nh = max(MIN_SIZE, oh + dy)

            if self._kunci_rasio:
                sisi = max(nw, nh)
                if "l" in self._drag_mode: nx = ox + ow - sisi
                if "t" in self._drag_mode: ny = oy + oh - sisi
                nw = nh = sisi

            nx = max(0.0, nx); ny = max(0.0, ny)
            nw = min(nw, self._canvas_w - nx)
            nh = min(nh, self._canvas_h - ny)
            self._crop_x, self._crop_y = nx, ny
            self._crop_w, self._crop_h = nw, nh

        self._refresh_canvas()

    def _clamp_img(self):
        img_w = self._pixmap_asli.width()  * self._skala
        img_h = self._pixmap_asli.height() * self._skala
        margin = 60
        self._img_x = max(-img_w + margin, min(self._canvas_w - margin, self._img_x))
        self._img_y = max(-img_h + margin, min(self._canvas_h - margin, self._img_y))

    def _on_confirm(self):
        rel_x = self._crop_x - self._img_x
        rel_y = self._crop_y - self._img_y
        src_x = rel_x / self._skala
        src_y = rel_y / self._skala
        src_w = self._crop_w / self._skala
        src_h = self._crop_h / self._skala

        src_x = max(0.0, min(src_x, self._pixmap_asli.width()  - 1))
        src_y = max(0.0, min(src_y, self._pixmap_asli.height() - 1))
        src_w = max(1.0, min(src_w, self._pixmap_asli.width()  - src_x))
        src_h = max(1.0, min(src_h, self._pixmap_asli.height() - src_y))

        self._hasil_crop = self._pixmap_asli.copy(
            int(src_x), int(src_y), int(src_w), int(src_h)
        )
        self.accept()

    def get_cropped_pixmap(self):
        return self._hasil_crop


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = QDialog()
    dialog.setWindowTitle("Account Settings - Preview")
    dialog.setFixedSize(880, 680)
    dialog.setStyleSheet("""
        QDialog {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #BDD7D8, stop:0.5 #D6E6E6,
                stop:0.75 #D2E6E5, stop:1 #F7CBCA
            );
        }
    """)

    stacked = QStackedWidget(dialog)
    stacked.setGeometry(0, 0, 880, 680)
    stacked.setStyleSheet("background: transparent;")

    user_dummy = {
        "nama": "Event Organizer", "bio": "Music Festival",
        "email": "eventorganizer@gmail.com", "kontak": "+6281-3456-7898",
        "role": ROLE_ORGANIZER, "inisial": "EO"
    }

    panel = AccountPanel(user_data=user_dummy, stacked_widget=stacked)
    stacked.addWidget(panel)
    stacked.setCurrentWidget(panel)

    dialog.show()
    sys.exit(app.exec_())

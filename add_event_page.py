# ==============================================================
# FILE: add_event_page.py  (UPDATED)
# PERUBAHAN dari versi asli:
#   - publikasi_event(): saat mode edit, tambahkan "event_id" dan
#     pertahankan "status" lama ke dalam data_event yang di-emit,
#     sehingga setting_window._simpan_perubahan_event() bisa
#     menemukan row yang benar di database.
#
# FIX MULTILINGUAL (4 titik):
#   1. Menu "Internal" / "External" sekarang pakai lang.t() +
#      di-retranslate di _retranslate()
#   2. Validasi required field tidak lagi campur bahasa —
#      masing-masing field punya key lang sendiri
#   3. "Event date cannot be in the past!" → lang.t("add_event.err_date_past")
#   4. "Time has not been entered!"        → lang.t("add_event.err_time_empty")
# ==============================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QComboBox, QScrollArea, QMessageBox,
    QSizePolicy, QDateEdit, QTimeEdit,
    QToolButton, QMenu,
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QSize, QDateTime
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon, QIntValidator
from toggle_widget import ToggleSwitch
from upload_widget import PosterUploadDialog
import os
from language_manager import lang


class AddEventPage(QWidget):

    event_dipublikasi = pyqtSignal(dict)
    dibatalkan        = pyqtSignal()

    def __init__(self, parent=None, data_event=None):
        super().__init__(parent)
        self.poster_path  = ""
        self.data_event   = data_event
        self.setObjectName("add_event_page")

        # Set state sebelum UI dibuat agar _retranslate() aman dipanggil
        # baik untuk mode tambah event maupun mode edit event.
        self.jenis_terpilih = ""

        self.setup_ui()
        self.apply_style()

        if self.data_event:
            self._prefill_form(self.data_event)

        # Paksa semua teks UI mengikuti bahasa aktif saat halaman dibuat.
        # Ini penting untuk halaman edit event yang dibuat dinamis dari Your Events.
        self._retranslate()
        lang.language_changed.connect(self._retranslate)

    # ----------------------------------------------------------
    def setup_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(12)

        self.judul_label = QLabel(lang.t("add_event.title_new"))
        self.judul_label.setObjectName("judul_label")
        font_judul = QFont("Inter", 24)
        font_judul.setWeight(QFont.ExtraBold)
        self.judul_label.setFont(font_judul)
        outer_layout.addWidget(self.judul_label)

        self.sub_judul = QLabel(
            lang.t("add_event.subtitle_new")
        )
        self.sub_judul.setObjectName("sub_judul")
        font_sub = QFont("Inter", 12)
        font_sub.setWeight(QFont.Normal)
        self.sub_judul.setFont(font_sub)
        outer_layout.addWidget(self.sub_judul)

        self.card = QWidget()
        self.card.setObjectName("form_widget")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        self.label_info = QLabel(lang.t("add_event.section_main"))
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
        self.label_nama  = QLabel(lang.t("add_event.field_name_req"))
        self.label_nama.setObjectName("label_field")
        self.input_nama  = QLineEdit()
        self.input_nama.setPlaceholderText(lang.t("add_event.ph_name"))
        self.input_nama.setObjectName("input_field")
        nama_layout.addWidget(self.label_nama)
        nama_layout.addWidget(self.input_nama)

        jenis_layout = QVBoxLayout()
        self.label_jenis = QLabel(lang.t("add_event.field_type_req"))
        self.label_jenis.setObjectName("label_field")

        self.input_jenis = QPushButton(lang.t("add_event.select_type"))
        self.input_jenis.setObjectName("input_combo")
        self.input_jenis.setFixedHeight(42)
        self.input_jenis.setCursor(Qt.PointingHandCursor)

        self.menu_jenis = QMenu(self)
        self.menu_jenis.setCursor(Qt.PointingHandCursor)
        self.menu_jenis.setFixedWidth(140)
        self.menu_jenis.setStyleSheet("""
            QMenu {
                background-color: white; border: 1px solid #CBD5E0;
                border-radius: 8px; padding: 2px;
            }
            QMenu::item {
                padding: 4px 10px; border-radius: 4px;
                margin: 0px; color: #1a1a1a;
            }
            QMenu::item:selected { background-color: #D2E6E5; color: #2D6A6A; }
            QMenu::separator { height: 1px; background: #E5E7EB; margin: 2px 6px; }
        """)

        # FIX #1 — pakai lang.t() bukan string hardcoded
        self.action_internal = self.menu_jenis.addAction(lang.t("detail.internal"))
        self.menu_jenis.addSeparator()
        self.action_external = self.menu_jenis.addAction(lang.t("detail.external"))
        self.action_internal.triggered.connect(lambda: self.pilih_jenis("Internal"))
        self.action_external.triggered.connect(lambda: self.pilih_jenis("External"))

        self.input_jenis.clicked.connect(lambda: self.menu_jenis.exec_(
            self.input_jenis.mapToGlobal(self.input_jenis.rect().bottomLeft())
        ))

        jenis_layout.addWidget(self.label_jenis)
        jenis_layout.addWidget(self.input_jenis)

        baris1_layout.addLayout(nama_layout)
        baris1_layout.addLayout(jenis_layout)
        form_layout.addLayout(baris1_layout)

        # ---- BARIS 2: DESKRIPSI + KATEGORI ----
        baris2_layout = QHBoxLayout()
        baris2_layout.setSpacing(16)

        deskripsi_layout = QVBoxLayout()
        self.label_deskripsi = QLabel(lang.t("add_event.field_desc_req"))
        self.label_deskripsi.setObjectName("label_field")
        self.input_deskripsi = QLineEdit()
        self.input_deskripsi.setPlaceholderText(lang.t("add_event.ph_desc"))
        self.input_deskripsi.setObjectName("input_field")
        deskripsi_layout.addWidget(self.label_deskripsi)
        deskripsi_layout.addWidget(self.input_deskripsi)

        kategori_layout = QVBoxLayout()
        self.label_kategori = QLabel(lang.t("add_event.field_category_req"))
        self.label_kategori.setObjectName("label_field")
        self.input_kategori = QLineEdit()
        self.input_kategori.setPlaceholderText(
            lang.t("add_event.ph_category")
        )
        self.input_kategori.setObjectName("input_field")
        kategori_layout.addWidget(self.label_kategori)
        kategori_layout.addWidget(self.input_kategori)

        baris2_layout.addLayout(deskripsi_layout)
        baris2_layout.addLayout(kategori_layout)
        form_layout.addLayout(baris2_layout)

        # ---- LABEL WAKTU & TEMPAT ----
        self.label_waktu_tempat = QLabel(lang.t("add_event.section_time_venue"))
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
        self.label_tanggal = QLabel(lang.t("add_event.field_date_req"))
        self.label_tanggal.setObjectName("label_field")
        self.input_tanggal = QDateEdit()
        self.input_tanggal.setCalendarPopup(True)
        self.input_tanggal.setDisplayFormat("dd/MM/yyyy")
        self.input_tanggal.setDate(QDate.currentDate())

        # Tidak bisa pilih tanggal sebelum hari ini
        self.input_tanggal.setMinimumDate(QDate.currentDate())
        self.input_tanggal.setObjectName("input_field")
        self.input_tanggal.setFixedHeight(42)
        self.input_tanggal.setCursor(Qt.PointingHandCursor)

        cal = self.input_tanggal.calendarWidget()
        cal.setGridVisible(False)
        cal.setVerticalHeaderFormat(cal.NoVerticalHeader)
        cal.setCursor(Qt.PointingHandCursor)
        for btn in cal.findChildren(QToolButton):
            btn.setCursor(Qt.PointingHandCursor)

        tanggal_layout.addWidget(self.label_tanggal)
        tanggal_layout.addWidget(self.input_tanggal)

        waktu_layout = QVBoxLayout()
        self.label_waktu = QLabel(lang.t("add_event.field_time_req"))
        self.label_waktu.setObjectName("label_field")
        self.input_waktu = QTimeEdit()
        self.input_waktu.setDisplayFormat("HH:mm")
        now    = QTime.currentTime()
        minute = 30 if now.minute() >= 30 else 0
        self.input_waktu.setTime(QTime(now.hour(), minute))
        try:
            self.input_waktu.setWrapping(True)
        except Exception:
            pass
        self.input_waktu.setObjectName("input_field")
        self.input_waktu.setFixedHeight(42)
        self.input_waktu.setCursor(Qt.PointingHandCursor)

        waktu_layout.addWidget(self.label_waktu)
        waktu_layout.addWidget(self.input_waktu)

        baris3_layout.addLayout(tanggal_layout)
        baris3_layout.addLayout(waktu_layout)
        form_layout.addLayout(baris3_layout)

        # ---- BARIS 4: LOKASI + NAMA KAMPUS ----
        baris4_layout = QHBoxLayout()
        baris4_layout.setSpacing(16)

        lokasi_layout = QVBoxLayout()
        self.label_lokasi = QLabel(lang.t("add_event.field_location_req"))
        self.label_lokasi.setObjectName("label_field")
        self.input_lokasi = QLineEdit()
        self.input_lokasi.setPlaceholderText(lang.t("add_event.ph_location"))
        self.input_lokasi.setObjectName("input_field")
        lokasi_layout.addWidget(self.label_lokasi)
        lokasi_layout.addWidget(self.input_lokasi)

        kampus_layout = QVBoxLayout()
        self.label_kampus = QLabel(lang.t("add_event.field_campus_req"))
        self.label_kampus.setObjectName("label_field")
        self.input_kampus = QLineEdit()
        self.input_kampus.setPlaceholderText(lang.t("add_event.ph_campus"))
        self.input_kampus.setObjectName("input_field")
        kampus_layout.addWidget(self.label_kampus)
        kampus_layout.addWidget(self.input_kampus)

        baris4_layout.addLayout(lokasi_layout)
        baris4_layout.addLayout(kampus_layout)
        form_layout.addLayout(baris4_layout)

        # ---- TIPE TIKET ----
        tiket_layout = QHBoxLayout()
        self.label_tiket = QLabel(lang.t("add_event.field_ticket_req"))
        self.label_tiket.setObjectName("label_field")
        self.toggle_tiket = ToggleSwitch()
        self.toggle_tiket.set_on(False)
        self.label_status_tiket = QLabel(lang.t("add_event.free"))
        self.label_status_tiket.setObjectName("label_status_tiket")
        self.toggle_tiket.toggled.connect(self.on_toggle_tiket)
        tiket_layout.addWidget(self.toggle_tiket)
        tiket_layout.addWidget(self.label_status_tiket)
        tiket_layout.addStretch()
        form_layout.addWidget(self.label_tiket)
        form_layout.addLayout(tiket_layout)

        self.harga_widget = QWidget()
        harga_layout = QVBoxLayout()
        harga_layout.setContentsMargins(0, 0, 0, 0)
        self.label_harga = QLabel(lang.t("add_event.field_price_req"))
        self.label_harga.setObjectName("label_field")
        self.input_harga = QLineEdit()
        self.input_harga.setPlaceholderText(lang.t("add_event.ph_price"))
        # QIntValidator(1, 999999999) = hanya angka dari 1 sampai 999999999
        # angka 0 tidak bisa karena minimum 1
        validator = QIntValidator(1, 999999999, self)
        self.input_harga.setValidator(validator)
        self.input_harga.setObjectName("input_field")
        harga_layout.addWidget(self.label_harga)
        harga_layout.addWidget(self.input_harga)
        self.harga_widget.setLayout(harga_layout)
        self.harga_widget.hide()
        form_layout.addWidget(self.harga_widget)
        form_layout.addStretch()

        # ---- POSTER ----
        poster_layout = QVBoxLayout()
        poster_layout.setContentsMargins(0, 60, 0, 0)
        poster_layout.setSpacing(8)
        poster_layout.setAlignment(Qt.AlignTop)

        self.label_poster = QLabel(lang.t("add_event.field_poster"))
        self.label_poster.setObjectName("label_field")
        font_poster = QFont("Inter SemiBold", 12)
        self.label_poster.setFont(font_poster)

        self.poster_preview = QWidget()
        self.poster_preview.setObjectName("poster_preview_area")
        self.poster_preview.setFixedSize(200, 280)
        self.poster_preview.setCursor(Qt.PointingHandCursor)

        poster_preview_layout = QVBoxLayout()
        poster_preview_layout.setAlignment(Qt.AlignCenter)
        poster_preview_layout.setSpacing(8)

        self.poster_preview_icon = QLabel("⬆")
        self.poster_preview_icon.setObjectName("poster_preview_icon")
        self.poster_preview_icon.setAlignment(Qt.AlignCenter)

        self.poster_preview_text = QLabel(lang.t("add_event.upload_hint"))
        self.poster_preview_text.setObjectName("poster_preview_text")
        self.poster_preview_text.setAlignment(Qt.AlignCenter)

        self.poster_preview_img = QLabel()
        self.poster_preview_img.setObjectName("poster_preview_img")
        self.poster_preview_img.setFixedSize(200, 280)
        self.poster_preview_img.setScaledContents(True)
        self.poster_preview_img.hide()

        poster_preview_layout.addWidget(self.poster_preview_icon)
        poster_preview_layout.addWidget(self.poster_preview_text)
        poster_preview_layout.addWidget(self.poster_preview_img)
        self.poster_preview.setLayout(poster_preview_layout)
        self.poster_preview.mousePressEvent = self.buka_dialog_upload

        poster_layout.addWidget(self.label_poster)
        poster_layout.addWidget(self.poster_preview)
        poster_layout.addStretch()

        garis_bawah = QWidget()
        garis_bawah.setFixedHeight(1)
        garis_bawah.setObjectName("garis_pemisah")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        self.btn_batal = QPushButton(lang.t("btn.cancel"))
        self.btn_batal.setObjectName("btn_batal")
        self.btn_batal.setFixedSize(120, 45)
        self.btn_batal.setCursor(Qt.PointingHandCursor)
        font_btn = QFont("Inter Medium", 13)
        self.btn_batal.setFont(font_btn)
        self.btn_batal.clicked.connect(self.dibatalkan.emit)

        self.btn_publikasi = QPushButton(lang.t("add_event.btn_publish_full"))
        self.btn_publikasi.setObjectName("btn_publikasi")
        self.btn_publikasi.setFixedSize(160, 45)
        self.btn_publikasi.setCursor(Qt.PointingHandCursor)
        self.btn_publikasi.setFont(font_btn)
        self.btn_publikasi.clicked.connect(self.publikasi_event)

        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_publikasi)

        konten_layout = QHBoxLayout()
        konten_layout.setSpacing(48)
        konten_layout.addLayout(form_layout, stretch=2)
        konten_layout.addLayout(poster_layout, stretch=1)

        card_inner_layout = QVBoxLayout()
        card_inner_layout.setContentsMargins(24, 24, 24, 24)
        card_inner_layout.setSpacing(16)
        card_inner_layout.addLayout(konten_layout)
        card_inner_layout.addSpacing(8)
        card_inner_layout.addWidget(garis_bawah)
        card_inner_layout.addLayout(btn_layout)

        self.card.setLayout(card_inner_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        scroll.setWidget(self.card)

        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)

    # ----------------------------------------------------------
    def on_toggle_tiket(self, is_on):
        if is_on:
            self.label_status_tiket.setText(lang.t("add_event.paid"))
            self.harga_widget.show()
        else:
            self.label_status_tiket.setText(lang.t("add_event.free"))
            self.harga_widget.hide()

    # ----------------------------------------------------------
    def reset_form(self):
        self.input_nama.clear()
        self.input_deskripsi.clear()
        self.input_kategori.clear()
        self.input_tanggal.clear()
        now    = QTime.currentTime()
        minute = 30 if now.minute() >= 30 else 0
        self.input_waktu.setTime(QTime(now.hour(), minute))
        self.input_lokasi.clear()
        self.input_kampus.clear()
        self.input_harga.clear()

        self.jenis_terpilih = ""
        self.input_jenis.setText(lang.t("add_event.select_type"))
        self.input_jenis.setLayoutDirection(Qt.RightToLeft)
        self.input_jenis.setIcon(QIcon("assets/icons/arrow_down.png"))
        self.input_jenis.setIconSize(QSize(12, 12))

        self.toggle_tiket.set_on(False)
        self.toggle_tiket.setCursor(Qt.PointingHandCursor)
        self.label_status_tiket.setText(lang.t("add_event.free"))
        self.harga_widget.hide()

        self.poster_path = ""
        self.poster_preview_icon.show()
        self.poster_preview_text.show()
        self.poster_preview_img.hide()
        self.poster_preview_img.clear()
        self.poster_preview.setStyleSheet("")

    # ----------------------------------------------------------
    def on_poster_dipilih(self, path):
        self.poster_path = path
        pixmap = QPixmap(path)
        self.poster_preview_img.setPixmap(pixmap)
        self.poster_preview_icon.hide()
        self.poster_preview_text.hide()
        self.poster_preview_img.show()
        self.poster_preview.setStyleSheet("""
            QWidget { border: none; border-radius: 8px; background-color: transparent; }
        """)
        self.poster_preview_img.setFixedSize(
            self.poster_preview.width(),
            self.poster_preview.height()
        )

    # ----------------------------------------------------------
    def buka_dialog_upload(self, event):
        from upload_widget import PosterUploadDialog
        dialog = PosterUploadDialog(self)
        dialog.gambar_dipilih.connect(self.on_poster_dipilih)
        dialog.exec_()

    # ----------------------------------------------------------
    def publikasi_event(self):
        """
        Validasi form lalu emit sinyal event_dipublikasi.

        PATCH (vs versi asli):
          - Saat mode edit (self.data_event tidak None), sertakan
            'event_id' asli dan pertahankan 'status' lama agar
            setting_window._simpan_perubahan_event() bisa menemukan
            row yang tepat di database (WHERE event_id = ?).
          - Mode create tetap mengirim status = "pending".

        FIX MULTILINGUAL:
          - Semua pesan error validasi sekarang menggunakan lang.t()
        """

        # ---- VALIDASI ----
        if not self.jenis_terpilih:
            self.tampilkan_error(lang.t("add_event.err_select_type"))
            return

        # FIX #2 — setiap field punya key lang sendiri, tidak campur bahasa
        text_fields = [
            (lang.t("add_event.err_name_required"),     self.input_nama),
            (lang.t("add_event.err_desc_required"),     self.input_deskripsi),
            (lang.t("add_event.err_category_required"), self.input_kategori),
            (lang.t("add_event.err_location_required"), self.input_lokasi),
            (lang.t("add_event.err_campus_required"),   self.input_kampus),
        ]
        for pesan_error, field in text_fields:
            if not field.text().strip():
                self.tampilkan_error(pesan_error)
                return

        tanggal = self.input_tanggal.date().toString("yyyy-MM-dd")
        waktu   = self.input_waktu.time().toString("HH:mm")

        # ---- VALIDASI TANGGAL & WAKTU ----
        tanggal_pilih    = self.input_tanggal.date()
        waktu_pilih      = self.input_waktu.time()
        tanggal_sekarang = QDate.currentDate()
        waktu_sekarang   = QTime.currentTime()

        # 1. Tidak boleh pilih tanggal yang sudah lewat
        if tanggal_pilih < tanggal_sekarang:
            # FIX #3 — gunakan key yang sudah ada
            self.tampilkan_error(lang.t("add_event.err_date_past"))
            return

        # 2. Jika tanggal hari ini, jam tidak boleh lewat (khusus mode create).
        # Untuk mode edit, event lama bisa saja sudah berlalu namun tetap boleh diedit
        # (mis. perbaikan deskripsi/poster) sebelum dikirim ulang ke admin.
        if tanggal_pilih == tanggal_sekarang and not self.data_event:
            if waktu_pilih < waktu_sekarang:
                self.tampilkan_error(lang.t("add_event.err_time_past"))
                return

        if not tanggal.strip():
            self.tampilkan_error(lang.t("add_event.err_date_empty"))
            return

        if not waktu.strip():
            # FIX #4 — gunakan key yang sudah ada
            self.tampilkan_error(lang.t("add_event.err_time_empty"))
            return

        if self.toggle_tiket.is_on() and not self.input_harga.text().strip():
            self.tampilkan_error(lang.t("add_event.err_price_empty"))
            return

        if not self.poster_path:
            self.tampilkan_error(lang.t("add_event.err_upload_poster"))
            return

        # Validasi tambahan harga tiket
        if self.toggle_tiket.is_on():
            harga_text = self.input_harga.text().strip()

            if not harga_text:
                self.tampilkan_error(lang.t("add_event.err_price_empty"))
                return

            if int(harga_text) < 1000:
                self.tampilkan_error(lang.t("add_event.err_price_min"))
                return

        # ---- BANGUN DICT ----
        data_event = {
            "nama_event"       : self.input_nama.text().strip(),
            "jenis_event"      : self.jenis_terpilih,
            "deskripsi_singkat": self.input_deskripsi.text().strip(),
            "kategori"         : self.input_kategori.text().strip(),
            "tanggal"          : tanggal,
            "waktu"            : waktu,
            "lokasi"           : self.input_lokasi.text().strip(),
            "penyelenggara"    : self.input_kampus.text().strip(),
            "tipe_tiket"       : "Paid" if self.toggle_tiket.is_on() else "Free",
            "harga_tiket"      : self.input_harga.text().strip() if self.toggle_tiket.is_on() else "0",
            "gambar_poster"    : self.poster_path,
            "source"           : "Manual Input",
        }

        # ── PATCH: sisipkan event_id & status saat mode edit ──────────
        if self.data_event:
            # Mode edit — sertakan event_id asli agar UPDATE WHERE bisa
            # menemukan baris yang tepat di database
            data_event["event_id"] = self.data_event.get("event_id", "")
            # Pertahankan status lama (misal "approved") agar tidak
            # kembali ke "pending" setelah disimpan
            data_event["status"] = self.data_event.get("status", "approved")
        else:
            # Mode create — perlu validasi admin dulu
            data_event["status"] = "pending"
        # ──────────────────────────────────────────────────────────────

        self.event_dipublikasi.emit(data_event)

    # ----------------------------------------------------------
    def tampilkan_error(self, pesan):
        teks = (pesan or lang.t("add_event.err_required_check")).strip()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(lang.t("add_event.validation_failed"))
        msg.setText(teks)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QMessageBox QLabel { color: #1a1a1a; min-width: 320px; }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 6px 12px;
                border: 1px solid #CBD5E0;
                border-radius: 6px;
                background-color: #f8fafc;
                color: #1a1a1a;
            }
            QMessageBox QPushButton:hover { background-color: #eef2f7; }
        """)
        msg.exec_()

    # ----------------------------------------------------------
    def pilih_jenis(self, jenis):
        self.input_jenis.setText(jenis)
        self.jenis_terpilih = jenis

    # ----------------------------------------------------------
    def _prefill_form(self, data):
        self.judul_label.setText(lang.t("add_event.title_edit"))
        self.sub_judul.setText(lang.t("add_event.subtitle_edit"))
        self.btn_publikasi.setText(lang.t("add_event.btn_save_changes"))

        self.input_nama.setText(data.get("nama_event", ""))
        self.input_deskripsi.setText(data.get("deskripsi_singkat", ""))
        self.input_kategori.setText(data.get("kategori", ""))

        tanggal_str = data.get("tanggal_waktu", "")[:10]
        if tanggal_str:
            try:
                tgl = QDate.fromString(tanggal_str, "yyyy-MM-dd")
                if tgl.isValid():
                    self.input_tanggal.setDate(tgl)
            except Exception:
                pass

        waktu_str = data.get("waktu_display", "")
        if waktu_str:
            try:
                wkt = QTime.fromString(waktu_str, "HH:mm")
                if not wkt.isValid():
                    wkt = QTime.fromString(waktu_str, "h AP")
                if wkt.isValid():
                    self.input_waktu.setTime(wkt)
            except Exception:
                pass

        self.input_lokasi.setText(data.get("lokasi", ""))
        self.input_kampus.setText(data.get("nama_eo", data.get("penyelenggara", "")))

        jenis = data.get("jenis_event", "")
        if jenis:
            self.input_jenis.setText(jenis)
            self.jenis_terpilih = jenis

        if data.get("tipe_tiket", "Free") not in ("Free", "Gratis", ""):
            self.toggle_tiket.set_on(True)
            self.input_harga.setText(data.get("harga_tiket", ""))

        poster = data.get("gambar_poster", "")
        if poster and os.path.exists(poster):
            self.poster_path = poster
            pixmap = QPixmap(poster)
            self.poster_preview_img.setPixmap(pixmap)
            self.poster_preview_icon.hide()
            self.poster_preview_text.hide()
            self.poster_preview_img.show()

    # ----------------------------------------------------------
    def _retranslate(self, _code: str = ""):
        is_edit = bool(self.data_event)
        self.judul_label.setText(lang.t("add_event.title_edit") if is_edit else lang.t("add_event.title_new"))
        self.sub_judul.setText(lang.t("add_event.subtitle_edit") if is_edit else lang.t("add_event.subtitle_new"))
        self.label_info.setText(lang.t("add_event.section_main"))
        self.label_nama.setText(lang.t("add_event.field_name_req"))
        self.input_nama.setPlaceholderText(lang.t("add_event.ph_name"))
        self.label_jenis.setText(lang.t("add_event.field_type_req"))
        if not self.jenis_terpilih:
            self.input_jenis.setText(lang.t("add_event.select_type"))
        # FIX #1 — retranslate teks menu Internal/External
        self.action_internal.setText(lang.t("detail.internal"))
        self.action_external.setText(lang.t("detail.external"))
        self.label_deskripsi.setText(lang.t("add_event.field_desc_req"))
        self.input_deskripsi.setPlaceholderText(lang.t("add_event.ph_desc"))
        self.label_kategori.setText(lang.t("add_event.field_category_req"))
        self.input_kategori.setPlaceholderText(lang.t("add_event.ph_category"))
        self.label_waktu_tempat.setText(lang.t("add_event.section_time_venue"))
        self.label_tanggal.setText(lang.t("add_event.field_date_req"))
        self.label_waktu.setText(lang.t("add_event.field_time_req"))
        self.label_lokasi.setText(lang.t("add_event.field_location_req"))
        self.input_lokasi.setPlaceholderText(lang.t("add_event.ph_location"))
        self.label_kampus.setText(lang.t("add_event.field_campus_req"))
        self.input_kampus.setPlaceholderText(lang.t("add_event.ph_campus"))
        self.label_tiket.setText(lang.t("add_event.field_ticket_req"))
        self.label_harga.setText(lang.t("add_event.field_price_req"))
        self.input_harga.setPlaceholderText(lang.t("add_event.ph_price"))
        self.label_poster.setText(lang.t("add_event.field_poster"))
        self.poster_preview_text.setText(lang.t("add_event.upload_hint"))
        self.btn_batal.setText(lang.t("btn.cancel"))
        self.btn_publikasi.setText(lang.t("add_event.btn_save_changes") if is_edit else lang.t("add_event.btn_publish_full"))
        self.update_label_tiket()

    # ----------------------------------------------------------
    def update_label_tiket(self):
        if self.toggle_tiket.is_on():
            self.label_status_tiket.setText(lang.t("add_event.paid"))
        else:
            self.label_status_tiket.setText(lang.t("add_event.free"))

    # ----------------------------------------------------------
    def apply_style(self):
        font_label = QFont("Inter", 12)
        font_label.setWeight(QFont.Bold)
        for label in [
            self.label_nama, self.label_jenis,
            self.label_deskripsi, self.label_kategori,
            self.label_tanggal, self.label_waktu,
            self.label_lokasi, self.label_kampus,
            self.label_tiket, self.label_harga,
            self.label_poster,
        ]:
            label.setFont(font_label)

        font_input = QFont("Inter", 13)
        font_input.setWeight(QFont.Normal)
        for inp in [
            self.input_nama, self.input_deskripsi,
            self.input_kategori, self.input_tanggal,
            self.input_waktu, self.input_lokasi,
            self.input_kampus, self.input_harga,
        ]:
            inp.setFont(font_input)

        self.input_jenis.setFont(font_input)

        self.setStyleSheet("""
            QWidget#add_event_page { background-color: transparent; }
            QLabel#judul_label { color: #516465; font-size: 24px; }
            QLabel#sub_judul   { color: #4A5568; font-size: 12px; }
            QWidget#form_widget { background-color: white; border-radius: 12px; border: none; }
            QLabel#label_section { color: #2D3748; font-size: 11px; letter-spacing: 1px; }
            QWidget#garis_pemisah { background-color: #E5E7EB; }
            QLabel#label_field { color: #2D3748; font-size: 12px; }
            QLineEdit#input_field, QDateEdit#input_field, QTimeEdit#input_field {
                background-color: white; border: 1px solid #CBD5E0;
                border-radius: 8px; padding: 10px 12px;
                font-size: 13px; color: #000000;
            }
            QLineEdit#input_field:focus, QDateEdit#input_field:focus, QTimeEdit#input_field:focus {
                border: 1px solid #2D6A6A;
            }
            QPushButton#input_combo {
                background-color: white; border: 1px solid #CBD5E0;
                border-radius: 8px; padding: 10px 14px; padding-right: 28px;
                text-align: left; font-size: 13px; color: #1a1a1a;
            }
            QPushButton#input_combo:focus { border: 1px solid #2D6A6A; }
            QLabel#label_status_tiket { color: #747C86; font-size: 13px; }
            QPushButton#btn_batal {
                background-color: white; color: #4A5568;
                border: 1px solid #CBD5E0; border-radius: 8px; font-size: 13px;
            }
            QPushButton#btn_batal:hover { background-color: #f0f0f0; }
            QPushButton#btn_publikasi {
                background-color: #2D6A6A; color: white;
                border: none; border-radius: 8px; font-size: 13px; font-weight: bold;
            }
            QPushButton#btn_publikasi:hover { background-color: #3a7a7a; }
            QWidget#poster_preview_area {
                background-color: #F0F7F7;
                border: 2px dashed #B0CECE; border-radius: 8px;
            }
            QLabel#poster_preview_icon { font-size: 24px; color: #5D6B6B; }
            QLabel#poster_preview_text { font-size: 11px; color: #888888; }
            QCalendarWidget {
                background-color: white; border-radius: 10px;
                border: 1px solid #CBD5E0;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2D6A6A; border-radius: 8px; padding: 4px;
            }
            QCalendarWidget QToolButton {
                background-color: transparent; color: white;
                font-size: 13px; font-weight: bold;
                border: none; border-radius: 6px; padding: 4px 8px;
            }
            QCalendarWidget QToolButton:hover { background-color: rgba(255,255,255,0.2); }
            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {
                color: white; font-size: 14px; font-weight: bold;
            }
            QCalendarWidget QHeaderView { background-color: #D2E6E5; }
            QCalendarWidget QHeaderView::section {
                background-color: #D2E6E5; color: #516465;
                font-size: 12px; font-weight: bold; padding: 4px; border: none;
            }
            QCalendarWidget QAbstractItemView {
                background-color: white; color: #1a1a1a;
                font-size: 13px;
                selection-background-color: #2D6A6A;
                selection-color: white; outline: none;
            }
            QCalendarWidget QAbstractItemView::item:selected {
                background-color: #2D6A6A; color: white; border-radius: 6px;
            }
            QCalendarWidget QAbstractItemView::item:hover {
                background-color: #D2E6E5; border-radius: 6px;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #CBD5E0; }
            QCalendarWidget QMenu {
                background-color: white; border: 1px solid #CBD5E0;
                border-radius: 8px; padding: 4px; font-size: 13px; color: #1a1a1a;
            }
            QCalendarWidget QMenu::item { padding: 6px 12px; border-radius: 6px; margin: 2px 4px; }
            QCalendarWidget QMenu::item:selected { background-color: #D2E6E5; color: #2D6A6A; }
            QCalendarWidget QSpinBox {
                background-color: transparent; color: white;
                border: none; font-size: 13px; font-weight: bold; padding: 0px 4px;
            }
            QCalendarWidget QSpinBox::up-button,
            QCalendarWidget QSpinBox::down-button { width: 0px; height: 0px; border: none; }
        """)
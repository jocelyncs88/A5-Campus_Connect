# ==============================================================
# FILE: admin_page.py
# TUGAS: Halaman Dashboard Validasi untuk Admin
# FITUR: Tabel antrean event dengan tombol Approve & Decline
# ==============================================================

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class AdminPage(QWidget):
    # Sinyal untuk komunikasi dengan main_window.py
    kembali_diklik = pyqtSignal()
    # Sinyal ini akan mengirimkan ID Event dan Status barunya ("approved" / "rejected")
    validasi_diklik = pyqtSignal(str, str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_style()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        # ---- HEADER ----
        header_layout = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        self.judul_label = QLabel("Dashboard Validasi Event")
        self.judul_label.setObjectName("judul")
        self.sub_judul = QLabel("Kelola antrean pengajuan event dari Event Organizer")
        self.sub_judul.setObjectName("sub_judul")
        
        title_layout.addWidget(self.judul_label)
        title_layout.addWidget(self.sub_judul)
        
        self.btn_kembali = QPushButton("← Kembali ke Home")
        self.btn_kembali.setObjectName("btn_kembali")
        self.btn_kembali.setCursor(Qt.PointingHandCursor)
        self.btn_kembali.clicked.connect(self.kembali_diklik.emit)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_kembali)

        layout.addLayout(header_layout)

        # ---- TABEL VALDASI ----
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(5)
        self.tabel.setHorizontalHeaderLabels(["ID Event", "Nama Event", "Tipe", "Waktu", "Aksi Validasi"])
        
        # Pengaturan agar tabel responsif dan rapi
        header = self.tabel.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Kolom ID pas konten
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Kolom Nama melar
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Kolom Tipe
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Kolom Waktu
        header.setSectionResizeMode(4, QHeaderView.Fixed)            # Kolom Aksi
        self.tabel.setColumnWidth(4, 200)

        # Mencegah user mengedit teks di dalam tabel secara manual
        self.tabel.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.tabel)

    def load_data_antrean(self):
        """Menarik data event yang berstatus 'pending' dari database"""
        import db_manager  # Import db_manager untuk narik data

        # Ambil data dari database yang antre (pending)
        data_pending = db_manager.get_events_by_status("pending")
        
        # Kosongkan tabel sebelum diisi ulang
        self.tabel.setRowCount(0)
        self.tabel.setRowCount(len(data_pending))

        # Struktur data dari DB: (0:id, 1:event_id, 2:nama_event, 3:deskripsi, 
        # 4:poster, 5:jenis_event, 6:waktu, 7:source, 8:kategori, 9:status)
        
        for row_idx, row in enumerate(data_pending):
            evt_id = row.get("event_id", "")
            nama_event = row.get("nama_event", "")
            jenis = row.get("jenis_event", "")
            waktu = row.get("tanggal_waktu", "")

            # Masukkan teks ke sel tabel
            kolom_data = [evt_id, nama_event, jenis, waktu]
            for col_idx, isi_teks in enumerate(kolom_data):
                item = QTableWidgetItem(str(isi_teks))
                item.setTextAlignment(Qt.AlignCenter if col_idx != 1 else Qt.AlignVCenter)
                self.tabel.setItem(row_idx, col_idx, item)

            # --- BUAT TOMBOL ACTION ---
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)
            action_layout.setSpacing(10)

            btn_approve = QPushButton("✓ Approve")
            btn_approve.setObjectName("btn_approve")
            btn_approve.setCursor(Qt.PointingHandCursor)
            # Kirim evt_id ke main_window saat diklik
            btn_approve.clicked.connect(lambda checked, eid=evt_id: self.validasi_diklik.emit(eid, "approved"))

            btn_decline = QPushButton("✗ Decline")
            btn_decline.setObjectName("btn_decline")
            btn_decline.setCursor(Qt.PointingHandCursor)
            btn_decline.clicked.connect(lambda checked, eid=evt_id: self.validasi_diklik.emit(eid, "rejected"))

            action_layout.addWidget(btn_approve)
            action_layout.addWidget(btn_decline)
            
            self.tabel.setCellWidget(row_idx, 4, action_widget)
            
    def apply_style(self):
        self.setStyleSheet("""
            QLabel#judul { font-size: 28px; font-weight: bold; color: #516465; }
            QLabel#sub_judul { font-size: 14px; color: #708080; }
            
            QPushButton#btn_kembali {
                background-color: transparent; color: #5D6B6B;
                border: 1.5px solid #CBD5E0; border-radius: 8px; padding: 8px 15px; font-weight: bold;
            }
            QPushButton#btn_kembali:hover { background-color: #D2E6E5; }
            
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.7); border: 1px solid #CBD5E0;
                border-radius: 10px; font-size: 14px;
            }
            QHeaderView::section {
                background-color: #D2E6E5; color: #516465; font-weight: bold;
                padding: 10px; border: none; border-right: 1px solid #CBD5E0;
            }
            
            QPushButton#btn_approve {
                background-color: #2D6A6A; color: white; border-radius: 5px; padding: 5px; font-weight: bold;
            }
            QPushButton#btn_approve:hover { background-color: #3a7a7a; }
            
            QPushButton#btn_decline {
                background-color: #e53e3e; color: white; border-radius: 5px; padding: 5px; font-weight: bold;
            }
            QPushButton#btn_decline:hover { background-color: #fc8181; }
        """)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class FAQAccordionItem(QWidget):
    def __init__(self, question, answer):
        super().__init__()
        
        # Buat Layout Vertikal untuk satu pasang Q & A
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 1. Komponen Pertanyaan (Menggunakan QPushButton agar bisa diklik)
        # Kita tambahkan simbol ▼ sebagai indikator visual
        self.btn_question = QPushButton(f"▼  {question}")
        self.btn_question.setCursor(Qt.PointingHandCursor)
        
        # Styling tombol agar terlihat seperti teks biasa (rata kiri)
        self.btn_question.setStyleSheet("""
            QPushButton {
                background: transparent;
                font-size: 20px;
                font-weight: bold;
                color: #516465;
                text-align: left;
                border: none;
                padding: 5px 0px;
            }
            QPushButton:hover {
                color: #F7CBCA; /* Warna pink saat di-hover */
            }
        """)
        
        # Hubungkan aksi klik dengan fungsi toggle
        self.btn_question.clicked.connect(self.toggle_answer)

        # 2. Komponen Jawaban (Menggunakan QLabel)
        self.lbl_answer = QLabel(answer)
        self.lbl_answer.setWordWrap(True)
        self.lbl_answer.setStyleSheet("""
            background: transparent;
            font-size: 15px;
            color: #667777;
            padding-left: 28px; /* Diberi jarak agar sejajar dengan teks, bukan panah */
            padding-bottom: 10px;
        """)
        
        # KUNCI ACCORDION: Sembunyikan jawaban secara default
        self.lbl_answer.setVisible(False)

        # Masukkan ke layout
        layout.addWidget(self.btn_question)
        layout.addWidget(self.lbl_answer)

    def toggle_answer(self):
        """Fungsi untuk memunculkan/menyembunyikan jawaban saat tombol diklik"""
        # Cek status saat ini (apakah sedang terlihat?)
        is_visible = self.lbl_answer.isVisible()
        
        # Ubah status visibilitas ke kebalikannya (True jadi False, False jadi True)
        self.lbl_answer.setVisible(not is_visible)
        
        # Animasi UX sederhana: Ubah arah panah
        if is_visible:
            # Jika sebelumnya terlihat, berarti sekarang disembunyikan -> panah ke bawah
            self.btn_question.setText(self.btn_question.text().replace("▲", "▼"))
        else:
            # Jika sebelumnya sembunyi, berarti sekarang dimunculkan -> panah ke atas
            self.btn_question.setText(self.btn_question.text().replace("▼", "▲"))

class FAQPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: Segoe UI;
                color: #4F5F60;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 20, 50, 20)
        layout.setSpacing(18)

        # TITLE
        title = QLabel("Frequently Asked Questions")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: #516465;
        """)

        subtitle = QLabel("Pusat Bantuan Campus Connect")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #708080;
        """)

        # MAIN CARD — tanpa padding di stylesheet (bentrok sama setContentsMargins)
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.35);
                border-radius: 24px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(18)

        faqs = [
            (
                "Apa itu Campus Connect?",
                "Campus Connect adalah aplikasi desktop yang membantu mahasiswa menemukan informasi event kampus secara cepat, mudah, dan terpusat."
            ),
            (
                "Bagaimana cara menambahkan event?",
                "Pengguna dapat menambahkan event melalui menu Add Event pada bagian kanan atas aplikasi."
            ),
            (
                "Apakah saya harus login terlebih dahulu?",
                "Beberapa fitur tertentu mungkin memerlukan proses login terlebih dahulu untuk keamanan akun."
            ),
            (
                "Apakah bisa melihat event yang akan datang?",
                "Ya, seluruh event yang akan datang dapat dilihat langsung pada halaman utama aplikasi."
            ),
            (
                "Siapa pengembang aplikasi ini?",
                "Aplikasi ini dikembangkan oleh kelompok A5 Informatika POLBAN sebagai proyek pengembangan perangkat lunak."
            )
        ]

        for i, (q, a) in enumerate(faqs):
            item = self.create_item(q, a)
            card_layout.addWidget(item)

            if i != len(faqs) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFixedHeight(1)
                line.setStyleSheet("background-color: rgba(80,100,100,0.12); border: none;")
                card_layout.addWidget(line)

        footer = QLabel("© 2026 Campus Connect Team")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            font-size: 12px;
            color: #8A9A9A;
            margin-top: 8px;
        """)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(card)
        layout.addSpacing(8)
        layout.addWidget(footer)

    def create_item(self, question, answer):
        item_widget = FAQAccordionItem(question, answer)
        return item_widget


# TEST
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    window = QWidget()
    window.resize(1400, 800)
    window.setWindowTitle("FAQ Fixed")
    window.setStyleSheet("""
        background:qlineargradient(
            x1:0,y1:0,x2:0,y2:1,
            stop:0 #BDD7D8,
            stop:1 #F7CBCA
        );
    """)

    layout = QVBoxLayout(window)
    layout.setContentsMargins(30, 30, 30, 30)

    faq = FAQPage()
    layout.addWidget(faq)

    window.show()
    sys.exit(app.exec_())
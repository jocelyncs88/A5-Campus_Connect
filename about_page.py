from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ── COLOR ───────────────────────────────
C_TITLE   = "#516465"
C_SUB     = "#708080"
C_BODY    = "#667777"
C_FOOTER  = "#8A9A9A"
C_PRIMARY = "#1f5555"
C_AVATAR  = "#b7ecec"
C_NAME    = "#0e1d25"


# ── AVATAR ─────────────────────────────
class Avatar(QWidget):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.setFixedSize(40, 40)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(C_AVATAR))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, 40, 40)

        p.setPen(QColor(C_PRIMARY))
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, self.text)


# ── LINE ───────────────────────────────
class Line(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(1)
        # FIX: gunakan selector spesifik QFrame agar tidak bocor ke child
        self.setObjectName("dividerLine")
        self.setStyleSheet("QFrame#dividerLine { background: rgba(80,100,100,0.15); border: none; }")


# ── PAGE ───────────────────────────────
class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            /* FIX GLOBAL: pastikan semua QLabel di page ini transparent */
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        self.setProperty("class", "aboutPage")
        self.setFont(QFont("Segoe UI"))
        self.build()

    def build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 20, 32, 20)
        root.setSpacing(0)

        root.addStretch(1)

        # ===== TITLE =====
        t_wrap = QVBoxLayout()
        t_wrap.setSpacing(4)

        title = QLabel("About Us")
        title.setAlignment(Qt.AlignCenter)
        # FIX: tambahkan background:transparent & border:none eksplisit
        title.setStyleSheet(f"font-size:34px; font-weight:bold; color:{C_TITLE}; background:transparent; border:none;")

        sub = QLabel("Campus Connect")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size:14px; color:{C_SUB}; background:transparent; border:none;")

        tag = QLabel("Connecting students with campus opportunities")
        tag.setAlignment(Qt.AlignCenter)
        tag.setStyleSheet(f"font-size:12px; color:{C_FOOTER}; background:transparent; border:none;")

        t_wrap.addWidget(title)
        t_wrap.addWidget(sub)
        t_wrap.addWidget(tag)

        root.addLayout(t_wrap)
        root.addSpacing(18)

        # ===== CARD =====
        card = QFrame()
        card.setObjectName("mainCard")
        card.setStyleSheet("""
            QFrame#mainCard {
                background: rgba(255,255,255,0.45);
                border-radius: 24px;
                border: none;
            }
        """)

        cv = QVBoxLayout(card)
        cv.setContentsMargins(36, 32, 36, 32)
        cv.setSpacing(0)

        self.section(cv, "ℹ", "About the Application",
            "Campus Connect adalah aplikasi desktop yang membantu mahasiswa menemukan "
            "informasi event kampus secara cepat, mudah, dan terpusat. Dirancang untuk "
            "menjembatani kesibukan akademik dengan kehidupan sosial kampus.")

        cv.addSpacing(20)
        cv.addWidget(Line())
        cv.addSpacing(20)

        self.section(cv, "🚀", "Our Mission",
            "Meningkatkan akses informasi kegiatan kampus dan mendorong keterlibatan "
            "mahasiswa agar berkembang di luar kelas.")

        cv.addSpacing(20)
        cv.addWidget(Line())
        cv.addSpacing(20)

        self.team(cv)

        root.addWidget(card)

        # ===== FOOTER =====
        root.addSpacing(30)

        f_wrap = QVBoxLayout()
        f_wrap.setSpacing(4)

        f_title = QLabel("Campus Connect")
        f_title.setAlignment(Qt.AlignCenter)
        f_title.setStyleSheet(f"font-size:14px; font-weight:bold; color:{C_TITLE}; background:transparent; border:none;")

        f_text = QLabel("© 2026 Campus Connect. Academic Serenity for the Modern Student.")
        f_text.setAlignment(Qt.AlignCenter)
        f_text.setStyleSheet(f"font-size:11px; color:{C_FOOTER}; background:transparent; border:none;")

        f_wrap.addWidget(f_title)
        f_wrap.addWidget(f_text)

        root.addLayout(f_wrap)

        root.addStretch(2)

    # ===== SECTION =====
    def section(self, layout, icon, title, text):
        row = QHBoxLayout()
        row.setSpacing(10)

        i = QLabel(icon)
        i.setFixedSize(26, 26)
        i.setAlignment(Qt.AlignCenter)
        # FIX: tambahkan background:transparent & border:none
        i.setStyleSheet(f"font-size:16px; color:{C_PRIMARY}; background:transparent; border:none;")

        t = QLabel(title)
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{C_TITLE}; background:transparent; border:none;")

        row.addWidget(i)
        row.addWidget(t)
        row.addStretch()

        layout.addLayout(row)
        layout.addSpacing(10)

        body = QLabel(text)
        body.setWordWrap(True)
        body.setStyleSheet(f"font-size:14px; color:{C_BODY}; background:transparent; border:none;")

        layout.addWidget(body)

    # ===== TEAM =====
    def team(self, layout):
        row = QHBoxLayout()

        i = QLabel("👥")
        i.setFixedSize(26, 26)
        i.setAlignment(Qt.AlignCenter)
        # FIX: eksplisit transparent
        i.setStyleSheet("background:transparent; border:none;")

        t = QLabel("Development Team")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{C_TITLE}; background:transparent; border:none;")

        row.addWidget(i)
        row.addWidget(t)
        row.addStretch()

        layout.addLayout(row)
        layout.addSpacing(14)

        sub = QLabel("INFORMATICS A5 TEAM")
        sub.setStyleSheet(f"font-size:11px; color:{C_SUB}; letter-spacing:2px; background:transparent; border:none;")
        layout.addWidget(sub)
        layout.addSpacing(12)

        members = [
            ("AF","Arsel Fahri Khadafi"),
            ("JS","Jocelyn Christina Simamora"),
            ("MR","Muhammad Rafi Al Rabbani"),
            ("MS","Muhammad Salman Al Farisi"),
            ("TR","Tania Putri Ramadhani"),
        ]

        # QGridLayout dengan 2 kolom equal — semua card otomatis sama lebar
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for idx, m in enumerate(members):
            row_i = idx // 2
            col_i = idx % 2
            grid.addWidget(self.card(m[0], m[1]), row_i, col_i)

        layout.addLayout(grid)

    # ===== MEMBER CARD =====
    def card(self, init, name):
        w = QWidget()
        w.setFixedHeight(56)
        w.setObjectName("memberCard")
        w.setStyleSheet("""
            QWidget#memberCard {
                background: rgba(255,255,255,0.6);
                border-radius: 12px;
                border: 1px solid rgba(80,100,100,0.15);
            }
        """)

        h = QHBoxLayout(w)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(10)

        h.addWidget(Avatar(init))

        lbl = QLabel(name)
        # FIX: eksplisit transparent & border:none pada label nama
        lbl.setStyleSheet(f"font-size:13px; color:{C_NAME}; background:transparent; border:none;")
        h.addWidget(lbl)

        h.addStretch()

        return w
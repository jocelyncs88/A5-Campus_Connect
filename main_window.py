from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #4F5F60;
                font-family: Segoe UI;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(18)

        # TITLE
        title = QLabel("About Us")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #516465;
        """)

        subtitle = QLabel("Campus Connect")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 28px;
            font-weight: 600;
            color: #5D6B6B;
        """)

        desc = QLabel(
            "Campus Connect adalah aplikasi desktop yang membantu mahasiswa "
            "menemukan informasi event kampus secara cepat, mudah, dan terpusat."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("""
            font-size: 22px;
            font-weight: 500;
            color: #667777;
            padding: 5px 90px;
        """)

        mission = QLabel(
            "Tujuan kami adalah meningkatkan akses informasi kegiatan kampus "
            "serta mendorong mahasiswa agar lebih aktif dan terhubung."
        )
        mission.setWordWrap(True)
        mission.setAlignment(Qt.AlignCenter)
        mission.setStyleSheet("""
            font-size: 20px;
            font-weight: 500;
            color: #708080;
            padding: 0px 100px;
        """)

        # TEAM TITLE
        dev_title = QLabel("Development Team")
        dev_title.setAlignment(Qt.AlignCenter)
        dev_title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #516465;
            margin-top: 10px;
        """)

        # TEAM GRID
        team_container = QWidget()
        team_layout = QGridLayout(team_container)
        team_layout.setContentsMargins(60, 10, 60, 10)
        team_layout.setHorizontalSpacing(60)
        team_layout.setVerticalSpacing(14)

        members = [
            "Arsel Fahri Khadafi (251524002)",
            "Jocelyn Christina Simamora (251524016)",
            "Muhammad Rafi Al Rabbani (251524025)",
            "Muhammad Salman Al Farisi (251524026)",
            "Tania Putri Ramadhani (251524031)"
        ]

        positions = [
            (0, 0),
            (1, 0),
            (2, 0),
            (0, 1),
            (1, 1)
        ]

        for i, member in enumerate(members):
            label = QLabel("• " + member)
            label.setStyleSheet("""
                font-size: 18px;
                color: #4F5F60;
            """)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            row, col = positions[i]
            team_layout.addWidget(label, row, col)

        footer = QLabel("© 2026 Campus Connect Team")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            font-size: 13px;
            color: #8A9A9A;
            margin-top: 10px;
        """)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(desc)
        layout.addWidget(mission)
        layout.addSpacing(10)
        layout.addWidget(dev_title)
        layout.addWidget(team_container)
        layout.addStretch()
        layout.addWidget(footer)
import os
from language_manager import lang

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ── COLOR ───────────────────────────────
C_TITLE   = "#516465"
C_SUB     = "#708080"
C_BODY    = "#667777"
C_MUTED = "#8A9A9A"
C_CARD = "rgba(255,255,255,0.58)"
C_CARD_SOFT = "rgba(255,255,255,0.72)"
C_BORDER = "rgba(81,100,101,0.16)"
C_PINK = "#EAA4A6"
C_PINK_SOFT = "rgba(234,164,166,0.28)"
C_TEAL_SOFT = "rgba(210,230,229,0.85)"
C_AVATAR = "#BFE8E6"
C_DARK = "#405354"


# ── AVATAR ─────────────────────────────
class Avatar(QWidget):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.setFixedSize(46, 46)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        p.setBrush(QColor(C_AVATAR))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, 46, 46)

        p.setPen(QColor(C_DARK))
        p.setFont(QFont("Segoe UI", 11, QFont.Bold))
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

        base_dir = os.path.dirname(os.path.abspath(__file__))
        id_lobster = QFontDatabase.addApplicationFont(
            os.path.join(base_dir, "assets", "fonts", "LobsterTwo-Regular.ttf")
        )
        self.font_lobster = (
            QFontDatabase.applicationFontFamilies(id_lobster)[0]
            if id_lobster != -1
            else "serif"
        )

        self.setFont(QFont("Segoe UI"))
        self.build()
        lang.language_changed.connect(self._rebuild)


    def _rebuild(self, _code: str = ""):
        old = self.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old)
        self.build()

    def build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 24, 48, 24)
        root.setSpacing(0)

        # ===== HERO =====
        hero = QVBoxLayout()
        hero.setSpacing(8)

        badge = QLabel(
            f"<span style='font-family: \"{self.font_lobster}\"; "
            f"font-size: 34px; font-weight: bold; color: #516465;'>Campus </span>"
            f"<span style='font-family: \"{self.font_lobster}\"; "
            f"font-size: 34px; font-weight: bold; color: #EAA4A6;'>Connect</span>"
        )
        badge.setAlignment(Qt.AlignCenter)
        badge.setTextFormat(Qt.RichText)
        badge.setStyleSheet("background: transparent;")

        title = QLabel(lang.t("about.hero_title"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {C_TITLE};
            font-size: 42px;
            font-weight: 800;
            background: transparent;
        """)

        subtitle = QLabel(lang.t("about.subtitle"))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"""
            color: {C_SUB};
            font-size: 15px;
            background: transparent;
        """)

        hero.addWidget(badge)
        hero.addWidget(title)
        hero.addWidget(subtitle)

        root.addLayout(hero)
        root.addSpacing(22)

        # ===== MAIN CARD =====
        main_card = QFrame()
        main_card.setObjectName("aboutMainCard")
        main_card.setStyleSheet(f"""
            QFrame#aboutMainCard {{
                background: {C_CARD};
                border-radius: 28px;
                border: 1px solid {C_BORDER};
            }}
        """)

        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(34, 30, 34, 30)
        card_layout.setSpacing(24)

        # ===== INTRO ROW =====
        intro_row = QHBoxLayout()
        intro_row.setSpacing(22)

        intro_box = self.big_info_card(
            "🎓",
            lang.t("about.built_title"),
            lang.t("about.built_body")
        )

        mission_box = self.big_info_card(
            "🚀",
            lang.t("about.mission_title"),
            lang.t("about.mission_body")
        )

        intro_row.addWidget(intro_box)
        intro_row.addWidget(mission_box)

        card_layout.addLayout(intro_row)

        # ===== FEATURE CARDS ====
        feature_row = QHBoxLayout()
        feature_row.setSpacing(16)

        feature_row.addWidget(self.feature_card("🔎", lang.t("about.discover_title"), lang.t("about.discover_body")))
        feature_row.addWidget(self.feature_card("🤝", lang.t("about.connect_title"), lang.t("about.connect_body")))
        feature_row.addWidget(self.feature_card("✨", lang.t("about.participate_title"), lang.t("about.participate_body")))

        card_layout.addLayout(feature_row)

        # ===== TEAM =====
        self.team_section(card_layout)

        root.addWidget(main_card)

        # ===== FOOTER =====
        root.addSpacing(18)

        footer = QLabel(lang.t("about.footer"))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"""
            color: {C_MUTED};
            font-size: 12px;
            background: transparent;
        """)
        root.addWidget(footer)

        root.addStretch()
    
    def big_info_card(self, icon, title, body):
        card = QFrame()
        card.setObjectName("bigInfoCard")
        card.setStyleSheet(f"""
            QFrame#bigInfoCard {{
                background: {C_CARD_SOFT};
                border-radius: 22px;
                border: 1px solid {C_BORDER};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background: {C_PINK_SOFT};
            border-radius: 19px;
            font-size: 18px;
        """)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: {C_TITLE};
            font-size: 22px;
            font-weight: bold;
        """)

        top.addWidget(icon_lbl)
        top.addWidget(title_lbl)
        top.addStretch()

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(f"""
            color: {C_BODY};
            font-size: 14px;
            line-height: 1.5;
        """)

        layout.addLayout(top)
        layout.addWidget(body_lbl)

        return card
    
    def feature_card(self, icon, title, body):
        card = QFrame()
        card.setObjectName("featureCard")
        card.setFixedHeight(118)
        card.setStyleSheet(f"""
            QFrame#featureCard {{
                background: rgba(255,255,255,0.68);
                border-radius: 20px;
                border: 1px solid {C_BORDER};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px;")

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: {C_TITLE};
            font-size: 18px;
            font-weight: bold;
        """)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(f"""
            color: {C_SUB};
            font-size: 13px;
        """)

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(body_lbl)

        return card
    
    def team_section(self, parent_layout):
        header = QHBoxLayout()
        header.setSpacing(12)

        icon_lbl = QLabel("👥")
        icon_lbl.setFixedSize(38, 38)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background: {C_TEAL_SOFT};
            border-radius: 19px;
            font-size: 18px;
        """)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(2)

        title = QLabel(lang.t("about.team_title"))
        title.setStyleSheet(f"""
            color: {C_TITLE};
            font-size: 23px;
            font-weight: bold;
        """)

        sub = QLabel(lang.t("about.team_name"))
        sub.setStyleSheet(f"""
            color: {C_MUTED};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 2px;
        """)

        title_wrap.addWidget(title)
        title_wrap.addWidget(sub)

        header.addWidget(icon_lbl)
        header.addLayout(title_wrap)
        header.addStretch()

        parent_layout.addLayout(header)

        members = [
            ("AF", "Arsel Fahri Khadafi"),
            ("JS", "Jocelyn Christina Simamora"),
            ("MR", "Muhammad Rafi Al Rabbani"),
            ("MS", "Muhammad Salman Al Farisi"),
            ("TR", "Tania Putri Ramadhani"),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for idx, member in enumerate(members):
            row = idx // 2
            col = idx % 2
            grid.addWidget(self.member_card(member[0], member[1]), row, col)

        parent_layout.addLayout(grid)

    
    def member_card(self, initials, name):
        card = QFrame()
        card.setObjectName("memberCard")
        card.setFixedHeight(68)
        card.setStyleSheet(f"""
            QFrame#memberCard {{
                background: rgba(255,255,255,0.76);
                border-radius: 18px;
                border: 1px solid {C_BORDER};
            }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        layout.addWidget(Avatar(initials))

        text_wrap = QVBoxLayout()
        text_wrap.setSpacing(2)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"""
            color: #243333;
            font-size: 14px;
            font-weight: bold;
        """)

        role_lbl = QLabel(lang.t("about.team_member"))
        role_lbl.setStyleSheet(f"""
            color: {C_MUTED};
            font-size: 12px;
        """)

        text_wrap.addWidget(name_lbl)
        text_wrap.addWidget(role_lbl)

        layout.addLayout(text_wrap)
        layout.addStretch()

        return card
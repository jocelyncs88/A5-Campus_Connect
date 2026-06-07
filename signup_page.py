# ==============================================================
# FILE: signup_page.py
# TUGAS: Membuat halaman signup untuk Student
# DIBUAT OLEH: UI/UX Component Builder
# ==============================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QGraphicsDropShadowEffect, QSizePolicy, QMessageBox
)

from language_manager import lang
from resource_path import asset_path
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon, QFontDatabase
import os

# ─── WARNA ─────────────────────────────────────────────────────
COLOR_TEXT_PRIMARY = "#5D6B6B"
COLOR_PINK_LOGIN = "#ff99aa"

class SignUpPage(QWidget):

    # ==========================================================
    # SIGNAL
    # ==========================================================

    signup_diklik = pyqtSignal(str, str, str, str, str) # nama, email, phone, university, password
    kembali_diklik = pyqtSignal()
    login_diklik = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("signup_page")

        # Load custom fonts
        id_lobster = QFontDatabase.addApplicationFont(asset_path("assets", "fonts", "LobsterTwo-Regular.ttf"))
        self.font_lobster = QFontDatabase.applicationFontFamilies(id_lobster)[0] if id_lobster != -1 else "serif"

        # Password visibility flag
        self.password_visible = False
        self.confirm_visible = False

        # Placeholder untuk widget agar eventFilter aman dipanggil pada init
        self.input_password = None
        self.btn_password_eye = None
        self.input_confirm = None
        self.btn_confirm_eye = None

        # Build UI
        self.setup_ui()

        # Apply stylesheet
        self.apply_style()
        self._retranslate()
        lang.language_changed.connect(self._retranslate)

        # Shadow effect untuk card
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(24)

        self.card.setGraphicsEffect(shadow)

    # ==========================================================
    # BUILD UI
    # ==========================================================

    def setup_ui(self):

        # ======================================================
        # OUTER LAYOUT
        # ======================================================

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(40, 40, 40, 40)

        # ======================================================
        # MAIN CARD
        # ======================================================

        self.card = QWidget()
        self.card.setObjectName("signup_card")
        self.card.setMinimumWidth(1200)
        self.card.setMinimumHeight(680)
        self.card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        card_layout = QHBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ======================================================
        # LEFT SIDE
        # ======================================================

        left_widget = QWidget()
        left_widget.setObjectName("left_widget")
        left_widget.setMinimumWidth(350)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(0)

        # LOGO — sama dengan main_window.py
        self.logo_label = QLabel(
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 60px; color: {COLOR_TEXT_PRIMARY};'>Campus</span><br>"
            f"<span style='font-family: \"{self.font_lobster}\"; font-size: 60px; font-weight: bold; color: {COLOR_PINK_LOGIN};'>Connect</span>"
        )
        self.logo_label.setObjectName("logo_label")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setTextFormat(Qt.RichText)

        left_layout.addWidget(self.logo_label)
        left_layout.addSpacing(50)

        # BIG TEXT — dikosongkan, diisi oleh _retranslate()
        self.big_text = QLabel()
        self.big_text.setObjectName("big_text")
        self.big_text.setAlignment(Qt.AlignCenter)
        self.big_text.setWordWrap(True)
        self.big_text.setMinimumWidth(300)

        big_font = QFont("Inter", 30)
        big_font.setBold(True)

        self.big_text.setFont(big_font)

        left_layout.addWidget(self.big_text)
        left_layout.addSpacing(20)

        # SUBTEXT — dikosongkan, diisi oleh _retranslate()
        self.sub_text = QLabel()
        self.sub_text.setObjectName("sub_text")
        self.sub_text.setAlignment(Qt.AlignCenter)

        sub_font = QFont("Inter", 13)
        self.sub_text.setFont(sub_font)

        left_layout.addWidget(self.sub_text)

        left_layout.addStretch()

        # IMAGE
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "student_signup.png"
        )

        if os.path.exists(image_path):

            pixmap = QPixmap(image_path)

            self.image_label.setPixmap(
                pixmap.scaled(
                    260,
                    260,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        left_layout.addWidget(self.image_label)

        left_widget.setLayout(left_layout)

        # ======================================================
        # RIGHT SIDE
        # ======================================================

        right_widget = QWidget()

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(50, 30, 50, 30)
        right_layout.setSpacing(8)

        # TITLE — dikosongkan, diisi oleh _retranslate()
        self.title = QLabel()
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)

        title_font = QFont("Inter", 30)
        title_font.setBold(True)

        self.title.setFont(title_font)

        right_layout.addWidget(self.title)

        # SUBTITLE — dikosongkan, diisi oleh _retranslate()
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)

        sub_font = QFont("Inter", 12)
        self.subtitle.setFont(sub_font)

        right_layout.addWidget(self.subtitle)
        right_layout.addSpacing(16)

        # FONT
        label_font = QFont("Inter", 11)
        label_font.setBold(True)

        input_font = QFont("Inter", 12)

        # ======================================================
        # FULL NAME
        # ======================================================

        self.label_name = QLabel()
        self.label_name.setObjectName("label_field")
        self.label_name.setFont(label_font)

        right_layout.addWidget(self.label_name)

        self.input_name = QLineEdit()
        self.input_name.setObjectName("input_field")
        self.input_name.setFixedHeight(48)
        self.input_name.setFont(input_font)
        self.input_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        right_layout.addWidget(self.input_name)
        right_layout.addSpacing(6)

        # ======================================================
        # EMAIL
        # ======================================================

        self.label_email = QLabel()
        self.label_email.setObjectName("label_field")
        self.label_email.setFont(label_font)

        right_layout.addWidget(self.label_email)

        self.input_email = QLineEdit()
        self.input_email.setObjectName("input_field")
        self.input_email.setFixedHeight(48)
        self.input_email.setFont(input_font)
        self.input_email.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        right_layout.addWidget(self.input_email)
        right_layout.addSpacing(6)

        # ======================================================
        # PHONE NUMBER + UNIVERSITY (1 ROW)
        # ======================================================

        row_layout = QHBoxLayout()
        row_layout.setSpacing(14)
        row_layout.setContentsMargins(0, 0, 0, 0)

        # ----------------------------------
        # PHONE NUMBER COLUMN
        # ----------------------------------

        phone_layout = QVBoxLayout()
        phone_layout.setSpacing(6)

        self.label_phone = QLabel()
        self.label_phone.setObjectName("label_field")
        self.label_phone.setFont(label_font)

        self.input_phone = QLineEdit()
        self.input_phone.setObjectName("input_field")
        self.input_phone.setFixedHeight(48)
        self.input_phone.setFont(input_font)
        self.input_phone.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        phone_layout.addWidget(self.label_phone)
        phone_layout.addWidget(self.input_phone)

        # ----------------------------------
        # UNIVERSITY COLUMN
        # ----------------------------------

        university_layout = QVBoxLayout()
        university_layout.setSpacing(6)

        self.label_university = QLabel()
        self.label_university.setObjectName("label_field")
        self.label_university.setFont(label_font)

        self.input_university = QLineEdit()
        self.input_university.setObjectName("input_field")
        self.input_university.setFixedHeight(48)
        self.input_university.setFont(input_font)
        self.input_university.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        university_layout.addWidget(self.label_university)
        university_layout.addWidget(self.input_university)

        # ----------------------------------
        # MASUKKAN KE ROW
        # ----------------------------------

        row_layout.addLayout(phone_layout, 1)
        row_layout.addLayout(university_layout, 1)

        right_layout.addLayout(row_layout)
        right_layout.addSpacing(6)

        # =========================================
        # PASSWORD INPUT + EYE BUTTON
        # =========================================

        self.label_password = QLabel()
        self.label_password.setObjectName("label_field")
        self.label_password.setFont(label_font)
        right_layout.addWidget(self.label_password)

        password_widget = QWidget()

        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        self.input_password = QLineEdit()
        self.input_password.setObjectName("input_password")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedHeight(48)
        self.input_password.setFont(input_font)
        self.input_password.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_password_eye = QPushButton()
        self.btn_password_eye.setObjectName("btn_eye")
        self.btn_password_eye.setFixedSize(48, 48)
        self.btn_password_eye.setCursor(Qt.PointingHandCursor)

        self.btn_password_eye.setIcon(QIcon(asset_path("assets", "icons", "eye_outline.png")))
        self.btn_password_eye.setIconSize(QSize(20, 20))

        self.btn_password_eye.clicked.connect(
            self.toggle_password
        )

        self.input_password.installEventFilter(self)
        self.btn_password_eye.installEventFilter(self)

        password_layout.addWidget(self.input_password)
        password_layout.addWidget(self.btn_password_eye)

        password_widget.setLayout(password_layout)

        right_layout.addWidget(password_widget)
        right_layout.addSpacing(6)

        # =========================================
        # CONFIRM PASSWORD + EYE BUTTON
        # =========================================

        self.label_confirm = QLabel()
        self.label_confirm.setObjectName("label_field")
        self.label_confirm.setFont(label_font)
        right_layout.addWidget(self.label_confirm)

        confirm_widget = QWidget()

        confirm_layout = QHBoxLayout()
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setSpacing(0)

        self.input_confirm = QLineEdit()
        self.input_confirm.setObjectName("input_password")
        self.input_confirm.setEchoMode(QLineEdit.Password)
        self.input_confirm.setFixedHeight(48)
        self.input_confirm.setFont(input_font)
        self.input_confirm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_confirm_eye = QPushButton()
        self.btn_confirm_eye.setObjectName("btn_eye")
        self.btn_confirm_eye.setFixedSize(48, 48)
        self.btn_confirm_eye.setCursor(Qt.PointingHandCursor)

        self.btn_confirm_eye.setIcon(QIcon(asset_path("assets", "icons", "eye_outline.png")))
        self.btn_confirm_eye.setIconSize(QSize(20, 20))

        self.btn_confirm_eye.clicked.connect(
            self.toggle_confirm_password
        )

        self.input_confirm.installEventFilter(self)
        self.btn_confirm_eye.installEventFilter(self)

        confirm_layout.addWidget(self.input_confirm)
        confirm_layout.addWidget(self.btn_confirm_eye)

        confirm_widget.setLayout(confirm_layout)

        right_layout.addWidget(confirm_widget)
        right_layout.addSpacing(20)

        # ======================================================
        # BUTTON SIGN UP — dikosongkan, diisi oleh _retranslate()
        # ======================================================

        self.btn_signup = QPushButton()
        self.btn_signup.setObjectName("btn_signup")
        self.btn_signup.setFixedHeight(48)
        self.btn_signup.setCursor(Qt.PointingHandCursor)

        self.btn_signup.clicked.connect(
            self.on_signup_diklik
        )

        right_layout.addWidget(self.btn_signup)

        # ======================================================
        # BUTTON BACK — dikosongkan, diisi oleh _retranslate()
        # ======================================================

        self.btn_back = QPushButton()
        self.btn_back.setObjectName("btn_back")
        self.btn_back.setFixedHeight(48)
        self.btn_back.setCursor(Qt.PointingHandCursor)

        self.btn_back.clicked.connect(
            self.kembali_diklik.emit
        )

        right_layout.addSpacing(6)
        right_layout.addWidget(self.btn_back)

        # ======================================================
        # FINAL SETUP
        # ======================================================

        right_widget.setLayout(right_layout)

        card_layout.addWidget(left_widget, 1)
        card_layout.addWidget(right_widget, 2)

        self.card.setLayout(card_layout)

        outer_layout.addWidget(self.card)

        self.setLayout(outer_layout)

    # ==========================================================
    # STYLE
    # ==========================================================

    def apply_style(self):

        self.setStyleSheet("""

            QWidget#signup_page {
                background-color: #D2E6E5;
            }

            QWidget#signup_card {
                background: white;
                border-radius: 28px;
            }

            QWidget#left_widget {
                background-color: #F7CBCA;
                border-top-left-radius: 28px;
                border-bottom-left-radius: 28px;
            }

            QLabel#logo_label {
                color: #516465;
                font-weight: bold;
            }

            QLabel#big_text {
                color: #516465;
                font-weight: bold;
            }

            QLabel#sub_text {
                color: #5D6B6B;
                line-height: 1.4;
            }

            QLabel#title {
                color: #516465;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #7A8B8B;
            }

            QLabel#label_field {
                color: #516465;
                font-weight: bold;
            }

            QLineEdit#input_field {
                border: 2px solid #D9E4E4;
                border-radius: 14px;
                padding-left: 14px;
                padding-right: 14px;
                background: #FAFAFA;
                color: #516465;
            }

            QLineEdit#input_field:focus {
                border: 2px solid #F7CBCA;
                background: white;
            }
                           
            QLineEdit#input_password {
                background-color: white;
                border: 2px solid #D9E4E4;
                border-top-left-radius: 14px;
                border-bottom-left-radius: 14px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-right: none;
                padding-left: 14px;
                color: #516465;
            }

            QLineEdit#input_password:focus,
            QLineEdit#input_password:focus + QPushButton#btn_eye,
            QPushButton#btn_eye:focus {
                border: 2px solid #F7CBCA;
            }

            QLineEdit#input_password:focus {
                border-right: none;
            }

            QLineEdit#input_password:focus + QPushButton#btn_eye,
            QPushButton#btn_eye:focus {
                border-left: none;
            }

            QPushButton#btn_eye {
                background-color: white;
                border: 2px solid #D9E4E4;
                border-left: none;
                border-top-right-radius: 14px;
                border-bottom-right-radius: 14px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                color: #516465;
            }

            QPushButton#btn_eye:hover {
                background-color: #F7CBCA;
            }

            QPushButton#btn_signup {
                background-color: #2D6A6A;
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#btn_signup:hover {
                background-color: #445556;
            }

            QPushButton#btn_signup:pressed {
                background-color: #394949;
            }

            QPushButton#btn_back {
                background-color: transparent;
                color: #5D6B6B;
                border: 1.5px solid #CBD5E0;
                border-radius: 10px;
                font-size: 14px;
                padding: 10px;
            }

            QPushButton#btn_back:hover {
                background-color: #D2E6E5;
            }

            QPushButton#btn_back:pressed {
                background-color: #BDD6D5;
            }

        """)

    # ==========================================================
    # SIGNUP BUTTON CLICK
    # ==========================================================

    def on_signup_diklik(self):

        nama = self.input_name.text().strip()
        email = self.input_email.text().strip()
        phone = self.input_phone.text().strip()
        university = self.input_university.text().strip()
        password = self.input_password.text()
        confirm_password = self.input_confirm.text()

        # =========================
        # VALIDASI FULL NAME
        # =========================
        if nama == "":
            QMessageBox.warning(
                self,
                lang.t("signup.msg_invalid_name_title"),
                lang.t("signup.msg_invalid_name_body")
            )
            return

        if email == "":
            QMessageBox.warning(
                self,
                lang.t("signup.msg_incomplete_title"),
                lang.t("signup.msg_email_empty")
            )
            return

        if phone == "":
            QMessageBox.warning(
                self,
                lang.t("signup.msg_incomplete_title"),
                lang.t("signup.msg_phone_empty")
            )
            return

        if password == "":
            QMessageBox.warning(
                self,
                lang.t("signup.msg_incomplete_title"),
                lang.t("signup.msg_password_empty")
            )
            return

        if confirm_password == "":
            QMessageBox.warning(
                self,
                lang.t("signup.msg_incomplete_title"),
                lang.t("signup.msg_confirm_empty")
            )
            return

        if university == "":
            QMessageBox.warning(
                self,
                lang.t("signup.msg_incomplete_title"),
                lang.t("signup.msg_university_empty")
            )
            return

        # =========================
        # VALIDASI EMAIL
        # =========================
        if "@" not in email:
            QMessageBox.warning(
                self,
                lang.t("signup.msg_invalid_email_title"),
                lang.t("signup.msg_invalid_email_body")
            )
            return

        # =========================
        # VALIDASI PHONE NUMBER
        # =========================
        if not phone.isdigit():
            QMessageBox.warning(
                self,
                lang.t("signup.msg_invalid_phone_title"),
                lang.t("signup.msg_phone_not_digit")
            )
            return

        if len(phone) > 12:
            QMessageBox.warning(
                self,
                lang.t("signup.msg_invalid_phone_title"),
                lang.t("signup.msg_phone_too_long")
            )
            return

        # =========================
        # VALIDASI PASSWORD
        # =========================
        if len(password) < 8:
            QMessageBox.warning(
                self,
                lang.t("signup.msg_weak_password_title"),
                lang.t("signup.msg_weak_password_body")
            )
            return

        # =========================
        # VALIDASI CONFIRM PASSWORD
        # =========================
        if password != confirm_password:
            QMessageBox.warning(
                self,
                lang.t("signup.msg_password_mismatch_title"),
                lang.t("signup.msg_password_mismatch_body")
            )
            return

        # =========================
        # JIKA SEMUA VALID
        # =========================
        self.signup_diklik.emit(
            nama,
            email,
            phone,
            university,
            password
        )

        QMessageBox.information(
            self,
            lang.t("signup.msg_success_title"),
            lang.t("signup.msg_success_body")
        )

        self.kembali_diklik.emit()

    # ==========================================================
    # TOGGLE PASSWORD
    # ==========================================================

    def toggle_password(self):

        if self.password_visible:

            self.input_password.setEchoMode(QLineEdit.Password)

            self.btn_password_eye.setIcon(
                QIcon(asset_path("assets", "icons", "eye_outline.png"))
            )

            self.password_visible = False

        else:

            self.input_password.setEchoMode(QLineEdit.Normal)

            self.btn_password_eye.setIcon(
                QIcon(asset_path("assets", "icons", "eye_filled.png"))
            )

            self.password_visible = True


    # ==========================================================
    # TOGGLE CONFIRM PASSWORD
    # ==========================================================

    def toggle_confirm_password(self):

        if self.confirm_visible:

            self.input_confirm.setEchoMode(QLineEdit.Password)

            self.btn_confirm_eye.setIcon(
                QIcon(asset_path("assets", "icons", "eye_outline.png"))
            )

            self.confirm_visible = False

        else:

            self.input_confirm.setEchoMode(QLineEdit.Normal)

            self.btn_confirm_eye.setIcon(
                QIcon(asset_path("assets", "icons", "eye_filled.png"))
            )

            self.confirm_visible = True

    def eventFilter(self, source, event):
        if source in (getattr(self, 'input_password', None), getattr(self, 'btn_password_eye', None)):
            if event.type() == QEvent.FocusIn:
                self.input_password.setStyleSheet(
                    "background-color: white;"
                    "border: 2px solid #F7CBCA;"
                    "border-top-left-radius: 14px;"
                    "border-bottom-left-radius: 14px;"
                    "border-top-right-radius: 0px;"
                    "border-bottom-right-radius: 0px;"
                    "border-right: none;"
                    "padding-left: 14px;"
                    "color: #516465;"
                )
                self.btn_password_eye.setStyleSheet(
                    "background-color: white;"
                    "border: 2px solid #F7CBCA;"
                    "border-top-right-radius: 14px;"
                    "border-bottom-right-radius: 14px;"
                    "border-top-left-radius: 0px;"
                    "border-bottom-left-radius: 0px;"
                    "border-left: none;"
                )
            elif event.type() == QEvent.FocusOut:
                if not (self.input_password.hasFocus() or self.btn_password_eye.hasFocus()):
                    self.input_password.setStyleSheet("")
                    self.btn_password_eye.setStyleSheet("")

        if source in (getattr(self, 'input_confirm', None), getattr(self, 'btn_confirm_eye', None)):
            if event.type() == QEvent.FocusIn:
                self.input_confirm.setStyleSheet(
                    "background-color: white;"
                    "border: 2px solid #F7CBCA;"
                    "border-top-left-radius: 14px;"
                    "border-bottom-left-radius: 14px;"
                    "border-top-right-radius: 0px;"
                    "border-bottom-right-radius: 0px;"
                    "border-right: none;"
                    "padding-left: 14px;"
                    "color: #516465;"
                )
                self.btn_confirm_eye.setStyleSheet(
                    "background-color: white;"
                    "border: 2px solid #F7CBCA;"
                    "border-top-right-radius: 14px;"
                    "border-bottom-right-radius: 14px;"
                    "border-top-left-radius: 0px;"
                    "border-bottom-left-radius: 0px;"
                    "border-left: none;"
                )
            elif event.type() == QEvent.FocusOut:
                if not (self.input_confirm.hasFocus() or self.btn_confirm_eye.hasFocus()):
                    self.input_confirm.setStyleSheet("")
                    self.btn_confirm_eye.setStyleSheet("")

        return super().eventFilter(source, event)

    def _retranslate(self):
        # LEFT SIDE
        self.big_text.setText(lang.t("signup.hero_title"))
        self.sub_text.setText(lang.t("signup.hero_subtitle"))

        # RIGHT SIDE
        self.title.setText(lang.t("signup.title"))
        self.subtitle.setText(lang.t("signup.subtitle"))

        # LABELS
        self.label_name.setText(lang.t("signup.full_name"))
        self.label_email.setText(lang.t("signup.email"))
        self.label_phone.setText(lang.t("signup.phone"))
        self.label_university.setText(lang.t("signup.university"))
        self.label_password.setText(lang.t("signup.password"))
        self.label_confirm.setText(lang.t("signup.confirm_password"))

        # PLACEHOLDERS
        self.input_name.setPlaceholderText(lang.t("signup.ph_name"))
        self.input_email.setPlaceholderText(lang.t("signup.ph_email"))
        self.input_phone.setPlaceholderText(lang.t("signup.ph_phone"))
        self.input_university.setPlaceholderText(lang.t("signup.ph_university"))
        self.input_password.setPlaceholderText(lang.t("signup.ph_password"))
        self.input_confirm.setPlaceholderText(lang.t("signup.ph_confirm"))

        # BUTTONS
        self.btn_signup.setText(lang.t("signup.button"))
        self.btn_back.setText(lang.t("signup.back_login"))
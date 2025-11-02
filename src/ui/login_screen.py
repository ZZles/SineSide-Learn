import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from src.data.database import add_user, check_user_exists

VALIDATION_RULES = {
    "username": {
        "min_length": 4,
        "regex": re.compile(r'^[a-zA-Z]+$'),
        "error_message": "Le nom d'utilisateur doit contenir au moins 4 lettres et aucun chiffre ou symbole."
    },
    "email": {
        "allowed_domains": {"@gmail.com", "@hotmail.com", "@hotmail.fr", "@outlook.fr", "@outlook.com", "@proton.me"},
        "error_message": "L'adresse e-mail doit provenir d'un domaine autorisé (gmail, hotmail, outlook, proton)."
    }
}

class LiquidGlassLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SineSide Learn")
        self.setWindowIcon(QIcon("C:/Users/Mavaax/3D Objects/SineSide-Learn/assets/logodark.png"))
        self.setFixedSize(900, 600)
        self.setWindowOpacity(0.95)

        self.setStyleSheet("""
            QMainWindow { background-color: #1C1C1C; }
            QFrame#Container { background-color: #2E2E2E; border-radius: 10px; }
            QLabel { color: white; font-family: 'Arial'; }
            QLabel#TitleLabel { font-size: 32px; font-weight: bold; color: #FF8C00; }
            QLineEdit { background-color: #333; border: 1px solid #555; border-radius: 5px; padding: 10px; color: white; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #FF8C00; }
            QPushButton { background-color: #FF8C00; color: white; border: none; border-radius: 5px; padding: 10px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #FFAD42; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        container = QFrame()
        container.setObjectName("Container")
        container.setFixedSize(400, 450)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addWidget(container)

        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.title_label)

        self.full_text = "SineSide Learn"
        self.typewriter_index = 0
        self.typewriter_direction = 1
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        QTimer.singleShot(500, self.start_typing)

        container_layout.addStretch(1)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Au moins 4 lettres")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Adresse e-mail valide")
        
        self.password_edit = QLineEdit()
        self.password_edit.setText("P@ssword123!")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.focusInEvent = self.password_focus_in

        container_layout.addWidget(QLabel("Nom d'utilisateur"))
        container_layout.addWidget(self.username_edit)
        container_layout.addWidget(QLabel("E-mail"))
        container_layout.addWidget(self.email_edit)
        container_layout.addWidget(QLabel("Mot de passe"))
        container_layout.addWidget(self.password_edit)
        container_layout.addStretch(1)

        self.login_button = QPushButton("Connexion ou Inscription")
        self.login_button.clicked.connect(self.handle_login_or_register)
        container_layout.addWidget(self.login_button)

    def password_focus_in(self, event):
        if self.password_edit.text() == "P@ssword123!":
            self.password_edit.selectAll()
        QLineEdit.focusInEvent(self.password_edit, event)

    def update_typewriter(self):
        if self.typewriter_direction == 1:
            if self.typewriter_index < len(self.full_text):
                self.title_label.setText(self.full_text[:self.typewriter_index + 1] + "|")
                self.typewriter_index += 1
            else:
                self.typewriter_timer.stop()
                QTimer.singleShot(1000, self.start_erasing)
        else:
            if self.typewriter_index > 0:
                self.title_label.setText(self.full_text[:self.typewriter_index - 1] + "|")
                self.typewriter_index -= 1
            else:
                self.typewriter_timer.stop()
                QTimer.singleShot(1000, self.start_typing)

    def start_typing(self):
        self.typewriter_direction = 1
        self.typewriter_timer.start(285)

    def start_erasing(self):
        self.typewriter_direction = -1
        self.typewriter_timer.start(142)

    def handle_login_or_register(self):
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not password:
            self.show_message("Erreur", "Le nom d'utilisateur et le mot de passe sont requis.", "warning")
            return

        if check_user_exists(username):
            self.show_message("Succès", f"Bienvenue, {username} !", "info")
            self.open_profile_screen(username)
            return

        rule_user = VALIDATION_RULES["username"]
        if len(username) < rule_user["min_length"] or not rule_user["regex"].match(username):
            self.show_message("Erreur d'inscription", rule_user["error_message"], "warning")
            return

        rule_email = VALIDATION_RULES["email"]
        if not email or not any(email.endswith(domain) for domain in rule_email["allowed_domains"]):
            self.show_message("Erreur d'inscription", rule_email["error_message"], "warning")
            return
        
        if add_user(username, email, password):
            self.show_message("Succès", f"Compte pour {username} créé avec succès !", "info")
            self.open_profile_screen(username)
        else:
            self.show_message("Erreur", "Une erreur interne est survenue.", "critical")

    def open_profile_screen(self, username):
        from src.ui.profile_screen import ProfileScreen
        self.profile_screen = ProfileScreen(username)
        self.profile_screen.show()
        self.close()

    def show_message(self, title, message, icon_type):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # --- MODIFIÉ: Style pour la QMessageBox ---
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2E2E2E;
            }
            QLabel {
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: #FF8C00;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #FFAD42;
            }
        """)

        icon_map = {"info": QMessageBox.Information, "warning": QMessageBox.Warning, "critical": QMessageBox.Critical}
        msg_box.setIcon(icon_map.get(icon_type, QMessageBox.NoIcon))
        msg_box.exec_()

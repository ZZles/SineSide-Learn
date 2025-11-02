import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsBlurEffect, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from src.data.database import init_database, check_user_exists, add_user

# Initialisation de la BDD (déplacée dans main.py, mais on la garde ici par sécurité)
init_database()


class LiquidGlassLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SineSide Learn")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Styles "Liquid Glass" orange (INCHANGÉ)
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF8C00, stop:1 #FF6B00);
                border-radius: 15px;
            }
            QFrame#GlassFrame {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 50);
            }
            QFrame#FormBubble {
                background-color: rgba(40, 40, 40, 180);
                border-radius: 20px;
                border: 1px solid rgba(255, 140, 0, 100);
                box-shadow: 0 8px 32px rgba(255, 140, 0, 0.3);
            }
            QLabel#TitleLabel {
                color: white;
                font-family: 'Arial';
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 20);
                border: 1px solid rgba(255, 140, 0, 100);
                border-radius: 10px;
                padding: 12px;
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF8C00, stop:1 #FF4500);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF7F00, stop:1 #FF6347);
                box-shadow: 0 0 15px rgba(255, 140, 0, 0.7);
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Frame principal avec effet de verre
        self.glass_frame = QFrame()
        self.glass_frame.setObjectName("GlassFrame")
        self.glass_frame.setFixedSize(800, 500)
        main_layout.addWidget(self.glass_frame, 0, Qt.AlignCenter)

        glass_layout = QVBoxLayout(self.glass_frame)
        glass_layout.setContentsMargins(30, 30, 30, 30)
        glass_layout.setSpacing(20)

        # Effet de flou
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(10)
        # self.glass_frame.setGraphicsEffect(blur_effect) # Désactivé car il floute aussi le contenu

        # Effet d'ombre
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setColor(QColor(255, 140, 0, 150))
        shadow_effect.setOffset(0, 0)
        self.glass_frame.setGraphicsEffect(shadow_effect)

        # Conteneur pour le titre (centré)
        title_container = QFrame()
        title_container.setFixedHeight(100)
        title_container.setStyleSheet("background: transparent;")
        glass_layout.addWidget(title_container, 0, Qt.AlignHCenter)

        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        # Titre avec animation "machine à écrire" aller-retour
        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.title_label)

        self.full_text = "SineSide Learn"
        self.current_text = ""
        self.typewriter_index = 0
        self.typewriter_direction = 1  # 1 = écriture, -1 = effacement
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        self.typewriter_timer.start(50)  # Délai initial

        # Formulaire dans une bulle (centré)
        form_bubble = QFrame()
        form_bubble.setObjectName("FormBubble")
        form_bubble.setFixedSize(400, 350)
        glass_layout.addWidget(form_bubble, 0, Qt.AlignHCenter)

        form_layout = QVBoxLayout(form_bubble)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nom d'utilisateur")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Adresse e-mail")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Mot de passe")
        self.password_edit.setEchoMode(QLineEdit.Password)

        # Label pour le formulaire
        form_title = QLabel("Connexion / Inscription")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        form_layout.addWidget(form_title)
        form_layout.addWidget(self.username_edit)
        form_layout.addWidget(self.email_edit)
        form_layout.addWidget(self.password_edit)

        self.login_button = QPushButton("Continuer")
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        # Animation de fondu
        self.fade_in_animation()

    def update_typewriter(self):
        """Animation de machine à écrire aller-retour (4s écriture, 2s effacement)."""
        if self.typewriter_direction == 1:  # Écriture
            if self.typewriter_index < len(self.full_text):
                self.current_text = self.full_text[:self.typewriter_index + 1]
                self.title_label.setText(self.current_text + ("|" if self.typewriter_index % 2 == 0 else ""))
                self.typewriter_index += 1
            else:
                # Pause de 1s avant l'effacement
                self.typewriter_timer.stop()
                QTimer.singleShot(1000, self.start_erasing)
        else:  # Effacement (2x plus rapide)
            if self.typewriter_index > 0:
                self.current_text = self.full_text[:self.typewriter_index - 1]
                self.title_label.setText(
                    self.current_text + ("|" if (len(self.full_text) - self.typewriter_index) % 2 == 0 else ""))
                self.typewriter_index -= 1
            else:
                # Pause de 1s avant de recommencer
                self.typewriter_timer.stop()
                QTimer.singleShot(1000, self.start_typing)

    def start_erasing(self):
        """Démarre l'effacement du texte (2s)."""
        self.typewriter_direction = -1
        self.typewriter_timer.start(25)  # 2x plus rapide (50ms/2)

    def start_typing(self):
        """Démarre l'écriture du texte (4s)."""
        self.typewriter_direction = 1
        self.typewriter_timer.start(50)  # Vitesse normale

    def fade_in_animation(self):
        """Animation de fondu au démarrage."""
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setDuration(800)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_anim.start()

    def handle_login(self):
        """Gère la connexion/inscription."""
        try:
            username = self.username_edit.text().strip()
            email = self.email_edit.text().strip()
            password = self.password_edit.text().strip()

            if not all([username, email, password]):
                self.show_message("Erreur", "Tous les champs sont obligatoires !", "warning")
                return

            if check_user_exists(username):
                # En production, il faudrait vérifier le mot de passe !
                self.show_message("Succès", f"Bienvenue de retour, {username} !", "info")
                self.open_trading_screen(username)
            else:
                # En production, il faudrait hasher le mot de passe !
                add_user(username, email, password)
                self.show_message("Succès", f"Compte créé pour {username} !", "info")
                self.open_trading_screen(username)


        except Exception as e:

            print(f"--- ERREUR CRITIQUE DANS HANDLE_LOGIN ---")  # Message plus visible

            print(f"DEBUG: {e}")  # Imprime l'erreur d'abord

            self.show_message("Erreur", f"Une erreur est survenue : {str(e)}", "critical")

    # --- MODIFICATION CRITIQUE ---
    def open_trading_screen(self, username):
        """Ouvre l'écran de jeu de trading."""
        # 1. Importer le NOUVEL écran de trading
        from src.ui.trading_screen import TradingScreen

        # 2. Créer l'instance du nouvel écran
        self.trading_screen = TradingScreen(username)
        self.trading_screen.show()

        # 3. Fermer la fenêtre de connexion
        self.close()

    def show_message(self, title, message, icon):
        """Affiche une boîte de dialogue stylisée."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
                border-radius: 10px;
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
                padding: 8px 16px;
                font-size: 14px;
            }
        """)
        if icon == "info":
            msg_box.setIcon(QMessageBox.Information)
        elif icon == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif icon == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        msg_box.exec_()


if __name__ == "__main__":
    # Ce bloc ne devrait pas être exécuté. 
    # Lancez l'application via main.py
    try:
        app = QApplication(sys.argv)
        window = LiquidGlassLogin()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erreur critique: {e}")
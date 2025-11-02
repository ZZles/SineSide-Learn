import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QPushButton, QFrame, QProgressBar, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtSvg import QSvgWidget

# L'import du menu des simulations est fait localement

class ProfileScreen(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("SineSide Learn")
        self.setWindowIcon(QIcon("C:/Users/Mavaax/3D Objects/SineSide-Learn/assets/logodark.png"))
        self.setFixedSize(1200, 800)
        self.setWindowOpacity(0.95)

        self.setStyleSheet("""
            QMainWindow { background-color: #1C1C1C; }
            QFrame { background-color: transparent; }
            QLabel#TitleLabel { font-size: 36px; font-weight: bold; color: #FF8C00; }
            QLabel#UsernameLabel { font-size: 18px; color: white; }
            QLabel#LevelLabel { font-size: 16px; color: #AAAAAA; margin-bottom: 5px; }
            QLabel#SectionTitle { font-size: 24px; font-weight: bold; color: white; margin-top: 20px; margin-bottom: 10px; }
            QProgressBar { height: 12px; border: 1px solid #FF8C00; border-radius: 6px; text-align: center; color: transparent; background-color: #1C1C1C; }
            QProgressBar::chunk { background-color: #FF8C00; border-radius: 5px; }
            /* NOUVEAU: Style pour le bouton de lancement */
            QPushButton#LaunchButton { 
                background-color: #FF8C00; 
                border: none; 
                border-radius: 10px; 
                padding: 20px; 
                color: white; 
                font-size: 22px; 
                font-weight: bold; 
            }
            QPushButton#LaunchButton:hover { background-color: #FFAD42; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        content_layout = QVBoxLayout(central_widget)
        content_layout.setContentsMargins(40, 20, 40, 40)
        content_layout.setSpacing(20)

        header_layout = self.create_header()
        content_layout.addLayout(header_layout)

        progress_achievements_layout = self.create_progress_achievements_section()
        content_layout.addLayout(progress_achievements_layout)
        content_layout.addStretch()

        # --- MODIFIÉ: Un seul bouton pour lancer le menu des simulations ---
        launch_button = QPushButton("Lancer une Simulation")
        launch_button.setObjectName("LaunchButton")
        launch_button.clicked.connect(self.open_simulations_menu)
        content_layout.addWidget(launch_button)
        content_layout.addStretch()

    def create_header(self):
        # ... (Inchangé)
        header_layout = QHBoxLayout()
        title_label = QLabel("SineSide")
        title_label.setObjectName("TitleLabel")
        header_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        header_layout.addStretch()
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(15)
        username_label = QLabel(self.username)
        username_label.setObjectName("UsernameLabel")
        profile_layout.addWidget(username_label)
        profile_pic = QLabel()
        pixmap = QPixmap("C:/Users/Mavaax/3D Objects/SineSide-Learn/assets/default_pfp.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic.setPixmap(pixmap)
        profile_layout.addWidget(profile_pic)
        header_layout.addLayout(profile_layout)
        return header_layout

    def create_progress_achievements_section(self):
        # ... (Inchangé)
        layout = QHBoxLayout()
        layout.setSpacing(30)
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        level_label = QLabel("Niveau 1 - Novice")
        level_label.setObjectName("LevelLabel")
        progress_layout.addWidget(level_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(25)
        progress_layout.addWidget(self.progress_bar)
        layout.addWidget(progress_frame, 2)
        achievements_frame = QFrame()
        achievements_layout = QGridLayout(achievements_frame)
        achievements_layout.setSpacing(15)
        for i in range(4):
            achievement_icon = QSvgWidget("C:/Users/Mavaax/3D Objects/SineSide-Learn/assets/reward1.svg")
            achievement_icon.setFixedSize(64, 64)
            achievements_layout.addWidget(achievement_icon, 0, i)
        layout.addWidget(achievements_frame, 3)
        return layout

    def open_simulations_menu(self):
        """Ouvre la nouvelle fenêtre de sélection des simulations."""
        from src.ui.simulations_menu import SimulationsMenu
        # On passe 'self' comme parent pour que le menu s'ouvre par-dessus
        menu = SimulationsMenu(self.username, self)
        menu.exec_()
        # Le code ici attend que le menu soit fermé

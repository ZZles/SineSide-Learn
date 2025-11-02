import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# L'import de TradingScreen est fait localement pour éviter les dépendances circulaires

class SimulationsMenu(QDialog):
    """Nouvelle fenêtre dédiée au choix des scénarios de simulation."""
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username

        self.setWindowTitle("SineSide Learn - Choix de la Simulation")
        self.setWindowIcon(QIcon("C:/Users/Mavaax/3D Objects/SineSide-Learn/assets/logodark.png"))
        self.setFixedSize(800, 600)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog { background-color: #1C1C1C; }
            QLabel#Title { font-size: 28px; font-weight: bold; color: #FF8C00; margin-bottom: 20px; }
            QPushButton { 
                background-color: #2E2E2E; 
                border: 1px solid #FF8C00; 
                border-radius: 10px; 
                padding: 20px; 
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                text-align: center; 
            }
            QPushButton:hover { background-color: #3c3c3c; border: 1px solid #FFAD42; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 40)
        main_layout.setAlignment(Qt.AlignTop)

        title_label = QLabel("Choisir un Scénario")
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        scenarios_layout = self.create_scenarios_grid()
        main_layout.addLayout(scenarios_layout)

    def create_scenarios_grid(self):
        scenarios_layout = QGridLayout()
        scenarios_layout.setSpacing(20)
        
        self.scenarios = {
            "Tutoriel Facile": ("Apprenez les bases dans un marché stable.", 1),
            "Marché Haussier": ("Profitez d'une tendance à la hausse claire.", 2),
            "Krach Soudain": ("Réagissez vite à une chute de marché inattendue.", 3),
            "Haute Volatilité": ("Maîtrisez le chaos d'un marché imprévisible.", 4)
        }

        row, col = 0, 0
        for name, (desc, stars) in self.scenarios.items():
            button = QPushButton(f"{name}\n{'★' * stars}{'☆' * (4 - stars)}")
            button.clicked.connect(lambda checked, n=name: self.launch_game(n))
            scenarios_layout.addWidget(button, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        return scenarios_layout

    def launch_game(self, scenario_name):
        """Lance l'écran de jeu et ferme le menu des simulations."""
        from src.ui.trading_screen import TradingScreen # Importation locale

        # On cache ce menu
        self.hide()

        # On lance le jeu comme un dialogue modal par-dessus la fenêtre de profil
        game_dialog = TradingScreen(self.username, scenario_name, self.parent())
        game_dialog.exec_()

        # Une fois le jeu terminé, on ferme aussi ce menu pour retourner au profil
        self.accept()

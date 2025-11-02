import sys
import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QMessageBox, QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QColor, QFont

# Imports Matplotlib
import matplotlib

matplotlib.use('Qt5Agg')  # Spécifier le backend Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Imports du projet
from src.game.simulator import Asset, MarketSimulator
from src.data.database import start_session, end_session, record_trade, get_user_stats

# Style "Liquid Glass Pro"
TRADING_STYLESHEET = """
    QMainWindow {
        background-color: #1e1e1e;
        border-radius: 15px;
    }
    QFrame#GlassPanel {
        background-color: rgba(40, 40, 40, 180); /* Effet verre fumé */
        border-radius: 15px;
        border: 1px solid rgba(255, 140, 0, 100); /* Accent orange */
    }
    QFrame#Header {
        background-color: rgba(30, 30, 30, 150);
        border-radius: 10px;
    }
    QLabel {
        color: white;
        font-family: 'Arial';
        font-size: 16px;
    }
    QLabel#Title {
        font-size: 24px;
        font-weight: bold;
        color: #FF8C00; /* Orange */
    }
    QLabel#PortfolioValue {
        font-size: 20px;
        font-weight: bold;
        color: white;
    }
    QLabel#PriceLabel {
        font-size: 28px;
        font-weight: bold;
        color: #FF8C00;
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
    }
    QPushButton#QuitButton {
        background-color: #d63031; /* Rouge */
    }
    QPushButton#QuitButton:hover {
        background-color: #e17055;
    }
    QLineEdit {
        background-color: rgba(255, 255, 255, 10);
        border: 1px solid rgba(255, 140, 0, 100);
        border-radius: 10px;
        padding: 12px;
        color: white;
        font-size: 16px;
    }
"""


class MatplotlibCanvas(FigureCanvas):
    """Widget Canvas pour Matplotlib."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        # Style du graphique
        self.fig.patch.set_facecolor('#1e1e1e')
        self.axes.set_facecolor('#2a2a2a')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.spines['left'].set_color('white')
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['right'].set_color('none')
        self.axes.spines['top'].set_color('none')

        super(MatplotlibCanvas, self).__init__(self.fig)


class TradingScreen(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"SineSide Learn - Session de Trading")
        self.setFixedSize(1200, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(TRADING_STYLESHEET)

        # --- État du jeu ---
        self.initial_balance = 10000.0
        self.balance = self.initial_balance
        self.shares = 0.0
        self.portfolio_value = self.initial_balance
        self.current_price = 0.0

        # --- Session de la Base de Données ---
        try:
            self.session_id = start_session(self.username)
        except Exception as e:
            self.show_message("Erreur Critique", f"Impossible de démarrer la session BDD: {e}", "critical")
            self.close()
            return

        # --- Simulateur de Marché ---
        btc_asset = Asset(symbol="BTC", name="Bitcoin", base_price=50000, volatility=0.02)
        self.simulator = MarketSimulator([btc_asset])
        self.current_price = btc_asset.base_price  # Prix initial

        # --- Initialisation de l'UI ---
        self.init_ui()

        # --- Timer pour le "Tick" du marché ---
        self.timer = QTimer()
        self.timer.setInterval(1000)  # Mise à jour chaque seconde
        self.timer.timeout.connect(self.update_game_tick)
        self.timer.start()

        # Animation de fondu
        self.fade_in_animation()

    def init_ui(self):
        """Construit l'interface utilisateur."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- 1. Header (Titre & Portefeuille) ---
        header_frame = QFrame()
        header_frame.setObjectName("Header")
        header_layout = QHBoxLayout(header_frame)

        self.title_label = QLabel(f"Utilisateur: {self.username}")
        self.title_label.setObjectName("Title")

        self.portfolio_label = QLabel(f"Portefeuille: ${self.portfolio_value:,.2f}")
        self.portfolio_label.setObjectName("PortfolioValue")
        self.portfolio_label.setAlignment(Qt.AlignRight)

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.portfolio_label)

        # --- 2. Contenu Principal (Graphique & Panneau) ---
        content_layout = QHBoxLayout()

        # 2a. Graphique (Gauche)
        self.canvas = MatplotlibCanvas(self, width=8, height=6)
        content_layout.addWidget(self.canvas, 7)  # 70% de la largeur

        # 2b. Panneau de Contrôle (Droite)
        control_panel = QFrame()
        control_panel.setObjectName("GlassPanel")
        control_panel.setGraphicsEffect(self.create_shadow())

        panel_layout = QVBoxLayout(control_panel)
        panel_layout.setSpacing(15)
        panel_layout.setContentsMargins(20, 20, 20, 20)

        self.price_label = QLabel(f"${self.current_price:,.2f}")
        self.price_label.setObjectName("PriceLabel")
        self.price_label.setAlignment(Qt.AlignCenter)

        self.balance_label = QLabel(f"Balance: ${self.balance:,.2f}")
        self.shares_label = QLabel(f"Actions (BTC): {self.shares:.4f}")

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Quantité (ex: 0.1)")

        self.buy_button = QPushButton("ACHETER")
        self.sell_button = QPushButton("VENDRE")
        self.quit_button = QPushButton("Terminer la Session")
        self.quit_button.setObjectName("QuitButton")

        # Connexions des boutons
        self.buy_button.clicked.connect(self.handle_buy)
        self.sell_button.clicked.connect(self.handle_sell)
        self.quit_button.clicked.connect(self.end_game_session)

        panel_layout.addWidget(QLabel("Prix Actuel (BTC)"), 0, Qt.AlignCenter)
        panel_layout.addWidget(self.price_label)
        panel_layout.addStretch(1)
        panel_layout.addWidget(self.balance_label)
        panel_layout.addWidget(self.shares_label)
        panel_layout.addWidget(self.amount_input)
        panel_layout.addWidget(self.buy_button)
        panel_layout.addWidget(self.sell_button)
        panel_layout.addStretch(2)
        panel_layout.addWidget(self.quit_button)

        content_layout.addWidget(control_panel, 3)  # 30% de la largeur

        # --- Assemblage Final ---
        main_layout.addWidget(header_frame)
        main_layout.addLayout(content_layout)

    def update_game_tick(self):
        """Mise à jour à chaque tick du timer."""
        # 1. Obtenir le nouveau prix
        tick = self.simulator.step()
        self.current_price = tick.prices["BTC"]

        # 2. Mettre à jour la valeur du portefeuille
        self.portfolio_value = self.balance + (self.shares * self.current_price)

        # 3. Mettre à jour les labels
        self.price_label.setText(f"${self.current_price:,.2f}")
        self.balance_label.setText(f"Balance: ${self.balance:,.2f}")
        self.shares_label.setText(f"Actions (BTC): {self.shares:.4f}")
        self.portfolio_label.setText(f"Portefeuille: ${self.portfolio_value:,.2f}")

        # 4. Mettre à jour le graphique
        self.update_plot()

    def update_plot(self):
        """Redessine le graphique Matplotlib."""
        history = self.simulator.get_history("BTC", n_points=50)
        self.canvas.axes.clear()  # Effacer l'ancien graphique

        # Redéfinir le style (car clear() l'enlève)
        self.canvas.axes.set_facecolor('#2a2a2a')
        self.canvas.axes.tick_params(axis='x', colors='white')
        self.canvas.axes.tick_params(axis='y', colors='white')
        self.canvas.axes.spines['left'].set_color('white')
        self.canvas.axes.spines['bottom'].set_color('white')
        self.canvas.axes.spines['right'].set_color('none')
        self.canvas.axes.spines['top'].set_color('none')

        # Dessiner la ligne de prix
        self.canvas.axes.plot(history, color='#FF8C00', linewidth=2)
        self.canvas.axes.set_title("Prix BTC/USD (50 derniers ticks)", color="white")
        self.canvas.draw()

    def handle_buy(self):
        """Logique d'achat."""
        try:
            amount = float(self.amount_input.text())
            if amount <= 0:
                raise ValueError("La quantité doit être positive")

            cost = self.current_price * amount

            if self.balance >= cost:
                self.balance -= cost
                self.shares += amount
                record_trade(self.session_id, 'BUY', self.current_price, amount)
                self.show_message("Achat Réussi", f"Achat de {amount:.4f} BTC pour ${cost:,.2f}", "info")
            else:
                self.show_message("Échec", "Fonds insuffisants.", "warning")

        except ValueError as e:
            self.show_message("Erreur", f"Veuillez entrer une quantité valide (ex: 0.1)\n{e}", "warning")

        self.amount_input.clear()

    def handle_sell(self):
        """Logique de vente."""
        try:
            amount = float(self.amount_input.text())
            if amount <= 0:
                raise ValueError("La quantité doit être positive")

            if self.shares >= amount:
                gain = self.current_price * amount
                self.balance += gain
                self.shares -= amount
                record_trade(self.session_id, 'SELL', self.current_price, amount)
                self.show_message("Vente Réussie", f"Vente de {amount:.4f} BTC pour ${gain:,.2f}", "info")
            else:
                self.show_message("Échec", "Pas assez d'actions à vendre.", "warning")

        except ValueError as e:
            self.show_message("Erreur", f"Veuillez entrer une quantité valide (ex: 0.1)\n{e}", "warning")

        self.amount_input.clear()

    def end_game_session(self):
        """Termine la session, calcule le profit et ferme la fenêtre."""
        self.timer.stop()  # Arrêter le jeu

        # Vente forcée de toutes les actions restantes
        if self.shares > 0:
            final_sale = self.shares * self.current_price
            self.balance += final_sale
            self.shares = 0
            self.show_message("Info", f"Vente automatique de {self.shares:.4f} BTC pour ${final_sale:,.2f}", "info")

        # Calcul du résultat
        profit = self.balance - self.initial_balance
        result = 'WIN' if profit > 0 else ('LOSS' if profit < 0 else 'DRAW')

        # Enregistrement dans la BDD
        end_session(self.session_id, result, profit)

        # Afficher les stats
        stats = get_user_stats(self.username)

        self.show_message(
            "Session Terminée",
            f"Profit de la session: ${profit:,.2f}\n"
            f"Résultat: {result}\n\n"
            f"--- Stats Globales ({self.username}) ---\n"
            f"Sessions jouées: {stats['total_sessions']}\n"
            f"Victoires: {stats['wins']}\n"
            f"Défaites: {stats['losses']}\n"
            f"Profit Total: ${stats['total_profit']:,.2f}",
            "info"
        )

        self.close()  # Ferme cette fenêtre

    def closeEvent(self, event):
        """S'assure que la session est terminée avant de fermer."""
        if self.timer.isActive():
            self.end_game_session()  # Assure la sauvegarde

        # Rouvrir la fenêtre de connexion
        from src.ui.profile_screen import LiquidGlassLogin
        self.login_window = LiquidGlassLogin()
        self.login_window.show()

        event.accept()

    def create_shadow(self):
        """Crée un effet d'ombre."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(255, 140, 0, 120))  # Ombre orange
        shadow.setOffset(0, 0)
        return shadow

    def fade_in_animation(self):
        """Animation de fondu au démarrage."""
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setDuration(800)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_anim.start()

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
    # Ce bloc est pour tester CET ÉCRAN uniquement
    # Lancez l'application via main.py
    app = QApplication(sys.argv)
    window = TradingScreen("TestUser")
    window.show()
    sys.exit(app.exec_())
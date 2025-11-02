import sys
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# --- NOUVELLE TECHNOLOGIE DE GRAPHIQUE ---
import pyqtgraph as pg

from src.game.simulator import Asset, MarketSimulator
from src.data.database import start_session, end_session, record_trade

class TradingScreen(QDialog):
    def __init__(self, username, scenario_name, parent=None):
        super().__init__(parent)
        self.username = username
        self.scenario_name = scenario_name
        self.session_id = None
        self.is_closing = False

        self.setWindowTitle("SineSide Learn")
        self.setWindowIcon(QIcon("C:/Users/Mavaax/3D Objects/SineSide-Learn/assets/logodark.png"))
        self.setFixedSize(1200, 700)
        self.setWindowOpacity(0.95)
        self.setModal(True)

        self.setStyleSheet(""" ... """) # Style inchangé

        self.init_game_state()
        if self.session_id is None:
            QTimer.singleShot(0, self.reject)
            return
            
        self.init_ui()
        self.init_timers()

    def init_game_state(self):
        # ... (Inchangé)
        self.session_id = start_session(self.username)
        if not self.session_id:
            QMessageBox.critical(self, "Erreur Critique", "Impossible de démarrer une session.")
            return
        self.initial_balance = 10000.0
        self.balance = self.initial_balance
        self.shares = 0.0
        btc_asset = Asset(symbol="BTC", name="Bitcoin", base_price=50000, volatility=0.02)
        self.simulator = MarketSimulator([btc_asset], scenario_name=self.scenario_name)
        self.current_price = btc_asset.base_price

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_frame = QFrame()
        header_frame.setObjectName("Header")
        header_layout = QHBoxLayout(header_frame)
        main_layout.addWidget(header_frame)

        self.title_label = QLabel(f"Utilisateur: {self.username}")
        self.timer_label = QLabel("Temps restant: 02:00")
        self.portfolio_label = QLabel(f"Portefeuille: ${self.initial_balance:,.2f}")
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.timer_label)
        header_layout.addWidget(self.portfolio_label)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- MODIFIÉ: Remplacement de Matplotlib par PyQtGraph ---
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_data = self.plot_widget.plot(pen=pg.mkPen(color='#FF8C00', width=2))
        content_layout.addWidget(self.plot_widget, 7)

        control_panel = QFrame()
        control_panel.setObjectName("ControlPanel")
        panel_layout = QVBoxLayout(control_panel)
        content_layout.addWidget(control_panel, 3)

        self.price_label = QLabel(f"${self.current_price:,.2f}")
        self.balance_label = QLabel(f"Balance: ${self.balance:,.2f}")
        self.shares_label = QLabel(f"Actions (BTC): {self.shares:.4f}")
        self.amount_input = QLineEdit()
        self.buy_button = QPushButton("ACHETER")
        self.sell_button = QPushButton("VENDRE")
        self.quit_button = QPushButton("Terminer la Session")

        panel_layout.addWidget(self.price_label)
        panel_layout.addWidget(self.balance_label)
        panel_layout.addWidget(self.shares_label)
        panel_layout.addWidget(self.amount_input)
        panel_layout.addWidget(self.buy_button)
        panel_layout.addWidget(self.sell_button)
        panel_layout.addStretch()
        panel_layout.addWidget(self.quit_button)

        self.buy_button.clicked.connect(self.handle_buy)
        self.sell_button.clicked.connect(self.handle_sell)
        self.quit_button.clicked.connect(self.end_game_session)

    def init_timers(self):
        # ... (Inchangé)
        self.time_left = 120
        self.market_timer = QTimer(self)
        self.market_timer.setInterval(1000)
        self.market_timer.timeout.connect(self.update_game_tick)
        self.market_timer.start()
        self.game_timer = QTimer(self)
        self.game_timer.setInterval(1000)
        self.game_timer.timeout.connect(self.update_timer_display)
        self.game_timer.start()

    def update_game_tick(self):
        if self.is_closing: return
        tick = self.simulator.step()
        self.current_price = tick.prices["BTC"]
        self.update_ui_labels()
        self.update_plot()

    def update_timer_display(self):
        # ... (Inchangé)
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.setText(f"Temps restant: {mins:02d}:{secs:02d}")
        if self.time_left <= 0:
            self.end_game_session()

    def update_ui_labels(self):
        # ... (Inchangé)
        portfolio_value = self.balance + (self.shares * self.current_price)
        self.price_label.setText(f"${self.current_price:,.2f}")
        self.balance_label.setText(f"Balance: ${self.balance:,.2f}")
        self.shares_label.setText(f"Actions (BTC): {self.shares:.4f}")
        self.portfolio_label.setText(f"Portefeuille: ${portfolio_value:,.2f}")

    def update_plot(self):
        """Met à jour le graphique PyQtGraph."""
        history = self.simulator.get_history("BTC", n_points=100)
        self.plot_data.setData(history)

    def handle_buy(self):
        # ... (Inchangé)
        pass

    def handle_sell(self):
        # ... (Inchangé)
        pass

    def end_game_session(self):
        if self.is_closing: return
        self.is_closing = True
        self.market_timer.stop()
        self.game_timer.stop()
        # Pas besoin de cleanup avec PyQtGraph, il est géré par Qt
        if self.shares > 0:
            final_sale = self.shares * self.current_price
            self.balance += final_sale
            record_trade(self.session_id, 'SELL', self.current_price, self.shares)
        profit = self.balance - self.initial_balance
        result = 'WIN' if profit > 0 else ('LOSS' if profit < 0 else 'DRAW')
        if self.session_id:
            end_session(self.session_id, result, profit)
        self.accept()

    def closeEvent(self, event):
        self.end_game_session()
        event.accept()

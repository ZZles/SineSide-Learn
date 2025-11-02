import random
import math
import time
from dataclasses import dataclass

@dataclass
class Asset:
    symbol: str
    name: str
    base_price: float
    volatility: float

class MarketTick:
    def __init__(self, timestamp, prices):
        self.timestamp = timestamp
        self.prices = prices

class MarketSimulator:
    def __init__(self, assets, scenario_name="Tutoriel Facile"):
        self.assets = {asset.symbol: asset for asset in assets}
        self.price_history = {asset.symbol: [asset.base_price] for asset in assets}
        self.scenario_name = scenario_name
        self.tick_count = 0

        self.trend = 0
        self.volatility_multiplier = 1.0

        self.setup_scenario()

    def setup_scenario(self):
        """Configure les paramètres du simulateur."""
        if self.scenario_name == "Marché Haussier":
            self.trend = random.uniform(0.0005, 0.001)
            self.volatility_multiplier = 0.8

        # --- DÉBOGAGE: Le Krach Soudain utilise temporairement les mêmes paramètres que le Tutoriel ---
        elif self.scenario_name == "Krach Soudain":
            self.trend = random.uniform(-0.0001, 0.0001) # Paramètres sûrs
            self.volatility_multiplier = 0.5 # Paramètres sûrs

        elif self.scenario_name == "Haute Volatilité":
            self.trend = 0
            self.volatility_multiplier = 2.5

        else: # Tutoriel Facile
            self.trend = random.uniform(-0.0001, 0.0001)
            self.volatility_multiplier = 0.5

    def _update_trend(self):
        if self.scenario_name not in ["Marché Haussier", "Krach Soudain"]:
             self.trend += random.uniform(-0.00005, 0.00005)
             self.trend = max(-0.001, min(0.001, self.trend))

    def step(self):
        self.tick_count += 1
        now = time.time()
        new_prices = {}

        self._update_trend()

        for symbol, asset in self.assets.items():
            last_price = self.price_history[symbol][-1]
            
            noise = random.gauss(0, asset.volatility * self.volatility_multiplier * 0.1)
            
            new_price = last_price * (1 + self.trend + noise)

            mean_reversion = (asset.base_price - new_price) * 0.0005
            new_price += mean_reversion
            
            new_price = max(0.1, new_price)

            new_prices[symbol] = new_price
            self.price_history[symbol].append(new_price)

        return MarketTick(timestamp=now, prices=new_prices)

    def get_history(self, symbol, n_points=100):
        hist = self.price_history.get(symbol, [])
        return hist[-n_points:]

    def current_price(self, symbol):
        hist = self.price_history.get(symbol, [])
        return hist[-1] if hist else None

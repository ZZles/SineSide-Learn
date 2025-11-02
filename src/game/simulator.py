import random
import math
import time
from dataclasses import dataclass


@dataclass
class Asset:
    """Représente un actif simulé (ex: BTC, ETH, etc.)"""
    symbol: str
    name: str
    base_price: float
    volatility: float


class MarketTick:
    """Structure contenant les prix simulés à un instant t."""

    def __init__(self, timestamp, prices):
        self.timestamp = timestamp
        self.prices = prices


class MarketSimulator:
    """
    Simule un marché avec des prix évoluant aléatoirement.
    Utilisé par le jeu de trading pour afficher un graphique en temps réel.
    """

    def __init__(self, assets, profile="NORMAL"):
        self.assets = {asset.symbol: asset for asset in assets}
        # Initialiser avec une base_price pour éviter les erreurs sur [-1]
        self.price_history = {asset.symbol: [asset.base_price] for asset in assets}
        self.profile = profile
        self.last_tick_time = time.time()

    def _get_drift_factor(self):
        """Définit la tendance générale selon le profil du marché."""
        if self.profile == "VOLATILE":
            return random.uniform(-0.05, 0.05)
        elif self.profile == "BULLISH":
            return random.uniform(0.0, 0.03)
        elif self.profile == "BEARISH":
            return random.uniform(-0.03, 0.0)
        else:
            return random.uniform(-0.01, 0.01)

    def step(self):
        """Fait avancer la simulation d’un ‘tick’ (nouvelle valeur de prix)."""
        now = time.time()
        # Pas besoin d'elapsed time pour cette simulation simple
        self.last_tick_time = now

        new_prices = {}

        for symbol, asset in self.assets.items():
            last_price = self.price_history[symbol][-1]
            drift = self._get_drift_factor()
            # Multiplier la volatilité par 0.1 pour la calmer un peu
            noise = random.gauss(0, asset.volatility * 0.1)

            # Formule de Mouvement Géométrique Brownien (simplifiée)
            # Ajout d'une petite tendance au retour à la moyenne (vers base_price)
            mean_reversion = (asset.base_price - last_price) * 0.001

            new_price = last_price * (1 + drift + noise) + mean_reversion
            new_price = max(0.1, new_price)  # Éviter les prix négatifs

            new_prices[symbol] = new_price
            self.price_history[symbol].append(new_price)

        return MarketTick(timestamp=now, prices=new_prices)

    def get_history(self, symbol, n_points=100):
        """Retourne les n derniers points de l’historique."""
        hist = self.price_history.get(symbol, [])
        return hist[-n_points:]

    def current_price(self, symbol):
        """Retourne le prix actuel d’un actif."""
        hist = self.price_history.get(symbol, [])
        return hist[-1] if hist else None
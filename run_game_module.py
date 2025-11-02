import sys
from PyQt5.QtWidgets import QApplication

# --- POINT D'ENTRÉE MODULAIRE ---
# Pour intégrer ce jeu dans une autre application Qt, vous n'aurez besoin que de ces lignes.

# 1. Assurez-vous que le chemin vers la racine du projet est dans le sys.path
# (Cela peut ne pas être nécessaire selon la structure de votre projet principal)
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Importez la fenêtre de lancement du module de jeu
from src.ui.login_screen import LiquidGlassLogin

# Variable globale pour garder une référence à la fenêtre du jeu
game_window = None

def launch_sineside_learn_module():
    """
    Fonction pour lancer le module de jeu SineSide Learn.
    Elle peut être appelée depuis n'importe quelle autre partie de votre application principale.
    """
    global game_window
    
    # S'assure qu'une seule instance du jeu est ouverte à la fois
    if game_window is None or not game_window.isVisible():
        # L'écran de connexion gère le reste du flux (profil, jeu, etc.)
        game_window = LiquidGlassLogin()
        game_window.show()
    else:
        # Si la fenêtre existe déjà, on la ramène au premier plan
        game_window.activateWindow()
        game_window.raise_()


if __name__ == "__main__":
    # Ce bloc permet de tester le module de manière autonome.
    # Votre application principale n'utilisera que la fonction launch_sineside_learn_module().
    
    app = QApplication.instance() # Récupère l'instance existante s'il y en a une
    if app is None:
        app = QApplication(sys.argv)

    print("Lancement du module SineSide Learn en mode autonome...")
    launch_sineside_learn_module()
    
    # La boucle d'événements doit être gérée par l'application principale.
    # Si on exécute ce script seul, on a besoin de app.exec_().
    if not QApplication.instance():
         sys.exit(app.exec_())

import sys
import os
from PyQt5.QtWidgets import QApplication
from src.data.database import init_database
from src.ui.profile_screen import LiquidGlassLogin

# --- Configuration du chemin ---
# Ajoute la racine du projet au PYTHONPATH pour que les imports (ex: "from src...") fonctionnent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Point d'entrée principal de l'application."""
    try:
        # 1. Initialiser la base de données au démarrage
        print("Initialisation de la base de données...")
        init_database()

        # 2. Créer l'application Qt
        app = QApplication(sys.argv)

        # 3. Lancer la fenêtre de connexion
        # La fenêtre de connexion gérera elle-même l'ouverture
        # de l'écran de jeu une fois la connexion réussie.
        login_window = LiquidGlassLogin()
        login_window.show()

        # 4. Exécuter l'application
        sys.exit(app.exec_())

    except ImportError as e:
        print(f"Erreur d'importation critique : {e}")
        print(
            "Veuillez vous assurer que tous les modules (PyQt5, matplotlib, numpy) sont installés via requirements.txt")
        print("Assurez-vous aussi que la structure de vos fichiers est correcte.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")


if __name__ == "__main__":
    main()
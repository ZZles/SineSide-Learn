import sys
import os
from PyQt5.QtWidgets import QApplication
from src.data.database import init_database
# --- MODIFIÉ: Importer depuis le nouveau fichier de connexion ---
from src.ui.login_screen import LiquidGlassLogin

# --- Configuration du chemin ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Point d'entrée principal de l'application."""
    try:
        # 1. Initialiser la base de données
        print("Initialisation de la base de données...")
        init_database()

        # 2. Créer l'application Qt
        app = QApplication(sys.argv)

        # 3. Lancer la fenêtre de connexion
        # Elle gérera l'ouverture de l'écran de profil.
        login_window = LiquidGlassLogin()
        login_window.show()

        # 4. Exécuter l'application
        sys.exit(app.exec_())

    except ImportError as e:
        print(f"Erreur d'importation critique : {e}")
        print(
            "Veuillez vous assurer que tous les modules (PyQt5, matplotlib, numpy) sont installés via requirements.txt")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")


if __name__ == "__main__":
    main()

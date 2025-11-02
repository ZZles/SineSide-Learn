import sqlite3
import os
from datetime import datetime

# Chemin robuste vers la base de données, située à la racine du projet.
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sineside_learn.db'))

def get_connection():
    """Crée le dossier parent si nécessaire et retourne une connexion à la BDD."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Permet d'accéder aux colonnes par leur nom
    return conn

def init_database():
    """Crée les tables si elles n'existent pas et gère les migrations simples."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Table des utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL, -- En production, devrait être un hash
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des sessions de jeu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                result TEXT, -- 'WIN', 'LOSS', 'DRAW', 'IN_PROGRESS'
                profit REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Table des transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                action TEXT NOT NULL CHECK (action IN ('BUY', 'SELL')),
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        # Logique de migration simple (exemple)
        cursor.execute("PRAGMA table_info(users)")
        columns = [column['name'] for column in cursor.fetchall()]
        if 'email' not in columns:
            print("MIGRATION: Ajout de la colonne 'email' à la table 'users'...")
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT 'no-email@example.com'")

        conn.commit()
        print(f"Base de données initialisée et vérifiée : {DB_PATH}")

def add_user(username: str, email: str, password: str) -> bool:
    """Ajoute un nouvel utilisateur. Retourne True en cas de succès, False sinon."""
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            print(f"Utilisateur '{username}' créé.")
            return True
        except sqlite3.IntegrityError:
            print(f"L'utilisateur '{username}' existe déjà.")
            return False

def check_user_exists(username: str) -> bool:
    """Vérifie si un utilisateur existe."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

def start_session(username: str) -> int | None:
    """Crée une nouvelle session de jeu et retourne son ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        user = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            print(f"Erreur: Utilisateur '{username}' introuvable pour démarrer la session.")
            return None
        
        user_id = user['id']
        start_time = datetime.now().isoformat()
        
        result = cursor.execute(
            "INSERT INTO sessions (user_id, start_time, result, profit) VALUES (?, ?, ?, ?)",
            (user_id, start_time, 'IN_PROGRESS', 0.0)
        )
        conn.commit()
        session_id = result.lastrowid
        print(f"Nouvelle session (ID: {session_id}) pour l'utilisateur {user_id}.")
        return session_id

def end_session(session_id: int, result: str, profit: float):
    """Met fin à une session et enregistre le résultat."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET end_time = ?, result = ?, profit = ? WHERE id = ?",
            (datetime.now().isoformat(), result, profit, session_id)
        )
        conn.commit()
        print(f"Session {session_id} terminée. Résultat: {result}, Profit: {profit:.2f}")

def record_trade(session_id: int, action: str, price: float, quantity: float):
    """Enregistre une transaction."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO trades (session_id, action, price, quantity, timestamp) VALUES (?, ?, ?, ?, ?)",
            (session_id, action, price, quantity, datetime.now().isoformat())
        )
        conn.commit()

def get_user_stats(username: str) -> dict:
    """Retourne les statistiques globales d'un utilisateur."""
    with get_connection() as conn:
        stats = conn.execute("""
            SELECT 
                COUNT(s.id) AS total_sessions,
                SUM(CASE WHEN s.result = 'WIN' THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN s.result = 'LOSS' THEN 1 ELSE 0 END) AS losses,
                SUM(s.profit) AS total_profit
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE u.username = ? AND s.result != 'IN_PROGRESS'
        """, (username,)).fetchone()

        if stats and stats['total_sessions'] > 0:
            return dict(stats)
        else:
            return {"total_sessions": 0, "wins": 0, "losses": 0, "total_profit": 0.0}

if __name__ == "__main__":
    print("Initialisation de la base de données en mode test...")
    init_database()
    # Ajout d'un utilisateur de test
    if not check_user_exists("testuser"):
        add_user("testuser", "test@example.com", "password")
    # Démarrage et fin d'une session de test
    session_id = start_session("testuser")
    if session_id:
        record_trade(session_id, 'BUY', 50000, 0.1)
        end_session(session_id, 'WIN', 123.45)
    print("\nStatistiques pour 'testuser':")
    print(get_user_stats("testuser"))

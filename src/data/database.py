import sqlite3
import os
from datetime import datetime

# 📍 Chemin vers la base de données (MODIFIÉ)
# Place la BDD à la racine du projet (ex: SineSide-Learn/sineside_learn.db)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'sineside_learn.db')


# --- 🔗 Connexion & Initialisation ---
def get_connection():
    """Retourne une connexion SQLite vers la base de données."""
    # os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) # Plus besoin si c'est à la racine
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_database():
    """Crée les tables si elles n'existent pas encore + migration automatique."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- Table des utilisateurs ---
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       email
                       TEXT
                       NOT
                       NULL,
                       password
                       TEXT
                       NOT
                       NULL,
                       created_at
                       TEXT
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)

    # 🔧 MIGRATION : Vérifier si la colonne 'email' existe (pour les anciennes BDD)
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'email' not in columns:
        print("⚙️ Migration: Ajout de la colonne 'email' à la table users...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT 'non-renseigne@email.com'")
            print("✅ Colonne 'email' ajoutée avec succès")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Erreur lors de la migration : {e}")

    # --- Table des sessions de jeu ---
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS sessions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       start_time
                       TEXT,
                       end_time
                       TEXT,
                       result
                       TEXT,
                       profit
                       REAL,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   )
                       )
                   """)

    # --- Table des transactions ---
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS trades
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       session_id
                       INTEGER,
                       action
                       TEXT
                       CHECK (
                       action
                       IN
                   (
                       'BUY',
                       'SELL'
                   )),
                       price REAL,
                       quantity REAL,
                       timestamp TEXT,
                       FOREIGN KEY
                   (
                       session_id
                   ) REFERENCES sessions
                   (
                       id
                   )
                       )
                   """)

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée :", DB_PATH)


# --- 👤 Gestion des utilisateurs ---
def add_user(username: str, email: str, password: str):
    """Ajoute un nouvel utilisateur dans la base."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        print(f"✅ Utilisateur '{username}' créé avec succès")
    except sqlite3.IntegrityError:
        print(f"⚠️ L'utilisateur '{username}' existe déjà")
    finally:
        conn.close()


def check_user_exists(username: str) -> bool:
    """Vérifie si un utilisateur existe déjà."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def get_user(username: str):
    """Retourne les informations complètes d'un utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


# --- 🕹️ Gestion des sessions de jeu ---
def start_session(username: str):
    """Crée une nouvelle session de jeu et la retourne."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Utilisateur '{username}' introuvable")

    user_id = row[0]
    start_time = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO sessions (user_id, start_time, result, profit) VALUES (?, ?, ?, ?)",
        (user_id, start_time, 'IN_PROGRESS', 0.0)
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    print(f"Nouvelle session démarrée (ID: {session_id}) pour {username}")
    return session_id


def end_session(session_id: int, result: str, profit: float):
    """Met fin à une session et enregistre le résultat."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET end_time = ?, result = ?, profit = ? WHERE id = ?",
        (datetime.now().isoformat(), result, profit, session_id)
    )
    conn.commit()
    print(f"Session {session_id} terminée. Résultat: {result}, Profit: {profit}")
    conn.close()


# --- 💹 Gestion des trades ---
def record_trade(session_id: int, action: str, price: float, quantity: float):
    """Enregistre une transaction (achat ou vente)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trades (session_id, action, price, quantity, timestamp) VALUES (?, ?, ?, ?, ?)",
        (session_id, action, price, quantity, datetime.now().isoformat())
    )
    conn.commit()
    print(f"Trade enregistré: {action} {quantity} @ {price}")
    conn.close()


# --- 🧾 Statistiques & Historique ---
def get_user_stats(username: str):
    """Retourne les statistiques globales d'un utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT COUNT(s.id)                                        AS total_sessions,
                          SUM(CASE WHEN s.result = 'WIN' THEN 1 ELSE 0 END)  AS wins,
                          SUM(CASE WHEN s.result = 'LOSS' THEN 1 ELSE 0 END) AS losses,
                          SUM(s.profit)                                      AS total_profit
                   FROM sessions s
                            JOIN users u ON u.id = s.user_id
                   WHERE u.username = ? AND s.result != 'IN_PROGRESS'
                   """, (username,))

    stats = cursor.fetchone()
    conn.close()

    if not stats or stats[0] is None or stats[0] == 0:
        return {"total_sessions": 0, "wins": 0, "losses": 0, "total_profit": 0.0}

    return {
        "total_sessions": stats[0],
        "wins": stats[1] if stats[1] else 0,
        "losses": stats[2] if stats[2] else 0,
        "total_profit": stats[3] if stats[3] else 0.0
    }


# --- 🧩 Exécution directe ---
if __name__ == "__main__":
    init_database()
    print("✅ Vérification structure OK")
# database.py - WERSJA PRO (POSTGRESQL / SUPABASE)
import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

# Wczytujemy zmienne (potrzebne, jeśli uruchamiasz plik bezpośrednio)
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Tworzy połączenie z bazą PostgreSQL."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"❌ Błąd połączenia z bazą: {e}")
        return None

def init_db():
    """Tworzy tabelę użytkowników i projektów w Postgresie."""
    conn = get_connection()
    if not conn: return
    
    try:
        with conn:
            with conn.cursor() as c:
                # Tabela Użytkowników
                c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        email TEXT UNIQUE,
                        password_hash BYTEA,
                        tier TEXT DEFAULT 'Free',
                        is_admin BOOLEAN DEFAULT FALSE,
                        credits INTEGER DEFAULT 3
                    );
                ''')
                
                # Tabela Projektów
                c.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id SERIAL PRIMARY KEY,
                        username TEXT REFERENCES users(username),
                        project_name TEXT,
                        folder_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
        print("✅ Baza danych zainicjowana (PostgreSQL).")
    except Exception as e:
        print(f"❌ Błąd inicjalizacji: {e}")
    finally:
        conn.close()

# --- FUNKCJE UŻYTKOWNIKA ---

def create_user(username, email, password):
    conn = get_connection()
    if not conn: return False, "Błąd połączenia."
    
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    initial_tier = "Free"
    is_admin = False
    initial_credits = 3
    
    # Backdoor dla Admina
    if username == "admin": 
        initial_tier = "Premium"
        is_admin = True
        initial_credits = 999999

    try:
        with conn:
            with conn.cursor() as c:
                # W Postgres używamy %s zamiast ?
                c.execute(
                    'INSERT INTO users (username, email, password_hash, tier, is_admin, credits) VALUES (%s, %s, %s, %s, %s, %s)', 
                    (username, email, hashed, initial_tier, is_admin, initial_credits)
                )
        return True, "Konto utworzone."
    except psycopg2.errors.UniqueViolation:
        return False, "Login lub Email już zajęty."
    except Exception as e:
        return False, f"Błąd bazy: {e}"
    finally:
        conn.close()

def check_login(username, password):
    conn = get_connection()
    if not conn: return False, None, None, None, 0
    
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('SELECT password_hash, tier, is_admin, email, credits FROM users WHERE username = %s', (username,))
                user = c.fetchone()
        
        if user:
            stored_hash = bytes(user[0]) # Postgres zwraca memoryview/bytes
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True, user[1], user[2], user[3], user[4]
        
        return False, None, None, None, 0
    except Exception as e:
        print(f"Błąd logowania: {e}")
        return False, None, None, None, 0
    finally:
        conn.close()

def update_user_tier(username, new_tier):
    credits_map = {"Basic": 10, "Standard": 30, "Premium": 100}
    new_credits = credits_map.get(new_tier, 5)
    
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('UPDATE users SET tier = %s, credits = %s WHERE username = %s', (new_tier, new_credits, username))
    finally:
        conn.close()

def update_tier_by_email(email, new_tier):
    credits_map = {"Basic": 10, "Standard": 30, "Premium": 100}
    new_credits = credits_map.get(new_tier, 5)
    
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('UPDATE users SET tier = %s, credits = %s WHERE email = %s', (new_tier, new_credits, email))
    finally:
        conn.close()

def add_user_credits(username, amount):
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('UPDATE users SET credits = credits + %s WHERE username = %s', (amount, username))
    finally:
        conn.close()

def deduct_credits(username, amount=1):
    conn = get_connection()
    if not conn: return False
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('SELECT credits, is_admin FROM users WHERE username = %s', (username,))
                res = c.fetchone()
                
                if not res: return False
                current, is_admin = res[0], res[1]
                
                if is_admin: return True # Admin free
                
                if current >= amount:
                    c.execute('UPDATE users SET credits = credits - %s WHERE username = %s', (amount, username))
                    return True
                else:
                    return False
    finally:
        conn.close()

def get_user_credits(username):
    conn = get_connection()
    if not conn: return 0
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('SELECT credits FROM users WHERE username = %s', (username,))
                res = c.fetchone()
        return res[0] if res else 0
    finally:
        conn.close()

def get_user_details(username):
    conn = get_connection()
    if not conn: return None
    try:
        with conn:
            with conn.cursor() as c:
                c.execute('SELECT tier, is_admin, email, credits FROM users WHERE username = %s', (username,))
                user = c.fetchone()
        if user:
            return {"tier": user[0], "is_admin": user[1], "email": user[2], "credits": user[3]}
        return None
    finally:
        conn.close()

# --- FUNKCJE PROJEKTÓW (Postgres) ---

def save_project(username, project_name, folder_path):
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            with conn.cursor() as c:
                # Sprawdź duplikat
                c.execute('SELECT id FROM projects WHERE folder_path = %s', (folder_path,))
                if not c.fetchone():
                    c.execute('INSERT INTO projects (username, project_name, folder_path) VALUES (%s, %s, %s)',
                              (username, project_name, folder_path))
    finally:
        conn.close()

def get_user_projects(username):
    conn = get_connection()
    if not conn: return []
    try:
        with conn:
            with conn.cursor() as c:
                # W Postgres nazwy kolumn zwracane są w krotce
                c.execute('SELECT project_name, folder_path, created_at FROM projects WHERE username = %s ORDER BY id DESC', (username,))
                projects = c.fetchall()
        return projects
    finally:
        conn.close()

# Inicjalizacja przy imporcie (stworzy tabele w chmurze przy pierwszym uruchomieniu)
if __name__ == "__main__":
    init_db() # Pozwala odpalić plik ręcznie, żeby stworzyć tabele
else:
    # W Streamlit wywołujemy to bezpiecznie, żeby nie blokować wątków
    pass
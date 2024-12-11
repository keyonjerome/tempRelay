import psycopg2
# Database connection parameters

DB_CONFIG = {
    'dbname': 'mydb',
    'user': 'me',
    'password': 'secret',
    'host': 'localhost',
}

def connexion(config:dict):
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(**config)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def close(conn):
    # fonction pour se déconnecter de la base de données
    conn.close()
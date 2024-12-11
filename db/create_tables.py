import psycopg2
import sys
sys.path.append('../')
import connexion

def read_sql_file(file_path):
    """Reads and returns the contents of a SQL file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    
def execute_statements(conn, statements):
    """Executes multiple SQL statements."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(statements)
            conn.commit()
            print("SQL executed successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error executing SQL statements: {e}Queries have been rolled back.")

def main():
    """Main function to create schema and insert data."""
    conn = connexion.connexion(connexion.DB_CONFIG)
    try:
        create_statements = read_sql_file('create_tables.sql')
        if create_statements is None:
            raise LookupError
        execute_statements(conn, create_statements)

        insert_statements = read_sql_file('insert_data.sql')
        if insert_statements is None:
            raise LookupError
        execute_statements(conn,insert_statements)

    finally:
        conn.close()

if __name__ == "__main__":
    main()

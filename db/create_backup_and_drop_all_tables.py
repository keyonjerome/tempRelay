import psycopg2
import subprocess
import os
from datetime import datetime
import sys
sys.path.append('../')

import connexion
# Database configuration dictionary
DB_CONFIG = connexion.DB_CONFIG


# Backup directory
backup_dir = '../backup/'  # Replace with the desired directory path
backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
backup_filepath = os.path.join(backup_dir, backup_filename)

# Function to create a database backup
def backup_database():
    try:
        print(f"Creating backup: {backup_filepath}")
        
        # Construct the pg_dump command
        dump_command = [
            'pg_dump',
            f'--dbname={DB_CONFIG["dbname"]}',
            f'--file={backup_filepath}',
            f'--username={DB_CONFIG["user"]}',
            f'--host={DB_CONFIG["host"]}'
        ]
        
        # Use PGPASSWORD for secure password handling
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_CONFIG['password']
        
        # Run the backup command
        subprocess.run(dump_command, check=True, env=env)
        print(f"Backup created successfully at {backup_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e}")
        exit(1)

# Function to drop all tables in the public schema
def drop_all_tables():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host']
        )
        cursor = conn.cursor()

        # Fetch all table names from the public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

        # Commit the changes
        conn.commit()
        print("All tables dropped successfully.")

    except psycopg2.Error as e:
        print(f"Error dropping tables: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def drop_all_tables_and_enums():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host']
        )
        cursor = conn.cursor()

        # Fetch all table names from the public schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

        # Fetch all enum types from the public schema
        cursor.execute("""
            SELECT n.nspname AS schema_name,
                   t.typname AS type_name
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname = 'public'
            GROUP BY schema_name, type_name;
        """)
        enums = cursor.fetchall()

        # Drop each enum type
        for enum in enums:
            schema_name, type_name = enum
            print(f"Dropping enum type: {type_name}")
            cursor.execute(f"DROP TYPE IF EXISTS {schema_name}.{type_name} CASCADE;")

        # Commit the changes
        conn.commit()
        print("All tables and enums dropped successfully.")

    except psycopg2.Error as e:
        print(f"Error dropping tables and enums: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Main script execution
if __name__ == "__main__":
    # Step 1: Create a backup
    backup_database()
    
    # Step 2: Drop all tables
    drop_all_tables_and_enums()

import psycopg2
import sys
sys.path.append("../")
import connexion

# Database connection dictionary (update these with your database credentials)
db_connection = connexion.DB_CONFIG

try:
    # Establish the database connection
    conn = psycopg2.connect(**db_connection)
    cursor = conn.cursor()

    # SQL query to add the column to the DataCapture table
    alter_table_query = """
    ALTER TABLE DataCapture
    ADD COLUMN packets INT,
    ADD column packet_loss INT;
    """

    # Execute the query
    cursor.execute(alter_table_query)
    conn.commit()
    print("Column added successfully.")

except psycopg2.Error as e:
    print(f"An error occurred: {e}")
    if conn:
        conn.rollback()

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()

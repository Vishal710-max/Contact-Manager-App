import mysql.connector
from mysql.connector import Error
import streamlit as st

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    #Local connection 
    """def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Change as per your MySQL setup
                password="system",  # Change as per your MySQL setup
                database="vishal",
                charset='utf8',  # Explicitly set charset
                use_unicode=True
            )
            if self.connection.is_connected():
                self.create_database()
                self.create_users_table()
        except Error as e:
            st.error(f"Error connecting to MySQL: {e}")"""
    #Global connection
    def get_database_connection():
    try:
        # Use Railway's environment variables
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            port=os.environ.get('DB_PORT', 5432)
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# In your app
conn = get_database_connection()
if conn:
    # Your database operations here
    
    def create_database(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS vishal")
            cursor.execute("USE vishal")
        except Error as e:
            st.error(f"Error creating database: {e}")
    
    def create_users_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Error as e:
            st.error(f"Error creating users table: {e}")
    
    def create_user_contacts_table(self, username):
        try:
            cursor = self.connection.cursor()
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    email VARCHAR(255),
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_phone (phone),
                    UNIQUE KEY unique_email (email)
                )
            """)
            return True
        except Error as e:
            st.error(f"Error creating contacts table: {e}")
            return False
    
    def get_connection(self):

        return self.connection

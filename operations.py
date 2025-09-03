from database import Database
from mysql.connector import Error

class ContactOperations:
    def __init__(self):
        self.db = Database()
        self.connection = self.db.get_connection()
    
    def register_user(self, username, password):
        try:
            cursor = self.connection.cursor()
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists"
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            self.connection.commit()
            
            # Create user's contacts table
            if self.db.create_user_contacts_table(username):
                return True, "User registered successfully"
            else:
                return False, "Error creating user contacts table"
        except Error as e:
            return False, f"Error registering user: {e}"
    
    def authenticate_user(self, username, password):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            return user is not None
        except Error as e:
            print(f"Error authenticating user: {e}")
            return False
    
    def get_contacts(self, username):
        try:
            cursor = self.connection.cursor(dictionary=True)
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY date_added DESC")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching contacts: {e}")
            return []
    
    def add_contact(self, username, name, phone, email):
        try:
            cursor = self.connection.cursor()
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
        
            # First check if phone number already exists
            cursor.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE phone = %s",
                (phone,)
            )
            phone_exists = cursor.fetchone()[0] > 0
        
            if phone_exists:
                return False, "Phone number already exists in your contacts"
        
            # Check if email exists (only if email is provided and not NULL)
            if email:  # email is not None and not empty string
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE email = %s AND email IS NOT NULL",
                    (email,)
                )
                email_exists = cursor.fetchone()[0] > 0
            
                if email_exists:
                    return False, "Email address already exists in your contacts"
        
                # If no duplicates found, insert the new contact
            cursor.execute(
                f"INSERT INTO {table_name} (name, phone, email) VALUES (%s, %s, %s)",
                (name, phone, email)
            )
            self.connection.commit()
            return True, "Contact added successfully"
        
        except Error as e:
            return False, f"Error adding contact: {e}"
    
    def update_contact(self, username, contact_id, name, phone, email):
        try:
            cursor = self.connection.cursor()
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
        
            # First, check if the phone number already exists (excluding current contact)
            cursor.execute(
                f"SELECT id FROM {table_name} WHERE phone = %s AND id != %s",
                (phone, contact_id)
                )
            if cursor.fetchone():
                return False, "Phone number already exists for another contact"
        
            # Check if the email already exists (excluding current contact)
            cursor.execute(
                f"SELECT id FROM {table_name} WHERE email = %s AND id != %s",
                (email, contact_id)
            )
            if cursor.fetchone():
                return False, "Email already exists for another contact"
        
            # If no duplicates found, proceed with the update
            cursor.execute(
                f"UPDATE {table_name} SET name = %s, phone = %s, email = %s WHERE id = %s",
                (name, phone, email, contact_id)
            )
            self.connection.commit()
            return True, "Contact updated successfully"
        
        except Error as e:
            return False, f"Error updating contact: {e}"
    
    def delete_contact(self, username, contact_id):
        try:
            cursor = self.connection.cursor()
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (contact_id,))
            self.connection.commit()
            return True, "Contact deleted successfully"
        except Error as e:
            return False, f"Error deleting contact: {e}"
    
    def search_contacts(self, username, search_term):
        try:
            cursor = self.connection.cursor(dictionary=True)
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
            query = f"""
                SELECT * FROM {table_name} 
                WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s 
                ORDER BY date_added DESC
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            return cursor.fetchall()
        except Error as e:
            print(f"Error searching contacts: {e}")
            return []
    
    def is_duplicate_contact(self, username, name, phone, email):
        """Check if a contact with the same name, phone, or email already exists"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            table_name = f"contacts_{username.replace(' ', '_').lower()}"
            
            # Check for duplicates
            query = f"""
                SELECT * FROM {table_name} 
                WHERE name = %s OR phone = %s OR email = %s
            """
            cursor.execute(query, (name, phone, email))
            duplicates = cursor.fetchall()
            
            return len(duplicates) > 0
        except Error as e:
            print(f"Error checking for duplicates: {e}")
            return False
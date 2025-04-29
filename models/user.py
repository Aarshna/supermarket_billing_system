import hashlib
import os

class User:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def authenticate(self, username, password):
        """Authenticate a user"""
        self.db_manager.connect()
        
        # Get user by username
        user = self.db_manager.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        
        if not user:
            self.db_manager.disconnect()
            return None
            
        # Check password
        hashed_password = self._hash_password(password, user['salt'])
        
        if hashed_password != user['password']:
            self.db_manager.disconnect()
            return None
            
        # Update last login
        self.db_manager.execute(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?",
            (user['id'],)
        )
        
        self.db_manager.commit()
        self.db_manager.disconnect()
        
        # Convert to dictionary before removing sensitive data
        user_dict = dict(user)
        
        # Remove sensitive data
        del user_dict['password']
        del user_dict['salt']
        
        return user_dict
        
    def get_all_users(self):
        """Get all users"""
        self.db_manager.connect()
        users = self.db_manager.fetch_all(
            "SELECT id, username, full_name, role, email, last_login, created_at FROM users"
        )
        self.db_manager.disconnect()
        return users
        
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        self.db_manager.connect()
        user = self.db_manager.fetch_one(
            "SELECT id, username, full_name, role, email, last_login, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        self.db_manager.disconnect()
        return user
        
    def add_user(self, username, password, full_name, role, email=None):
        """Add a new user"""
        try:
            self.db_manager.connect()
            
            # Check if username already exists
            existing = self.db_manager.fetch_one(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            )
            
            if existing:
                self.db_manager.disconnect()
                return False
                
            # Generate salt and hash password
            salt = os.urandom(32).hex()
            hashed_password = self._hash_password(password, salt)
            
            # Insert user
            self.db_manager.execute(
                """
                INSERT INTO users (username, password, salt, full_name, role, email, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (username, hashed_password, salt, full_name, role, email)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error adding user: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False
            
    def update_user(self, user_id, full_name, role, email=None):
        """Update user details (not password)"""
        try:
            self.db_manager.connect()
            
            self.db_manager.execute(
                """
                UPDATE users
                SET full_name = ?, role = ?, email = ?
                WHERE id = ?
                """,
                (full_name, role, email, user_id)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error updating user: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False
            
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        try:
            self.db_manager.connect()
            
            # Get user
            user = self.db_manager.fetch_one(
                "SELECT password, salt FROM users WHERE id = ?",
                (user_id,)
            )
            
            if not user:
                self.db_manager.disconnect()
                return False
                
            # Verify current password
            current_hashed = self._hash_password(current_password, user['salt'])
            
            if current_hashed != user['password']:
                self.db_manager.disconnect()
                return False
                
            # Generate new salt and hash new password
            new_salt = os.urandom(32).hex()
            new_hashed = self._hash_password(new_password, new_salt)
            
            # Update password
            self.db_manager.execute(
                """
                UPDATE users
                SET password = ?, salt = ?
                WHERE id = ?
                """,
                (new_hashed, new_salt, user_id)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error changing password: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False
            
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            self.db_manager.connect()
            
            # Check if user has created invoices
            invoices = self.db_manager.fetch_one(
                "SELECT COUNT(*) as count FROM invoices WHERE created_by = ?",
                (user_id,)
            )
            
            if invoices and invoices['count'] > 0:
                self.db_manager.disconnect()
                return False
                
            # Delete user
            self.db_manager.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False
            
    def _hash_password(self, password, salt):
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
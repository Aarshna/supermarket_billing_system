from models.user import User

class AuthController:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.user_model = User(db_manager)
        self.current_user = None
        
    def login(self, username, password):
        """
        Authenticate a user with username and password
        Returns user object if successful, None otherwise
        """
        user = self.user_model.authenticate(username, password)
        if user:
            self.current_user = user
            return user
        return None
        
    def logout(self):
        """Log out the current user"""
        self.current_user = None
        
    def get_current_user(self):
        """Get the currently logged in user"""
        return self.current_user
        
    def is_authenticated(self):
        """Check if a user is currently logged in"""
        return self.current_user is not None
        
    def is_admin(self):
        """Check if the current user is an admin"""
        if not self.current_user:
            return False
        return self.current_user['role'] == 'admin'
        
    def change_password(self, user_id, current_password, new_password):
        """
        Change a user's password
        Returns True if successful, False otherwise
        """
        # Verify current password first
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return False
            
        # Check if current password is correct
        if not self.user_model.verify_password(user['username'], current_password):
            return False
            
        # Update password
        return self.user_model.update_password(user_id, new_password)
        
    def create_user(self, username, password, full_name, role, email=None):
        """
        Create a new user
        Returns True if successful, False otherwise
        """
        if not self.is_admin():
            return False
            
        return self.user_model.create_user(username, password, full_name, role, email)
        
    def update_user(self, user_id, full_name, role, email=None):
        """
        Update a user's information
        Returns True if successful, False otherwise
        """
        if not self.is_admin():
            return False
            
        return self.user_model.update_user(user_id, full_name, role, email)
        
    def delete_user(self, user_id):
        """
        Delete a user
        Returns True if successful, False otherwise
        """
        if not self.is_admin():
            return False
            
        # Don't allow deleting the current user
        if self.current_user and self.current_user['id'] == user_id:
            return False
            
        return self.user_model.delete_user(user_id)
        
    def get_all_users(self):
        """
        Get all users
        Returns a list of user objects
        """
        if not self.is_admin():
            return []
            
        return self.user_model.get_all_users()

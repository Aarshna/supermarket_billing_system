 
import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User

class SettingsWindow:
    def __init__(self, root, db_manager, user, return_callback):
        self.root = root
        self.db_manager = db_manager
        self.user = user
        self.return_callback = return_callback
        self.user_model = User(db_manager)
        
        # Configure the window
        self.root.title("Supermarket Billing System - Settings")
        
        # Create main frame
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            self.frame, 
            text="Settings", 
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Create UI components
        self.create_ui()
        
    def create_ui(self):
        # Create notebook for different settings
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # User Profile Tab
        profile_frame = ttk.Frame(notebook, padding="10")
        notebook.add(profile_frame, text="User Profile")
        
        # User Management Tab (admin only)
        if self.user['role'] == 'admin':
            users_frame = ttk.Frame(notebook, padding="10")
            notebook.add(users_frame, text="User Management")
            self.create_user_management_ui(users_frame)
        
        # Create User Profile UI
        self.create_profile_ui(profile_frame)
        
        # Back button
        ttk.Button(self.frame, text="Back to Main Menu", command=self.return_callback).pack(side=tk.RIGHT, pady=10)
        
    def create_profile_ui(self, parent_frame):
        # User information
        info_frame = ttk.LabelFrame(parent_frame, text="User Information")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Username
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(info_frame, text=self.user['username']).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Full Name
        ttk.Label(info_frame, text="Full Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(info_frame, text=self.user['full_name']).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Role
        ttk.Label(info_frame, text="Role:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(info_frame, text=self.user['role']).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Email
        ttk.Label(info_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(info_frame, text=self.user['email'] if self.user['email'] else "").grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Last Login
        ttk.Label(info_frame, text="Last Login:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(info_frame, text=self.user['last_login'] if self.user['last_login'] else "").grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Change Password
        password_frame = ttk.LabelFrame(parent_frame, text="Change Password")
        password_frame.pack(fill=tk.X, pady=10)
        
        # Current Password
        ttk.Label(password_frame, text="Current Password:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        current_password_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=current_password_var, show="*").grid(row=0, column=1, padx=5, pady=5)
        
        # New Password
        ttk.Label(password_frame, text="New Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        new_password_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=new_password_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        # Confirm New Password
        ttk.Label(password_frame, text="Confirm New Password:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        confirm_password_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=confirm_password_var, show="*").grid(row=2, column=1, padx=5, pady=5)
        
        # Change Password Button
        def change_password():
            current_password = current_password_var.get()
            new_password = new_password_var.get()
            confirm_password = confirm_password_var.get()
            
            if not current_password or not new_password or not confirm_password:
                messagebox.showwarning("Warning", "All fields are required")
                return
                
            if new_password != confirm_password:
                messagebox.showwarning("Warning", "New passwords do not match")
                return
                
            if len(new_password) < 6:
                messagebox.showwarning("Warning", "New password must be at least 6 characters")
                return
                
            # Change password
            success = self.user_model.change_password(self.user['id'], current_password, new_password)
            
            if success:
                messagebox.showinfo("Success", "Password changed successfully")
                current_password_var.set("")
                new_password_var.set("")
                confirm_password_var.set("")
            else:
                messagebox.showerror("Error", "Failed to change password. Check your current password.")
                
        ttk.Button(password_frame, text="Change Password", command=change_password).grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)
        
    def create_user_management_ui(self, parent_frame):
        # Create user list frame
        list_frame = ttk.Frame(parent_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create user list
        ttk.Label(list_frame, text="Users:").pack(anchor=tk.W, pady=(0, 5))
        
        # Create treeview for users
        columns = ("ID", "Username", "Full Name", "Role", "Email")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        for col in columns:
            self.users_tree.heading(col, text=col)
            
        # Set column widths
        self.users_tree.column("ID", width=50)
        self.users_tree.column("Username", width=100)
        self.users_tree.column("Full Name", width=150)
        self.users_tree.column("Role", width=100)
        self.users_tree.column("Email", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load users
        self.load_users()
        
        # Create user form frame
        form_frame = ttk.LabelFrame(parent_frame, text="Add New User")
        form_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=username_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=password_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        # Full Name
        ttk.Label(form_frame, text="Full Name:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        full_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=full_name_var).grid(row=2, column=1, padx=5, pady=5)
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        role_var = tk.StringVar(value="cashier")
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, state="readonly")
        role_combo["values"] = ["admin", "manager", "cashier"]
        role_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=email_var).grid(row=4, column=1, padx=5, pady=5)
        
        # Add User Button
        def add_user():
            username = username_var.get().strip()
            password = password_var.get()
            full_name = full_name_var.get().strip()
            role = role_var.get()
            email = email_var.get().strip()
            
            if not username or not password or not full_name:
                messagebox.showwarning("Warning", "Username, password, and full name are required")
                return
                
            if len(password) < 6:
                messagebox.showwarning("Warning", "Password must be at least 6 characters")
                return
                
            # Add user
            success = self.user_model.add_user(username, password, full_name, role, email)
            
            if success:
                messagebox.showinfo("Success", "User added successfully")
                username_var.set("")
                password_var.set("")
                full_name_var.set("")
                role_var.set("cashier")
                email_var.set("")
                self.load_users()
            else:
                messagebox.showerror("Error", "Failed to add user. Username may already exist.")
                
        ttk.Button(form_frame, text="Add User", command=add_user).grid(row=5, column=1, padx=5, pady=10, sticky=tk.E)
        
        # Delete User Button
        def delete_user():
            selected = self.users_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a user to delete")
                return
                
            user_id = self.users_tree.item(selected[0])['values'][0]
            
            # Cannot delete yourself
            if user_id == self.user['id']:
                messagebox.showwarning("Warning", "You cannot delete your own account")
                return
                
            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
                return
                
            # Delete user
            success = self.user_model.delete_user(user_id)
            
            if success:
                messagebox.showinfo("Success", "User deleted successfully")
                self.load_users()
            else:
                messagebox.showerror("Error", "Failed to delete user. The user may have created invoices.")
                
        ttk.Button(form_frame, text="Delete Selected User", command=delete_user).grid(row=6, column=1, padx=5, pady=10, sticky=tk.E)
        
    def load_users(self):
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        # Get all users
        users = self.user_model.get_all_users()
        
        # Insert users into treeview
        for user in users:
            self.users_tree.insert("", tk.END, values=(
                user['id'],
                user['username'],
                user['full_name'],
                user['role'],
                user['email'] if user['email'] else ""
            ))

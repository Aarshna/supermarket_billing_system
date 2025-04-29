import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User

class LoginWindow:
    def __init__(self, root, db_manager, login_callback):
        self.root = root
        self.db_manager = db_manager
        self.login_callback = login_callback
        self.user_model = User(db_manager)
        
        # Configure the window
        self.root.title("Supermarket Billing System - Login")
        
        # Create main frame
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI components
        self.create_ui()
        
    def create_ui(self):
        # Center the login form
        main_frame = ttk.Frame(self.frame)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Supermarket Billing System", 
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var, width=30).grid(row=1, column=1, pady=5)
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, pady=5)
        
        # Login button
        ttk.Button(main_frame, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Version info
        ttk.Label(
            main_frame, 
            text="Version 1.0", 
            font=("Arial", 8)
        ).grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        # Authenticate user
        user = self.user_model.authenticate(username, password)
        
        if user:
            # Call the login callback with the user object
            self.login_callback(user)
        else:
            messagebox.showerror("Error", "Invalid username or password")

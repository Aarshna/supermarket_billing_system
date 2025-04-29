import tkinter as tk
from tkinter import ttk

class MainMenu:
    def __init__(self, root, user, billing_callback, inventory_callback, reports_callback, settings_callback, logout_callback):
        self.root = root
        self.user = user
        self.billing_callback = billing_callback
        self.inventory_callback = inventory_callback
        self.reports_callback = reports_callback
        self.settings_callback = settings_callback
        self.logout_callback = logout_callback
        
        # Configure the window
        self.root.title("Supermarket Billing System - Main Menu")
        
        # Create main frame
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI components
        self.create_ui()
        
    def create_ui(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text="Supermarket Billing System", 
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        # User info
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            user_frame, 
            text=f"Logged in as: {self.user['full_name']} ({self.user['role']})"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            user_frame, 
            text="Logout", 
            command=self.logout_callback
        ).pack(side=tk.LEFT)
        
        # Main menu buttons
        menu_frame = ttk.Frame(self.frame)
        menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Billing button
        billing_btn = ttk.Button(
            menu_frame, 
            text="Billing", 
            command=self.billing_callback,
            width=20
        )
        billing_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Inventory button
        inventory_btn = ttk.Button(
            menu_frame, 
            text="Inventory Management", 
            command=self.inventory_callback,
            width=20
        )
        inventory_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Reports button
        reports_btn = ttk.Button(
            menu_frame, 
            text="Reports", 
            command=self.reports_callback,
            width=20
        )
        reports_btn.grid(row=1, column=0, padx=10, pady=10)
        
        # Settings button
        settings_btn = ttk.Button(
            menu_frame, 
            text="Settings", 
            command=self.settings_callback,
            width=20
        )
        settings_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Disable settings for non-admin users
        if self.user['role'] != 'admin':
            settings_btn.state(['disabled'])
            
        # Footer
        footer_frame = ttk.Frame(self.frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        ttk.Label(
            footer_frame, 
            text="© 2023 Supermarket Billing System", 
            font=("Arial", 8)
        ).pack(side=tk.RIGHT)

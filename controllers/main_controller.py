import tkinter as tk
from views.login_window import LoginWindow
from views.main_menu import MainMenu
from views.billing_window import BillingWindow
from views.inventory_window import InventoryWindow
from views.reports_window import ReportsWindow
from views.settings_window import SettingsWindow

class MainController:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.current_user = None
        self.current_frame = None
        
        # Configure the root window
        self.root.title("Supermarket Billing System")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Start with login window
        self.show_login()
        
    def clear_window(self):
        # Destroy all widgets in the root window
        for widget in self.root.winfo_children():
            widget.destroy()
            
    def show_login(self):
        self.clear_window()
        self.current_frame = LoginWindow(self.root, self.db_manager, self.handle_login)
        
    def handle_login(self, user):
        self.current_user = user
        self.show_main_menu()
        
    def show_main_menu(self):
        self.clear_window()
        self.current_frame = MainMenu(
            self.root, 
            self.current_user,
            self.show_billing,
            self.show_inventory,
            self.show_reports,
            self.show_settings,
            self.handle_logout
        )
        
    def show_billing(self):
        self.clear_window()
        self.current_frame = BillingWindow(
            self.root,
            self.db_manager,
            self.current_user,
            self.show_main_menu
        )
        
    def show_inventory(self):
        self.clear_window()
        self.current_frame = InventoryWindow(
            self.root,
            self.db_manager,
            self.current_user,
            self.show_main_menu
        )
        
    def show_reports(self):
        self.clear_window()
        self.current_frame = ReportsWindow(
            self.root,
            self.db_manager,
            self.current_user,
            self.show_main_menu
        )
        
    def show_settings(self):
        self.clear_window()
        self.current_frame = SettingsWindow(
            self.root,
            self.db_manager,
            self.current_user,
            self.show_main_menu
        )
        
    def handle_logout(self):
        self.current_user = None
        self.show_login()

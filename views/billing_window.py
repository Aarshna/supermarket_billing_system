import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.product import Product
from models.invoice import Invoice
from models.customer import Customer
import datetime
from config import DEFAULT_TAX_RATE, CURRENCY_SYMBOL
from utils.pdf_generator import generate_receipt

class BillingWindow:
    def __init__(self, root, db_manager, user, return_callback):
        self.root = root
        self.db_manager = db_manager
        self.user = user
        self.return_callback = return_callback
        self.product_model = Product(db_manager)
        self.invoice_model = Invoice(db_manager)
        self.customer_model = Customer(db_manager)
        
        # Configure the window
        self.root.title("Supermarket Billing System - New Bill")
        
        # Create main frame
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            self.frame, 
            text="New Bill", 
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Create UI components
        self.create_ui()
        
        # Initialize cart and customer
        self.cart_items = []
        self.selected_customer = None
        self.discount_amount = 0.0
        
    def create_ui(self):
        # Create a frame for customer selection
        customer_frame = ttk.LabelFrame(self.frame, text="Customer Information")
        customer_frame.pack(fill=tk.X, pady=10)
        
        self.customer_name_var = tk.StringVar(value="Walk-in Customer")
        ttk.Label(customer_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(customer_frame, textvariable=self.customer_name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(customer_frame, text="Select Customer", command=self.select_customer).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(customer_frame, text="New Customer", command=self.add_customer).grid(row=0, column=3, padx=5, pady=5)
        
        # Create a frame for product search
        search_frame = ttk.LabelFrame(self.frame, text="Product Search")
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_entry.bind("<Return>", self.search_product)
        
        ttk.Button(search_frame, text="Search", command=self.search_product).grid(row=0, column=2, padx=5, pady=5)
        
        # Create a frame for the cart
        cart_frame = ttk.LabelFrame(self.frame, text="Shopping Cart")
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for cart items
        columns = ("ID", "Product", "Price", "Quantity", "Total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.cart_tree.heading(col, text=col)
        
        # Set column widths
        self.cart_tree.column("ID", width=50)
        self.cart_tree.column("Product", width=200)
        self.cart_tree.column("Price", width=100)
        self.cart_tree.column("Quantity", width=100)
        self.cart_tree.column("Total", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for cart actions
        cart_actions_frame = ttk.Frame(self.frame)
        cart_actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(cart_actions_frame, text="Remove Item", command=self.remove_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(cart_actions_frame, text="Change Quantity", command=self.change_quantity).pack(side=tk.LEFT, padx=5)
        ttk.Button(cart_actions_frame, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, padx=5)
        ttk.Button(cart_actions_frame, text="Apply Discount", command=self.apply_discount).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for totals
        totals_frame = ttk.LabelFrame(self.frame, text="Bill Summary")
        totals_frame.pack(fill=tk.X, pady=10)
        
        # Subtotal
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.subtotal_var = tk.StringVar(value=f"{CURRENCY_SYMBOL}0.00")
        ttk.Label(totals_frame, textvariable=self.subtotal_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Tax
        ttk.Label(totals_frame, text=f"Tax ({DEFAULT_TAX_RATE*100}%):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.tax_var = tk.StringVar(value=f"{CURRENCY_SYMBOL}0.00")
        ttk.Label(totals_frame, textvariable=self.tax_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Discount
        ttk.Label(totals_frame, text="Discount:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.discount_var = tk.StringVar(value=f"{CURRENCY_SYMBOL}0.00")
        ttk.Label(totals_frame, textvariable=self.discount_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Total
        ttk.Label(totals_frame, text="Total:", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.total_var = tk.StringVar(value=f"{CURRENCY_SYMBOL}0.00")
        ttk.Label(totals_frame, textvariable=self.total_var, font=("Arial", 10, "bold")).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Create a frame for payment
        payment_frame = ttk.Frame(self.frame)
        payment_frame.pack(fill=tk.X, pady=10)
        
        # Payment method
        ttk.Label(payment_frame, text="Payment Method:").pack(side=tk.LEFT, padx=5)
        self.payment_method_var = tk.StringVar(value="Cash")
        payment_method_combo = ttk.Combobox(payment_frame, textvariable=self.payment_method_var, width=15)
        payment_method_combo['values'] = ('Cash', 'Credit Card', 'Debit Card', 'Mobile Payment')
        payment_method_combo.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        ttk.Button(payment_frame, text="Complete Sale", command=self.complete_sale).pack(side=tk.RIGHT, padx=5)
        ttk.Button(payment_frame, text="Back to Main Menu", command=self.return_callback).pack(side=tk.RIGHT, padx=5)

    def search_product(self, event=None):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a product name")
            return
        
        # Search for products
        products = self.product_model.search_products(search_term)
    
        if not products:  # Check if products list is empty
            messagebox.showinfo("Info", "No products found")
            return
        
        # If we found exactly one product, use it directly
        if len(products) == 1:
            product = products[0]
        else:
            # Show selection dialog if multiple products found
            product = self._show_product_selection_dialog(products)
            if not product:  # User canceled selection
                return
            
        # Check if product is in stock
        if product['stock'] <= 0:
            messagebox.showwarning("Warning", "Product is out of stock")
            return
        
        # Ask for quantity
        quantity = simpledialog.askinteger(
            "Quantity", 
            f"Enter quantity for {product['name']}:", 
            minvalue=1, 
            maxvalue=product['stock']
        )
        if not quantity:
            return
        
        # Add to cart
        self.add_to_cart(product, quantity)
    
        # Clear search field
        self.search_var.set("")

    def _show_product_selection_dialog(self, products):
        """Show a dialog to select from multiple products"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Product")
        dialog.geometry("600x400")
        
        # Create treeview
        columns = ("ID", "Name", "Category", "Price", "Stock")
        tree = ttk.Treeview(dialog, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            
        # Set column widths
        tree.column("ID", width=50)
        tree.column("Name", width=200)
        tree.column("Category", width=150)
        tree.column("Price", width=80)
        tree.column("Stock", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Insert products
        for product in products:
            tree.insert("", tk.END, values=(
                product['id'],
                product['name'],
                product['category_name'] if product['category_name'] else "",
                f"${product['price']:.2f}",
                product['stock']
            ))
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        selected_product = None
        
        def on_select():
            nonlocal selected_product
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a product")
                return
                
            # Get the selected product
            item = tree.item(selection[0])
            product_id = item['values'][0]
            
            # Find the product in our list
            for product in products:
                if product['id'] == product_id:
                    selected_product = product
                    break
                    
            dialog.destroy()
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        dialog.wait_window()
        return selected_product
        
    def add_to_cart(self, product, quantity):
        # Check if product already in cart
        for i, item in enumerate(self.cart_items):
            if item['product_id'] == product['id']:
                # Update quantity
                new_quantity = item['quantity'] + quantity
                if new_quantity > product['stock']:
                    messagebox.showwarning("Warning", "Cannot add more than available stock")
                    return
                    
                self.cart_items[i]['quantity'] = new_quantity
                self.cart_items[i]['total_price'] = new_quantity * product['price']
                self.update_cart_display()
                return
                
        # Add new item to cart
        cart_item = {
            'product_id': product['id'],
            'product_name': product['name'],
            'unit_price': product['price'],
            'quantity': quantity,
            'total_price': quantity * product['price']
        }
        
        self.cart_items.append(cart_item)
        self.update_cart_display()
        
    def update_cart_display(self):
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        # Insert cart items
        for item in self.cart_items:
            self.cart_tree.insert("", tk.END, values=(
                item['product_id'],
                item['product_name'],
                f"{CURRENCY_SYMBOL}{item['unit_price']:.2f}",
                item['quantity'],
                f"{CURRENCY_SYMBOL}{item['total_price']:.2f}"
            ))
            
        # Update totals
        self.update_totals()
        
    def update_totals(self):
        subtotal = sum(item['total_price'] for item in self.cart_items)
        tax = subtotal * DEFAULT_TAX_RATE
        total = subtotal + tax - self.discount_amount
        
        self.subtotal_var.set(f"{CURRENCY_SYMBOL}{subtotal:.2f}")
        self.tax_var.set(f"{CURRENCY_SYMBOL}{tax:.2f}")
        self.discount_var.set(f"{CURRENCY_SYMBOL}{self.discount_amount:.2f}")
        self.total_var.set(f"{CURRENCY_SYMBOL}{total:.2f}")
        
    def remove_item(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
            
        # Get the selected item index
        item_id = self.cart_tree.item(selected[0])['values'][0]
        
        # Remove from cart
        self.cart_items = [item for item in self.cart_items if item['product_id'] != item_id]
        
        # Update display
        self.update_cart_display()
        
    def change_quantity(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to change quantity")
            return
            
        # Get the selected item
        item_id = self.cart_tree.item(selected[0])['values'][0]
        
        # Find the item in cart
        for i, item in enumerate(self.cart_items):
            if item['product_id'] == item_id:
                # Get product to check stock
                product = self.product_model.get_product_by_id(item_id)
                
                # Ask for new quantity
                new_quantity = simpledialog.askinteger(
                    "Quantity", 
                    f"Enter new quantity for {item['product_name']}:", 
                    minvalue=1, 
                    maxvalue=product['stock']
                )
                if not new_quantity:
                    return
                    
                # Update quantity
                self.cart_items[i]['quantity'] = new_quantity
                self.cart_items[i]['total_price'] = new_quantity * item['unit_price']
                self.update_cart_display()
                return
                
    def clear_cart(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the cart?"):
            self.cart_items = []
            self.discount_amount = 0.0
            self.update_cart_display()
            
    def apply_discount(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
            
        subtotal = sum(item['total_price'] for item in self.cart_items)
        
        # Ask for discount amount
        discount = simpledialog.askfloat(
            "Discount", 
            f"Enter discount amount (0-{subtotal}):", 
            minvalue=0, 
            maxvalue=subtotal
        )
        if discount is None:
            return
            
        self.discount_amount = discount
        self.update_totals()
        
    def select_customer(self):
        # This would open a customer selection dialog
        # For simplicity
        customers = self.customer_model.get_all_customers()
        
        if not customers:
            messagebox.showinfo("Info", "No customers found")
            return
            
        # Create a simple dialog to select customer
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Customer")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create a listbox with customers
        listbox = tk.Listbox(dialog, width=50, height=15)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(listbox, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate listbox
        for customer in customers:
            listbox.insert(tk.END, f"{customer['id']} - {customer['name']} ({customer['phone']})")
            
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_select():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a customer")
                return
                
            # Get customer ID from the selected item
            customer_id = int(listbox.get(selection[0]).split(' - ')[0])
            customer = self.customer_model.get_customer_by_id(customer_id)
            
            if customer:
                self.selected_customer = customer
                self.customer_name_var.set(f"{customer['name']} ({customer['phone']})")
                dialog.destroy()
                
        def on_cancel():
            dialog.destroy()
            
        ttk.Button(button_frame, text="Select", command=on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=5)
        
    def add_customer(self):
        # Create a dialog to add a new customer
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Customer")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=email_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Address
        ttk.Label(form_frame, text="Address:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        address_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=address_var, width=30).grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def on_save():
            name = name_var.get().strip()
            phone = phone_var.get().strip()
            email = email_var.get().strip()
            address = address_var.get().strip()
            
            if not name or not phone:
                messagebox.showwarning("Warning", "Name and phone are required")
                return
                
            # Add customer
            result = self.customer_model.add_customer(name, phone, email, address)
            
            if result:
                # Get the newly added customer
                customer = self.customer_model.get_customer_by_phone(phone)
                if customer:
                    self.selected_customer = customer
                    self.customer_name_var.set(f"{customer['name']} ({customer['phone']})")
                    messagebox.showinfo("Success", "Customer added successfully")
                    dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add customer")
                
        def on_cancel():
            dialog.destroy()
            
        ttk.Button(button_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
    def complete_sale(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
            
        # Calculate totals
        subtotal = sum(item['total_price'] for item in self.cart_items)
        tax = subtotal * DEFAULT_TAX_RATE
        total = subtotal + tax - self.discount_amount
        
        # Get payment method
        payment_method = self.payment_method_var.get()
        
        # Confirm sale
        if not messagebox.askyesno("Confirm Sale", f"Complete sale for {CURRENCY_SYMBOL}{total:.2f}?"):
            return
            
        # Create invoice
        customer_id = self.selected_customer['id'] if self.selected_customer else None
        
        success, invoice_id, invoice_number = self.invoice_model.create_invoice(
            customer_id=customer_id,
            items=self.cart_items,
            total_amount=subtotal,
            tax_amount=tax,
            discount_amount=self.discount_amount,
            final_amount=total,
            payment_method=payment_method,
            payment_status="Paid",
            created_by=self.user['id']
        )
        
        if success:
            messagebox.showinfo("Success", f"Sale completed successfully!\nInvoice: {invoice_number}")
            
            # Ask if user wants to print receipt
            if messagebox.askyesno("Print Receipt", "Do you want to print the receipt?"):
                # Generate receipt PDF
                generate_receipt(self.db_manager, invoice_id)
                
            # Clear cart and reset
            self.cart_items = []
            self.discount_amount = 0.0
            self.selected_customer = None
            self.customer_name_var.set("Walk-in Customer")
            self.update_cart_display()
        else:
            messagebox.showerror("Error", "Failed to complete sale")
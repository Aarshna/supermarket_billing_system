from tkinter import *
from tkinter import ttk, messagebox
import tkinter as tk
from models.product import Product
from models.category import Category

class InventoryWindow:
    def __init__(self, root, db_manager, user=None, callback=None):
        self.root = root
        self.db_manager = db_manager
        self.user = user
        self.callback = callback
        self.product_model = Product(db_manager)
        self.category_model = Category(db_manager)

        self.window = Toplevel(root)
        self.window.title("Inventory Management")
        self.window.geometry("1000x600")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.product_id = None
        self.search_var = StringVar()
        self.category_var = StringVar()
        self.name_var = StringVar()
        self.price_var = StringVar()
        self.cost_price_var = StringVar()  # Using cost_price consistently to match database field
        self.stock_var = StringVar()
        self.categories = []

        self.load_categories()
        self.create_left_frame()
        self.create_right_frame()
        self.load_products()

    def on_close(self):
        self.window.destroy()
        if self.callback:
            self.callback()

    def load_categories(self):
        try:
            self.categories = self.category_model.get_all_categories()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")
            self.categories = []

    def create_left_frame(self):
        left_frame = Frame(self.window, width=600, height=600)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)

        search_frame = Frame(left_frame, padx=10, pady=10)
        search_frame.pack(fill=X)

        Label(search_frame, text="Search Products:").pack(side=LEFT, padx=5)
        Entry(search_frame, textvariable=self.search_var, width=30).pack(side=LEFT, padx=5)
        Button(search_frame, text="Search", command=self.search_products).pack(side=LEFT, padx=5)
        Button(search_frame, text="Clear", command=self.clear_search).pack(side=LEFT, padx=5)

        list_frame = Frame(left_frame)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        columns = ("ID", "Name", "Category", "Price", "Cost", "Stock")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "ID" else 50)

        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)

    def create_right_frame(self):
        right_frame = Frame(self.window, width=400, height=600, padx=10, pady=10)
        right_frame.pack(side=RIGHT, fill=BOTH)

        self.main_frame = right_frame
        self.create_form()

        button_frame = Frame(right_frame)
        button_frame.pack(pady=10)
        Button(button_frame, text="New", command=self.clear_form).pack(side=LEFT, padx=5)
        Button(button_frame, text="Save", command=self.save_product).pack(side=LEFT, padx=5)
        Button(button_frame, text="Delete", command=self.delete_product).pack(side=LEFT, padx=5)

        if self.user:
            stock_frame = Frame(right_frame)
            stock_frame.pack(pady=10)
            Label(stock_frame, text="Quick Stock Adjustment:").pack(anchor=W)
            for row in [["+", 1], ["+5", 5], ["+10", 10], ["-", -1], ["-5", -5], ["-10", -10]]:
                Button(stock_frame, text=row[0], command=lambda a=row[1]: self.quick_adjust_stock(a)).pack(side=LEFT, padx=3)

    def create_form(self):
        form_frame = ttk.LabelFrame(self.main_frame, text="Product Details", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        row = 0
        ttk.Label(form_frame, text="Product Name:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        Entry(form_frame, textvariable=self.name_var).grid(row=row, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(form_frame, text="Category:").grid(row=row, column=2, padx=5, pady=5, sticky=tk.W)
        category_names = [category["name"] for category in self.categories]
        ttk.Combobox(form_frame, textvariable=self.category_var, values=category_names).grid(row=row, column=3, padx=5, pady=5, sticky=tk.EW)

        row += 1
        ttk.Label(form_frame, text="Description:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.description_text = Text(form_frame, height=3, width=30)
        self.description_text.grid(row=row, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        row += 1
        ttk.Label(form_frame, text="Price:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        Entry(form_frame, textvariable=self.price_var).grid(row=row, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(form_frame, text="Cost Price:").grid(row=row, column=2, padx=5, pady=5, sticky=tk.W)
        Entry(form_frame, textvariable=self.cost_price_var).grid(row=row, column=3, padx=5, pady=5, sticky=tk.EW)

        row += 1
        ttk.Label(form_frame, text="Stock:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        Entry(form_frame, textvariable=self.stock_var).grid(row=row, column=1, padx=5, pady=5, sticky=tk.EW)

        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

    def load_products(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            products = self.product_model.get_all_products()
            for product in products:
                self.tree.insert("", "end", values=(
                    product["id"],
                    product["name"],
                    product["category_name"],
                    f"${product['price']:.2f}",
                    f"${product['cost_price']:.2f}",
                    product["stock"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def search_products(self):
        try:
            term = self.search_var.get()
            if not term:
                self.load_products()
                return
            
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            products = self.product_model.search_products(term)
            for product in products:
                self.tree.insert("", "end", values=(
                    product["id"],
                    product["name"],
                    product["category_name"],
                    f"${product['price']:.2f}",
                    f"${product['cost_price']:.2f}",
                    product["stock"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error searching products: {str(e)}")

    def clear_search(self):
        self.search_var.set("")
        self.load_products()

    def on_product_select(self, event=None):
        try:
            selected = self.tree.selection()
            if not selected:
                return
            
            values = self.tree.item(selected[0], 'values')
            self.product_id = values[0]
            product = self.product_model.get_product_by_id(self.product_id)
            
            if not product:
                return
                
            self.name_var.set(product["name"])
            self.category_var.set(product["category_name"])
            self.price_var.set(f"{product['price']:.2f}")
            self.cost_price_var.set(f"{product['cost_price']:.2f}")
            self.stock_var.set(str(product["stock"]))
            self.description_text.delete(1.0, END)
            self.description_text.insert(END, product.get("description", ""))
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting product: {str(e)}")

    def clear_form(self):
        self.product_id = None
        self.name_var.set("")
        self.category_var.set("")
        self.price_var.set("")
        self.cost_price_var.set("")
        self.stock_var.set("")
        self.description_text.delete(1.0, END)

    def validate_product_data(self):
        name = self.name_var.get()
        category_name = self.category_var.get()
        price_str = self.price_var.get().replace("$", "")
        cost_price_str = self.cost_price_var.get().replace("$", "")
        stock_str = self.stock_var.get()
        
        if not name or not category_name or not price_str or not stock_str:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return None
            
        try:
            price = float(price_str)
            if price < 0:
                messagebox.showerror("Error", "Price must be a positive number.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number.")
            return None
            
        try:
            cost_price = float(cost_price_str) if cost_price_str else 0.0
            if cost_price < 0:
                messagebox.showerror("Error", "Cost price must be a positive number.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Cost price must be a valid number.")
            return None
            
        try:
            stock = int(stock_str)
            if stock < 0:
                messagebox.showerror("Error", "Stock cannot be negative.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Stock must be a valid integer.")
            return None
            
        category = self.product_model.get_category_by_name(category_name)
        if not category:
            messagebox.showerror("Error", "Invalid category.")
            return None
            
        description = self.description_text.get(1.0, END).strip()
        
        return {
            "name": name,
            "category_id": category["id"],
            "price": price,
            "cost_price": cost_price,
            "stock": stock,
            "description": description
        }

    def save_product(self):
        try:
            product_data = self.validate_product_data()
            if not product_data:
                return
                
            if self.product_id:
                result = self.product_model.update_product(
                    self.product_id, 
                    product_data["name"], 
                    product_data["description"], 
                    product_data["category_id"], 
                    product_data["price"], 
                    product_data["cost_price"], 
                    product_data["stock"]
                )
                if result:
                    messagebox.showinfo("Success", "Product updated successfully.")
                else:
                    messagebox.showerror("Error", "Failed to update product.")
            else:
                product_id = self.product_model.add_product(
                    product_data["name"], 
                    product_data["description"], 
                    product_data["category_id"], 
                    product_data["price"], 
                    product_data["cost_price"], 
                    product_data["stock"]
                )
                if product_id:
                    self.product_id = product_id
                    messagebox.showinfo("Success", "Product added successfully.")
                else:
                    messagebox.showerror("Error", "Failed to add product.")
                    
            self.load_products()
            
        except Exception as e:
            print(f"Error in save_product: {e}")
            messagebox.showerror("Unexpected Error", str(e))

    def delete_product(self):
        if not self.product_id:
            messagebox.showerror("Error", "No product selected.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?")
        if not confirm:
            return
            
        try:
            result, message = self.product_model.delete_product(self.product_id)
            if result:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_products()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")

    def quick_adjust_stock(self, amount):
        if not self.product_id:
            messagebox.showerror("Error", "No product selected.")
            return
            
        try:
            current_stock = int(self.stock_var.get())
            new_stock = max(0, current_stock + amount)
            
            if self.product_model.update_stock(
                self.product_id,
                new_stock,
                'quick_adjustment',
                f"Quick adjustment by {amount}",
                self.user["id"] if self.user else None
            ):
                self.stock_var.set(str(new_stock))
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to update stock.")
        except ValueError:
            messagebox.showerror("Error", "Current stock value is not a valid number.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Error adjusting stock: {str(e)}")
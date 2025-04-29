import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from models.product import Product
from models.invoice import Invoice
from utils.pdf_generator import generate_sales_report
import os

class ReportsWindow:
    def __init__(self, root, db_manager, user, return_callback):
        self.root = root
        self.db_manager = db_manager
        self.user = user
        self.return_callback = return_callback
        self.product_model = Product(db_manager)
        self.invoice_model = Invoice(db_manager)
        
        # Configure the window
        self.root.title("Supermarket Billing System - Reports")
        
        # Create main frame
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            self.frame, 
            text="Reports", 
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Create notebook for different reports
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.sales_frame = ttk.Frame(self.notebook, padding="10")
        self.inventory_frame = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.sales_frame, text="Sales Reports")
        self.notebook.add(self.inventory_frame, text="Inventory Reports")
        
        # Create UI components
        self.create_sales_report_ui()
        self.create_inventory_report_ui()
        
        # Back button
        ttk.Button(self.frame, text="Back to Main Menu", command=self.return_callback).pack(side=tk.RIGHT, pady=10)
        
    def create_sales_report_ui(self):
        # Date selection frame
        date_frame = ttk.LabelFrame(self.sales_frame, text="Select Date Range")
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # From date
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Create date entry fields
        self.from_year_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y"))
        self.from_month_var = tk.StringVar(value=datetime.datetime.now().strftime("%m"))
        self.from_day_var = tk.StringVar(value="01")
        
        from_year_combo = ttk.Combobox(date_frame, textvariable=self.from_year_var, width=6)
        from_year_combo['values'] = [str(year) for year in range(2020, datetime.datetime.now().year + 2)]
        from_year_combo.grid(row=0, column=1, padx=2, pady=5)
        
        from_month_combo = ttk.Combobox(date_frame, textvariable=self.from_month_var, width=4)
        from_month_combo['values'] = [f"{month:02d}" for month in range(1, 13)]
        from_month_combo.grid(row=0, column=2, padx=2, pady=5)
        
        from_day_combo = ttk.Combobox(date_frame, textvariable=self.from_day_var, width=4)
        from_day_combo['values'] = [f"{day:02d}" for day in range(1, 32)]
        from_day_combo.grid(row=0, column=3, padx=2, pady=5)
        
        # To date
        ttk.Label(date_frame, text="To:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.to_year_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y"))
        self.to_month_var = tk.StringVar(value=datetime.datetime.now().strftime("%m"))
        self.to_day_var = tk.StringVar(value=datetime.datetime.now().strftime("%d"))
        
        to_year_combo = ttk.Combobox(date_frame, textvariable=self.to_year_var, width=6)
        to_year_combo['values'] = [str(year) for year in range(2020, datetime.datetime.now().year + 2)]
        to_year_combo.grid(row=0, column=5, padx=2, pady=5)
        
        to_month_combo = ttk.Combobox(date_frame, textvariable=self.to_month_var, width=4)
        to_month_combo['values'] = [f"{month:02d}" for month in range(1, 13)]
        to_month_combo.grid(row=0, column=6, padx=2, pady=5)
        
        to_day_combo = ttk.Combobox(date_frame, textvariable=self.to_day_var, width=4)
        to_day_combo['values'] = [f"{day:02d}" for day in range(1, 32)]
        to_day_combo.grid(row=0, column=7, padx=2, pady=5)
        
        # Generate report button
        ttk.Button(date_frame, text="Generate Report", command=self.generate_sales_report).grid(row=0, column=8, padx=10, pady=5)
        
        # Sales report frame
        report_frame = ttk.LabelFrame(self.sales_frame, text="Sales Report")
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for sales
        columns = ("Invoice", "Date", "Customer", "Items", "Total", "Payment")
        self.sales_tree = ttk.Treeview(report_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.sales_tree.heading(col, text=col)
            
        # Set column widths
        self.sales_tree.column("Invoice", width=100)
        self.sales_tree.column("Date", width=150)
        self.sales_tree.column("Customer", width=150)
        self.sales_tree.column("Items", width=80)
        self.sales_tree.column("Total", width=100)
        self.sales_tree.column("Payment", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sales_tree.pack(fill=tk.BOTH, expand=True)
        
        # Summary frame
        summary_frame = ttk.Frame(self.sales_frame)
        summary_frame.pack(fill=tk.X, pady=10)
        
        # Summary labels
        ttk.Label(summary_frame, text="Total Sales:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.total_sales_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, textvariable=self.total_sales_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Total Invoices:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.total_invoices_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_invoices_var).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Average Sale:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.average_sale_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, textvariable=self.average_sale_var).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Export button
        ttk.Button(summary_frame, text="Export to PDF", command=self.export_sales_report).grid(row=0, column=6, padx=20, pady=5)
        
    def create_inventory_report_ui(self):
        # Inventory report frame
        report_frame = ttk.LabelFrame(self.inventory_frame, text="Inventory Status")
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for inventory
        columns = ("ID", "Name", "Category", "Price", "Cost", "Stock", "Value")
        self.inventory_tree = ttk.Treeview(report_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            
        # Set column widths
        self.inventory_tree.column("ID", width=50)
        self.inventory_tree.column("Name", width=200)
        self.inventory_tree.column("Category", width=100)
        self.inventory_tree.column("Price", width=80)
        self.inventory_tree.column("Cost", width=80)
        self.inventory_tree.column("Stock", width=80)
        self.inventory_tree.column("Value", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        
        # Filter frame
        filter_frame = ttk.Frame(self.inventory_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Filter options
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All Products", variable=self.filter_var, value="all", command=self.load_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Low Stock", variable=self.filter_var, value="low", command=self.load_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Out of Stock", variable=self.filter_var, value="out", command=self.load_inventory).pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        ttk.Button(filter_frame, text="Refresh", command=self.load_inventory).pack(side=tk.RIGHT, padx=5)
        
        # Summary frame
        summary_frame = ttk.Frame(self.inventory_frame)
        summary_frame.pack(fill=tk.X, pady=10)
        
        # Summary labels
        ttk.Label(summary_frame, text="Total Products:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.total_products_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_products_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Total Stock Value:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.total_value_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, textvariable=self.total_value_var).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Low Stock Items:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.low_stock_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.low_stock_var).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Load inventory data
        self.load_inventory()
        
    def generate_sales_report(self):
        try:
            # Get date range
            from_year = int(self.from_year_var.get())
            from_month = int(self.from_month_var.get())
            from_day = int(self.from_day_var.get())
            
            to_year = int(self.to_year_var.get())
            to_month = int(self.to_month_var.get())
            to_day = int(self.to_day_var.get())
            
            # Create date strings
            from_date = f"{from_year}-{from_month:02d}-{from_day:02d}"
            to_date = f"{to_year}-{to_month:02d}-{to_day:02d}"
            
            # Validate dates
            try:
                datetime.datetime.strptime(from_date, "%Y-%m-%d")
                datetime.datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid date format")
                return
                
            # Get sales data
            sales_data = self.invoice_model.get_sales_report(from_date, to_date)
            
            # Clear existing items
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
                
            # Insert sales data into treeview
            total_amount = 0
            for sale in sales_data:
                self.sales_tree.insert("", tk.END, values=(
                    sale["invoice_number"],
                    sale["created_at"],
                    sale["customer_name"] if sale["customer_name"] else "Walk-in Customer",
                    sale["item_count"],
                    f"${sale['final_amount']:.2f}",
                    sale["payment_method"]
                ))
                total_amount += sale["final_amount"]
                
            # Update summary
            self.total_sales_var.set(f"${total_amount:.2f}")
            self.total_invoices_var.set(str(len(sales_data)))
            
            if len(sales_data) > 0:
                average_sale = total_amount / len(sales_data)
                self.average_sale_var.set(f"${average_sale:.2f}")
            else:
                self.average_sale_var.set("$0.00")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating sales report: {str(e)}")
            
    def export_sales_report(self):
        try:
            # Get date range
            from_year = int(self.from_year_var.get())
            from_month = int(self.from_month_var.get())
            from_day = int(self.from_day_var.get())
            
            to_year = int(self.to_year_var.get())
            to_month = int(self.to_month_var.get())
            to_day = int(self.to_day_var.get())
            
            # Create date strings
            from_date = f"{from_year}-{from_month:02d}-{from_day:02d}"
            to_date = f"{to_year}-{to_month:02d}-{to_day:02d}"
            
            # Get sales data
            sales_data = self.invoice_model.get_sales_report(from_date, to_date)
            
            if not sales_data:
                messagebox.showinfo("Info", "No sales data to export")
                return
                
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialdir="reports",
                initialfile=f"sales_report_{from_date}_to_{to_date}.pdf"
            )
            
            if not file_path:
                return
                
            # Create reports directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Generate PDF report
            generate_sales_report(
                file_path,
                sales_data,
                from_date,
                to_date,
                self.total_sales_var.get(),
                self.total_invoices_var.get(),
                self.average_sale_var.get()
            )
            
            messagebox.showinfo("Success", f"Sales report exported to {file_path}")
            
            # Open the PDF file
            try:
                import platform
                import subprocess
                
                if platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', file_path))
                elif platform.system() == 'Windows':  # Windows
                    os.startfile(file_path)
                else:  # Linux
                    subprocess.call(('xdg-open', file_path))
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting sales report: {str(e)}")
            
    def load_inventory(self):
        try:
            # Get filter option
            filter_option = self.filter_var.get()
            
            # Get inventory data
            inventory_data = self.product_model.get_inventory_update()
            
            # Clear existing items
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
                
            # Insert inventory data into treeview
            total_value = 0
            low_stock_count = 0
            
            for product in inventory_data:
                # Determine Status
                stock = product['current_stock'] or 0
                reorder_level = product['reorder_level'] or 5

                if stock == 0:
                    status = "Out of Stock"
                elif stock < reorder_level:
                    status = "Low Stock"
                    low_stock_count += 1
                else:
                    status = "In Stock"
                
                # Apply Filters
                if filter_option == "low" and status != "Low Stock":
                    continue
                if filter_option == "out" and status != "Out of Stock":
                    continue

                self.inventory_tree.insert("", tk.END, values=(
                    product['name'],
                    product['category_name'] or "Uncategorized",
                    stock,
                    reorder_level,
                    status
                ))
            # Update summary
            self.total_products_var.set(str(len(inventory_data)))
            self.low_stock_var.set(str(low_stock_count))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading inventory report: {str(e)}")


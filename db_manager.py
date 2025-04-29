import sqlite3
import os
import hashlib
import datetime
import uuid

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.cursor = None
            self.connection.close()
            self.connection = None
            
    def execute(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return False
            
    def fetch_one(self, query, params=None):
        """Execute a query and fetch one result"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return None
            
    def fetch_all(self, query, params=None):
        """Execute a query and fetch all results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return []
            
    def commit(self):
        """Commit the current transaction"""
        if self.connection:
            self.connection.commit()
            
    def rollback(self):
        """Rollback the current transaction"""
        if self.connection:
            self.connection.rollback()
            
    def get_last_row_id(self):
        """Get the ID of the last inserted row"""
        return self.cursor.lastrowid
        
    def initialize_database(self):
        """Initialize the database with schema"""
        try:
            self.connect()
        
            # Read schema from file
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as f:
                schema_script = f.read()
            
            # Execute schema script
            self.connection.executescript(schema_script)
        
            # Create default admin user
            salt = os.urandom(32).hex()
            hashed_password = hashlib.sha256(('admin' + salt).encode()).hexdigest()
            self.execute("""
                INSERT INTO users (username, password, salt, full_name, role, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', hashed_password, salt, 'Administrator', 'admin', 'admin@example.com'))
        
            self.commit()
            print("Database initialized successfully")
            return True
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False
        finally:
            self.disconnect()

    # Product Management Functions
    def search_products(self, search_term, category_id=None):
        """Search products by name or description with optional category filter"""
        try:
            self.connect()
            query = """
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE (p.name LIKE ? OR p.description LIKE ?)
            """
            params = [f"%{search_term}%", f"%{search_term}%"]
            
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)
                
            return self.fetch_all(query, params)
        finally:
            self.disconnect()
            
    def get_product_by_id(self, product_id):
        """Get a product by its ID"""
        try:
            self.connect()
            return self.fetch_one(
                "SELECT * FROM products WHERE id = ?", 
                (product_id,)
            )
        finally:
            self.disconnect()
            
    def update_product(self, product_id, name, description, price, cost_price, 
                       category_id, stock, reorder_level):
        """Update a product's details"""
        try:
            self.connect()
            result = self.execute(
                """
                UPDATE products 
                SET name = ?, description = ?, price = ?, cost_price = ?,
                    category_id = ?, stock = ?, reorder_level = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, description, price, cost_price, category_id, 
                 stock, reorder_level, product_id)
            )
            self.commit()
            return result
        finally:
            self.disconnect()

    def add_product(self, name, description, price, cost_price, category_id, 
                   stock, reorder_level):
        """Add a new product"""
        try:
            self.connect()
            self.execute(
                """
                INSERT INTO products 
                (name, description, price, cost_price, category_id, stock, reorder_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, price, cost_price, category_id, stock, reorder_level)
            )
            product_id = self.get_last_row_id()
            
            # Log the initial inventory
            if stock > 0:
                self.execute(
                    """
                    INSERT INTO inventory_transactions
                    (product_id, quantity_change, transaction_type, notes, created_by)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (product_id, stock, 'purchase', 'Initial inventory', 1)  # Assuming admin ID is 1
                )
            
            self.commit()
            return product_id
        finally:
            self.disconnect()

    def delete_product(self, product_id):
        """Delete a product"""
        try:
            self.connect()
            result = self.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.commit()
            return result
        finally:
            self.disconnect()

    # Cart Management Functions
    def add_to_cart(self, session_id, product_id, quantity=1):
        """Add an item to the shopping cart"""
        try:
            self.connect()
            
            # Check if the product is already in the cart
            existing_item = self.fetch_one(
                "SELECT * FROM cart_items WHERE session_id = ? AND product_id = ?",
                (session_id, product_id)
            )
            
            if existing_item:
                # Update quantity if the product is already in the cart
                new_quantity = existing_item['quantity'] + quantity
                self.execute(
                    """
                    UPDATE cart_items 
                    SET quantity = ?
                    WHERE session_id = ? AND product_id = ?
                    """,
                    (new_quantity, session_id, product_id)
                )
            else:
                # Add new item to cart
                self.execute(
                    """
                    INSERT INTO cart_items (session_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    """,
                    (session_id, product_id, quantity)
                )
                
            self.commit()
            return True
        finally:
            self.disconnect()
            
    def update_cart_item(self, session_id, product_id, quantity):
        """Update the quantity of an item in the cart"""
        try:
            self.connect()
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                self.execute(
                    "DELETE FROM cart_items WHERE session_id = ? AND product_id = ?",
                    (session_id, product_id)
                )
            else:
                # Update quantity
                self.execute(
                    """
                    UPDATE cart_items 
                    SET quantity = ?
                    WHERE session_id = ? AND product_id = ?
                    """,
                    (quantity, session_id, product_id)
                )
                
            self.commit()
            return True
        finally:
            self.disconnect()
            
    def get_cart_items(self, session_id):
        """Get all items in a user's cart with product details"""
        try:
            self.connect()
            return self.fetch_all(
                """
                SELECT c.*, p.name, p.price, p.stock, 
                       (p.price * c.quantity) as total_price
                FROM cart_items c
                JOIN products p ON c.product_id = p.id
                WHERE c.session_id = ?
                """,
                (session_id,)
            )
        finally:
            self.disconnect()
            
    def clear_cart(self, session_id):
        """Remove all items from a user's cart"""
        try:
            self.connect()
            self.execute("DELETE FROM cart_items WHERE session_id = ?", (session_id,))
            self.commit()
            return True
        finally:
            self.disconnect()

    # Billing and Invoice Functions
    def create_invoice(self, session_id, customer_id, payment_method, created_by, tax_rate=0.1):
        """Create an invoice from cart items"""
        try:
            self.connect()
            
            # Get cart items
            cart_items = self.get_cart_items(session_id)
            if not cart_items:
                return None
                
            # Generate invoice number
            invoice_number = f"INV-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
            
            # Calculate totals
            total_amount = sum(item['total_price'] for item in cart_items)
            tax_amount = total_amount * tax_rate
            final_amount = total_amount + tax_amount
            
            # Create invoice
            self.execute(
                """
                INSERT INTO invoices 
                (invoice_number, customer_id, total_amount, tax_amount, 
                final_amount, payment_method, payment_status, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (invoice_number, customer_id, total_amount, tax_amount, 
                final_amount, payment_method, 'paid', created_by)
            )
            
            invoice_id = self.get_last_row_id()
            
            # Add invoice items
            for item in cart_items:
                product_id = item['product_id']
                quantity = item['quantity']
                unit_price = item['price']
                total_price = item['total_price']
                
                # Add invoice item
                self.execute(
                    """
                    INSERT INTO invoice_items 
                    (invoice_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (invoice_id, product_id, quantity, unit_price, total_price)
                )
                
                # Update product stock
                self.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product_id)
                )
                
                # Log inventory transaction
                self.execute(
                    """
                    INSERT INTO inventory_transactions
                    (product_id, quantity_change, transaction_type, reference_id, created_by)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (product_id, -quantity, 'sale', invoice_id, created_by)
                )
            
            # Clear the cart
            self.clear_cart(session_id)
            
            self.commit()
            return invoice_id
        finally:
            self.disconnect()
            
    def get_invoice(self, invoice_id):
        """Get invoice details with items"""
        try:
            self.connect()
            
            invoice = self.fetch_one(
                """
                SELECT i.*, c.name as customer_name, u.full_name as created_by_name
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                JOIN users u ON i.created_by = u.id
                WHERE i.id = ?
                """,
                (invoice_id,)
            )
            
            if not invoice:
                return None
                
            items = self.fetch_all(
                """
                SELECT ii.*, p.name as product_name
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
                """,
                (invoice_id,)
            )
            
            # Convert to dict for easier manipulation
            invoice_dict = dict(invoice)
            invoice_dict['items'] = [dict(item) for item in items]
            
            return invoice_dict
        finally:
            self.disconnect()

    # Reporting Functions
    def generate_sales_report(self, start_date, end_date, category_id=None):
        """Generate a sales report for a date range with optional category filter"""
        try:
            self.connect()
            
            query = """
                SELECT 
                    p.id, p.name, 
                    c.name as category_name,
                    SUM(ii.quantity) as total_quantity,
                    SUM(ii.total_price) as total_sales,
                    COUNT(DISTINCT i.id) as order_count
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                JOIN invoices i ON ii.invoice_id = i.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE i.created_at BETWEEN ? AND ?
            """
            
            params = [start_date, end_date]
            
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)
                
            query += """
                GROUP BY p.id
                ORDER BY total_sales DESC
            """
            
            return self.fetch_all(query, params)
        finally:
            self.disconnect()
            
    def generate_inventory_report(self, category_id=None, low_stock_only=False):
        """Generate an inventory report with optional category filter and low stock filter"""
        try:
            self.connect()
            
            query = """
                SELECT 
                    p.id, p.name, p.description,
                    c.name as category_name,
                    p.stock as current_stock,
                    p.reorder_level,
                    p.price, p.cost_price,
                    (p.price - p.cost_price) as profit_margin,
                    ((p.price - p.cost_price)/p.price * 100) as margin_percentage,
                    p.updated_at as last_updated
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE 1=1
            """
            
            params = []
            
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)
                
            if low_stock_only:
                query += " AND p.stock <= p.reorder_level"
                
            query += " ORDER BY p.stock ASC"
            
            return self.fetch_all(query, params)
        finally:
            self.disconnect()

    def get_daily_sales_summary(self, date):
        """Get daily sales summary for a specific date"""
        try:
            self.connect()
            
            # Format date as string for SQL comparison
            date_str = date.strftime('%Y-%m-%d')
            
            return self.fetch_one(
                """
                SELECT 
                    COUNT(*) as total_invoices,
                    SUM(total_amount) as total_sales,
                    SUM(tax_amount) as total_tax,
                    SUM(final_amount) as total_revenue,
                    AVG(final_amount) as average_sale
                FROM invoices
                WHERE DATE(created_at) = ?
                """,
                (date_str,)
            )
        finally:
            self.disconnect()
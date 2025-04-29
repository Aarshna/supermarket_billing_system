from db_manager import DatabaseManager
from datetime import datetime

class Product:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_products(self):
        """Get all products with stock from inventory"""
        self.db_manager.connect()
        products = self.db_manager.fetch_all("""
            SELECT p.*, c.name AS category_name, i.quantity AS stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            ORDER BY p.name
        """)
        self.db_manager.disconnect()
        return products

    def get_product_by_id(self, product_id):
        """Get a single product by ID"""
        self.db_manager.connect()
        product = self.db_manager.fetch_one("""
            SELECT p.*, c.name AS category_name, i.quantity AS stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.id = ?
        """, (product_id,))
        self.db_manager.disconnect()
        return product

    def search_products(self, search_term):
        """Search products by name"""
        self.db_manager.connect()
        products = self.db_manager.fetch_all("""
            SELECT p.*, c.name AS category_name, i.quantity AS stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.name LIKE ?
            ORDER BY p.name
        """, (f"%{search_term}%",))
        self.db_manager.disconnect()
        return products

    def add_product(self, name, description, category_id, price, cost_price, stock):
        """Add a new product with stock"""
        try:
            self.db_manager.connect()

            # Insert into products
            self.db_manager.execute("""
                INSERT INTO products (name, description, category_id, price, cost_price, reorder_level, updated_at)
                VALUES (?, ?, ?, ?, ?, 5, CURRENT_TIMESTAMP)
            """, (name, description, category_id, price, cost_price))

            product_id = self.db_manager.get_last_row_id()

            # Insert into inventory
            self.db_manager.execute("""
                INSERT INTO inventory (product_id, quantity)
                VALUES (?, ?)
            """, (product_id, stock))

            self.db_manager.commit()
            return product_id
        except Exception as e:
            print(f"Error adding product: {e}")
            self.db_manager.rollback()
            return False
        finally:
            self.db_manager.disconnect()

    def update_product(self, product_id, name, description, category_id, price, cost_price, stock):
        """Update a product and its stock"""
        try:
            self.db_manager.connect()

            # Update product details
            self.db_manager.execute("""
                UPDATE products
                SET name = ?, description = ?, category_id = ?, price = ?, cost_price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, description, category_id, price, cost_price, product_id))

            # Update stock in inventory
            self.db_manager.execute("""
                UPDATE inventory
                SET quantity = ?
                WHERE product_id = ?
            """, (stock, product_id))

            self.db_manager.commit()
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            self.db_manager.rollback()
            return False
        finally:
            self.db_manager.disconnect()
            
    def update_stock(self, product_id, stock, adjustment_type='adjustment', notes='Stock update', user_id=None):
        """Update only product stock with optional tracking"""
        try:
            self.db_manager.connect()
            
            # Get current stock
            current_stock = self.db_manager.fetch_one(
                "SELECT quantity FROM inventory WHERE product_id = ?", 
                (product_id,)
            )
            
            if current_stock:
                current_qty = current_stock['quantity']
            else:
                current_qty = 0
            
            # Update stock in inventory
            self.db_manager.execute("""
                UPDATE inventory
                SET quantity = ?
                WHERE product_id = ?
            """, (stock, product_id))
            
            # Log stock adjustment if we have a user_id
            if user_id is not None:
                # Check if stock_adjustments table exists
                table_exists = self.db_manager.fetch_one(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='stock_adjustments'"
                )
                
                if table_exists:
                    self.db_manager.execute("""
                        INSERT INTO stock_adjustments 
                        (product_id, previous_quantity, new_quantity, adjustment_type, notes, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (product_id, current_qty, stock, adjustment_type, notes, user_id))
            
            self.db_manager.commit()
            return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            self.db_manager.rollback()
            return False
        finally:
            self.db_manager.disconnect()

    def delete_product(self, product_id):
        """Delete a product"""
        try:
            self.db_manager.connect()

            # Check if product is used in invoices
            used_in_invoice = self.db_manager.fetch_one(
                "SELECT COUNT(*) as count FROM invoice_items WHERE product_id = ?",
                (product_id,)
            )

            if used_in_invoice and used_in_invoice['count'] > 0:
                self.db_manager.disconnect()
                return False, "Cannot delete product that has been sold."

            # Delete from inventory
            self.db_manager.execute("DELETE FROM inventory WHERE product_id = ?", (product_id,))

            # Delete from products
            self.db_manager.execute("DELETE FROM products WHERE id = ?", (product_id,))

            self.db_manager.commit()
            return True, "Product deleted successfully."
        except Exception as e:
            print(f"Error deleting product: {e}")
            self.db_manager.rollback()
            return False, "Error deleting product."
        finally:
            self.db_manager.disconnect()

    def get_category_by_name(self, category_name):
        """Get category by name (helper for Inventory window)"""
        self.db_manager.connect()
        category = self.db_manager.fetch_one(
            "SELECT * FROM categories WHERE name = ?", (category_name,)
        )
        self.db_manager.disconnect()
        return category
        
    # Add the missing inventory report method
    def get_inventory_report(self, category_id=None):
        """Get inventory report with optional category filter"""
        self.db_manager.connect()
        
        query = """
            SELECT p.id, p.name, p.description, p.price, p.cost_price, p.reorder_level,
                   c.name AS category_name, i.quantity AS stock,
                   (p.price - p.cost_price) AS profit_margin,
                   ((p.price - p.cost_price) / CASE WHEN p.cost_price = 0 THEN 1 ELSE p.cost_price END) * 100 AS profit_percentage,
                   (p.price * i.quantity) AS inventory_value
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
        """
        
        params = ()
        if category_id:
            query += " WHERE p.category_id = ?"
            params = (category_id,)
            
        query += " ORDER BY p.name"
        
        inventory_report = self.db_manager.fetch_all(query, params)
        self.db_manager.disconnect()
        return inventory_report
    
    def get_inventory_update(self): 
        """Get current inventory status with stock levels"""
        self.db_manager.connect() 
        query = """
            SELECT 
                p.id, 
                p.name, 
                p.reorder_level, 
                c.name as category_name,
                COALESCE(i.quantity, 0) as current_stock,
                i.quantity as current_stock, 
                i.last_updated 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            LEFT JOIN inventory i ON p.id = i.product_id 
            ORDER BY p.name
        """
        inventory_data = self.db_manager.fetch_all(query)
        self.db_manager.disconnect()
        return inventory_data
    
    def get_low_stock_products(self):
        """Get products with stock below reorder level"""
        self.db_manager.connect()
        query = """
            SELECT 
                p.id, 
                p.name, 
                p.reorder_level, 
                c.name AS category_name, 
                i.quantity AS current_stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE i.quantity < p.reorder_level
            ORDER BY p.name
        """
        low_stock = self.db_manager.fetch_all(query)
        self.db_manager.disconnect()
        return low_stock

    def get_out_of_stock_products(self):
        """Get products with zero stock"""
        self.db_manager.connect()
        query = """
            SELECT 
                p.id, 
                p.name, 
                p.reorder_level, 
                c.name AS category_name, 
                i.quantity AS current_stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE i.quantity = 0 OR i.quantity IS NULL
            ORDER BY p.name
        """
        out_of_stock = self.db_manager.fetch_all(query)
        self.db_manager.disconnect()
        return out_of_stock
        
    # Add the sales report generation method
    def generate_sales_report(self, start_date, end_date, category_id=None, product_id=None, customer_id=None, include_canceled=False):
        """Generate sales report with filters
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            category_id (int, optional): Filter by category ID
            product_id (int, optional): Filter by product ID
            customer_id (int, optional): Filter by customer ID
            include_canceled (bool, optional): Whether to include canceled invoices
            
        Returns:
            list: Sales report data
        """
        self.db_manager.connect()
        
        query = """
            SELECT 
                i.id AS invoice_id,
                i.invoice_date,
                c.name AS customer_name,
                p.id AS product_id,
                p.name AS product_name,
                cat.name AS category_name,
                ii.quantity,
                ii.unit_price,
                (ii.quantity * ii.unit_price) AS total_amount,
                ((ii.unit_price - p.cost_price) * ii.quantity) AS profit,
                i.status
            FROM invoices i
            JOIN invoice_items ii ON i.id = ii.invoice_id
            JOIN products p ON ii.product_id = p.id
            JOIN customers c ON i.customer_id = c.id
            LEFT JOIN categories cat ON p.category_id = cat.id
            WHERE i.invoice_date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        if not include_canceled:
            query += " AND i.status != 'canceled'"
            
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
            
        if product_id:
            query += " AND p.id = ?"
            params.append(product_id)
            
        if customer_id:
            query += " AND i.customer_id = ?"
            params.append(customer_id)
            
        query += " ORDER BY i.invoice_date DESC, p.name"
        
        sales_report = self.db_manager.fetch_all(query, tuple(params))
        self.db_manager.disconnect()
        return sales_report
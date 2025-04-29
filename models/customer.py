class Customer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def get_all_customers(self):
        """Get all customers from the database"""
        self.db_manager.connect()
        customers = self.db_manager.fetch_all(
            "SELECT * FROM customers ORDER BY name"
        )
        self.db_manager.disconnect()
        return customers
        
    def get_customer_by_id(self, customer_id):
        """Get a customer by ID"""
        self.db_manager.connect()
        customer = self.db_manager.fetch_one(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,)
        )
        self.db_manager.disconnect()
        return customer
        
    def get_customer_by_phone(self, phone):
        """Get a customer by phone number"""
        self.db_manager.connect()
        customer = self.db_manager.fetch_one(
            "SELECT * FROM customers WHERE phone = ?",
            (phone,)
        )
        self.db_manager.disconnect()
        return customer
        
    def add_customer(self, name, phone, email=None, address=None):
        """Add a new customer"""
        try:
            self.db_manager.connect()
            
            # Check if customer with this phone already exists
            existing = self.db_manager.fetch_one(
                "SELECT id FROM customers WHERE phone = ?",
                (phone,)
            )
            
            if existing:
                return False
                
            # Insert new customer
            self.db_manager.execute(
                """
                INSERT INTO customers (name, phone, email, address, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (name, phone, email, address)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error adding customer: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False
            
    def update_customer(self, customer_id, name, phone, email=None, address=None):
        """Update an existing customer"""
        try:
            self.db_manager.connect()
            
            # Check if another customer with this phone exists
            existing = self.db_manager.fetch_one(
                "SELECT id FROM customers WHERE phone = ? AND id != ?",
                (phone, customer_id)
            )
            
            if existing:
                return False
                
            # Update customer
            self.db_manager.execute(
                """
                UPDATE customers
                SET name = ?, phone = ?, email = ?, address = ?
                WHERE id = ?
                """,
                (name, phone, email, address, customer_id)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error updating customer: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False
            
    def delete_customer(self, customer_id):
        """Delete a customer"""
        try:
            self.db_manager.connect()
            
            # Check if customer has invoices
            invoices = self.db_manager.fetch_one(
                "SELECT COUNT(*) as count FROM invoices WHERE customer_id = ?",
                (customer_id,)
            )
            
            if invoices and invoices['count'] > 0:
                return False
                
            # Delete customer
            self.db_manager.execute(
                "DELETE FROM customers WHERE id = ?",
                (customer_id,)
            )
            
            self.db_manager.commit()
            self.db_manager.disconnect()
            return True
            
        except Exception as e:
            print(f"Error deleting customer: {e}")
            self.db_manager.rollback()
            self.db_manager.disconnect()
            return False

import datetime

class Invoice:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_invoice(self, customer_id, items, total_amount, tax_amount, discount_amount, final_amount, payment_method, payment_status, created_by):
        """Create a new invoice with its items"""
        try:
            self.db_manager.connect()

            today = datetime.datetime.now().strftime("%Y%m%d")

            last_invoice = self.db_manager.fetch_one(
                "SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
                (f"INV-{today}-%",)
            )

            if last_invoice:
                seq_num = int(last_invoice['invoice_number'].split('-')[-1]) + 1
            else:
                seq_num = 1

            invoice_number = f"INV-{today}-{seq_num:04d}"

            # Insert invoice
            self.db_manager.execute(
                """
                INSERT INTO invoices (
                    invoice_number, customer_id, total_amount, tax_amount, 
                    discount_amount, final_amount, payment_method, 
                    payment_status, created_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    invoice_number, customer_id, total_amount, tax_amount,
                    discount_amount, final_amount, payment_method,
                    payment_status, created_by
                )
            )

            invoice_id = self.db_manager.get_last_row_id()

            if not invoice_id:
                self.db_manager.rollback()
                return False, None, None

            # Insert invoice items
            for item in items:
                success = self.db_manager.execute(
                    """
                    INSERT INTO invoice_items (
                        invoice_id, product_id, quantity, unit_price, total_price
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_id, item['product_id'], item['quantity'],
                        item['unit_price'], item['total_price']
                    )
                )
                if not success:
                    self.db_manager.rollback()
                    return False, None, None

                # Update product stock
                self.db_manager.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity - ?
                    WHERE product_id = ?
                    """,
                    (item['quantity'], item['product_id'])
                )

            self.db_manager.commit()
            return True, invoice_id, invoice_number

        except Exception as e:
            print(f"Error creating invoice: {e}")
            self.db_manager.rollback()
            return False, None, None
        finally:
            self.db_manager.disconnect()

    def get_invoice_by_id(self, invoice_id):
        """Get invoice details by ID"""
        try:
            self.db_manager.connect()

            invoice = self.db_manager.fetch_one(
                """
                SELECT i.*, c.name as customer_name, c.phone as customer_phone,
                       u.username as created_by_user
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN users u ON i.created_by = u.id
                WHERE i.id = ?
                """,
                (invoice_id,)
            )

            if not invoice:
                return None
                
            # Convert SQLite row to dictionary
            invoice_dict = dict(invoice)

            items = self.db_manager.fetch_all(
                """
                SELECT ii.*, p.name as product_name
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
                """,
                (invoice_id,)
            )

            # Add items to the dictionary, not directly to the SQLite Row
            invoice_dict['items'] = items
            return invoice_dict

        except Exception as e:
            print(f"Error getting invoice: {e}")
            return None
        finally:
            self.db_manager.disconnect()

    def get_sales_report(self, from_date, to_date):
        """Get sales report for a date range"""
        try:
            self.db_manager.connect()
            return self.db_manager.fetch_all(
                """
                SELECT i.id, i.invoice_number, i.created_at, c.name as customer_name,
                       COUNT(ii.id) as item_count, i.final_amount, i.payment_method
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                JOIN invoice_items ii ON i.id = ii.invoice_id
                WHERE DATE(i.created_at) BETWEEN ? AND ?
                GROUP BY i.id
                ORDER BY i.created_at DESC
                """,
                (from_date, to_date)
            )
        except Exception as e:
            print(f"Error getting sales report: {e}")
            return []
        finally:
            self.db_manager.disconnect()

    def get_top_selling_products(self, from_date, to_date, limit=10):
        """Get top selling products for a date range"""
        try:
            self.db_manager.connect()
            return self.db_manager.fetch_all(
                """
                SELECT p.id, p.name, c.name as category_name,
                       SUM(ii.quantity) as total_quantity,
                       SUM(ii.total_price) as total_sales
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                LEFT JOIN categories c ON p.category_id = c.id
                JOIN invoices i ON ii.invoice_id = i.id
                WHERE DATE(i.created_at) BETWEEN ? AND ?
                GROUP BY p.id
                ORDER BY total_quantity DESC
                LIMIT ?
                """,
                (from_date, to_date, limit)
            )
        except Exception as e:
            print(f"Error getting top selling products: {e}")
            return []
        finally:
            self.db_manager.disconnect()

    def get_sales_by_category(self, from_date, to_date):
        """Get sales by category for a date range"""
        try:
            self.db_manager.connect()
            return self.db_manager.fetch_all(
                """
                SELECT c.name as category_name,
                       SUM(ii.quantity) as total_quantity,
                       SUM(ii.total_price) as total_sales
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                LEFT JOIN categories c ON p.category_id = c.id
                JOIN invoices i ON ii.invoice_id = i.id
                WHERE DATE(i.created_at) BETWEEN ? AND ?
                GROUP BY c.id
                ORDER BY total_sales DESC
                """,
                (from_date, to_date)
            )
        except Exception as e:
            print(f"Error getting sales by category: {e}")
            return []
        finally:
            self.db_manager.disconnect()

    def get_daily_sales(self, from_date, to_date):
        """Get daily sales for a date range"""
        try:
            self.db_manager.connect()
            return self.db_manager.fetch_all(
                """
                SELECT DATE(i.created_at) as date,
                       COUNT(i.id) as invoice_count,
                       SUM(i.final_amount) as total_sales
                FROM invoices i
                WHERE DATE(i.created_at) BETWEEN ? AND ?
                GROUP BY DATE(i.created_at)
                ORDER BY date
                """,
                (from_date, to_date)
            )
        except Exception as e:
            print(f"Error getting daily sales: {e}")
            return []
        finally:
            self.db_manager.disconnect()
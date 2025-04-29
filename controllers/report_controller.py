from models.product import Product
from models.invoice import Invoice
import datetime
import os
from utils.pdf_generator import generate_sales_report

class ReportController:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.product_model = Product(db_manager)
        self.invoice_model = Invoice(db_manager)
        
    def get_sales_report(self, from_date, to_date, category_id=None, product_id=None, 
                         customer_id=None, include_canceled=False):
        """Get sales report for a date range with optional filters"""
        return self.product_model.generate_sales_report(
            from_date, to_date, category_id, product_id, 
            customer_id, include_canceled
        )
        
    def get_sales_summary(self, from_date, to_date):
        """Get sales summary for a date range"""
        sales_data = self.invoice_model.get_sales_report(from_date, to_date)
        
        if not sales_data:
            return {
                'total_sales': 0,
                'total_invoices': 0,
                'average_sale': 0,
                'total_items': 0,
                'payment_methods': {}
            }
            
        # Calculate summary
        total_sales = sum(sale['final_amount'] for sale in sales_data)
        total_invoices = len(sales_data)
        average_sale = total_sales / total_invoices if total_invoices > 0 else 0
        total_items = sum(sale['item_count'] for sale in sales_data)
        
        # Count payment methods
        payment_methods = {}
        for sale in sales_data:
            method = sale['payment_method']
            if method in payment_methods:
                payment_methods[method] += 1
            else:
                payment_methods[method] = 1
                
        return {
            'total_sales': total_sales,
            'total_invoices': total_invoices,
            'average_sale': average_sale,
            'total_items': total_items,
            'payment_methods': payment_methods
        }
        
    def get_inventory_report(self, category_id=None):
        """Get inventory report with optional category filter"""
        return self.product_model.get_inventory_report(category_id)
        
    def get_inventory_summary(self):
        """Get inventory summary"""
        inventory_data = self.product_model.get_inventory_report()
        
        if not inventory_data:
            return {
                'total_products': 0,
                'total_value': 0,
                'low_stock_count': 0,
                'out_of_stock_count': 0
            }
            
        # Calculate summary
        total_products = len(inventory_data)
        total_value = 0
        low_stock_count = 0
        out_of_stock_count = 0
        
        for product in inventory_data:
            # Calculate stock value
            cost = product["cost_price"] if product["cost_price"] else product["price"]
            stock_value = cost * product["stock"]
            total_value += stock_value
            
            # Count low stock and out of stock items
            if product["stock"] == 0:
                out_of_stock_count += 1
            elif product["stock"] < 10:
                low_stock_count += 1
                
        return {
            'total_products': total_products,
            'total_value': total_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count
        }
        
    def export_sales_report_to_pdf(self, from_date, to_date, file_path):
        """Export sales report to PDF"""
        try:
            # Get sales data
            sales_data = self.invoice_model.get_sales_report(from_date, to_date)
            
            if not sales_data:
                return False
                
            # Get summary
            summary = self.get_sales_summary(from_date, to_date)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Fix parameter mismatch - we need to match what utils.pdf_generator.generate_sales_report expects
            generate_sales_report(
                file_path,                  # file_path
                sales_data,                 # sales_data
                from_date,                  # start_date 
                to_date                     # end_date
                # Removed the extra parameters that were causing the error
            )
            
            return True
        except Exception as e:
            print(f"Error exporting sales report: {e}")
            return False
            
    def get_top_selling_products(self, from_date, to_date, limit=10):
        """Get top selling products for a date range"""
        return self.invoice_model.get_top_selling_products(from_date, to_date, limit)
        
    def get_sales_by_category(self, from_date, to_date):
        """Get sales by category for a date range"""
        return self.invoice_model.get_sales_by_category(from_date, to_date)
        
    def get_daily_sales(self, from_date, to_date):
        """Get daily sales for a date range"""
        return self.invoice_model.get_daily_sales(from_date, to_date)
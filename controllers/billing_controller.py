from models.product import Product
from models.customer import Customer
from models.invoice import Invoice
import datetime
import os
from utils.pdf_generator import generate_receipt

class BillingController:
    def __init__(self, db_manager, auth_controller):
        self.db_manager = db_manager
        self.auth_controller = auth_controller
        self.product_model = Product(db_manager)
        self.customer_model = Customer(db_manager)
        self.invoice_model = Invoice(db_manager)
        
        # Current cart
        self.cart_items = []
        self.customer = None
        
    def search_product(self, search_term):
        """Search for a product by barcode or name"""
        if not search_term:
            return []
            
        # Try to find by exact barcode first
        product = self.product_model.get_product_by_barcode(search_term)
        if product:
            return [product]
            
        # Otherwise search by name or partial barcode
        return self.product_model.search_products(search_term)
        
    def add_to_cart(self, product_id, quantity=1):
        """Add a product to the cart"""
        if quantity <= 0:
            return False
            
        # Get product details
        product = self.product_model.get_product_by_id(product_id)
        if not product:
            return False
            
        # Check if product is in stock
        if product['stock'] < quantity:
            return False
            
        # Check if product is already in cart
        for item in self.cart_items:
            if item['id'] == product_id:
                # Update quantity
                item['quantity'] += quantity
                item['total'] = item['quantity'] * item['price']
                return True
                
        # Add new item to cart
        self.cart_items.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'total': product['price'] * quantity
        })
        
        return True
        
    def update_cart_item(self, product_id, quantity):
        """Update the quantity of an item in the cart"""
        if quantity <= 0:
            return self.remove_from_cart(product_id)
            
        # Get product details
        product = self.product_model.get_product_by_id(product_id)
        if not product:
            return False
            
        # Check if product is in stock
        if product['stock'] < quantity:
            return False
            
        # Update quantity
        for item in self.cart_items:
            if item['id'] == product_id:
                item['quantity'] = quantity
                item['total'] = quantity * item['price']
                return True
                
        return False
        
    def remove_from_cart(self, product_id):
        """Remove an item from the cart"""
        for i, item in enumerate(self.cart_items):
            if item['id'] == product_id:
                self.cart_items.pop(i)
                return True
                
        return False
        
    def clear_cart(self):
        """Clear the cart"""
        self.cart_items = []
        self.customer = None
        
    def get_cart_total(self):
        """Get the total amount of the cart"""
        return sum(item['total'] for item in self.cart_items)
        
    def get_cart_item_count(self):
        """Get the number of items in the cart"""
        return len(self.cart_items)
        
    def get_cart_items(self):
        """Get all items in the cart"""
        return self.cart_items
        
    def search_customer(self, phone):
        """Search for a customer by phone number"""
        if not phone:
            return None
            
        return self.customer_model.get_customer_by_phone(phone)
        
    def set_customer(self, customer):
        """Set the customer for the current transaction"""
        self.customer = customer
        
    def create_or_update_customer(self, name, phone, email=None, address=None):
        """Create a new customer or update an existing one"""
        if not name or not phone:
            return None
            
        # Check if customer exists
        customer = self.customer_model.get_customer_by_phone(phone)
        
        if customer:
            # Update existing customer
            success = self.customer_model.update_customer(
                customer['id'], name, phone, email, address
            )
            if success:
                customer = self.customer_model.get_customer_by_id(customer['id'])
                self.customer = customer
                return customer
            return None
        else:
            # Create new customer
            customer_id = self.customer_model.add_customer(name, phone, email, address)
            if customer_id:
                customer = self.customer_model.get_customer_by_id(customer_id)
                self.customer = customer
                return customer
            return None
            
    def create_invoice(self, payment_method, discount=0, notes=None):
        """Create a new invoice from the current cart"""
        if not self.cart_items:
            return None
    
        if not self.auth_controller.is_authenticated():
            return None
    
        # Calculate totals
        subtotal = self.get_cart_total()
        tax = subtotal * 0.1  # 10% tax
        final_amount = subtotal + tax - discount
    
        # Prepare invoice items
        invoice_items = [{
            'product_id': item['id'],
            'quantity': item['quantity'],
            'unit_price': item['price'],
            'total_price': item['total']
        } for item in self.cart_items]
    
        # Create invoice using the Invoice model
        success, invoice_id, invoice_number = self.invoice_model.create_invoice(
            customer_id=self.customer['id'] if self.customer else None,
            items=invoice_items,
            total_amount=subtotal,
            tax_amount=tax,
            discount_amount=discount,
            final_amount=final_amount,
            payment_method=payment_method,
            payment_status='paid',
            created_by=self.auth_controller.get_current_user()['id']
        )
    
        if not success:
            return None
    
        # Get the complete invoice
        invoice = self.invoice_model.get_invoice_by_id(invoice_id)
    
        # Generate receipt
        if invoice:
            self.generate_receipt(invoice)
            self.clear_cart()  # Clear the cart after successful invoice creation
    
        return invoice

        
    def generate_receipt(self, invoice):
        """Generate a PDF receipt for an invoice"""
        try:
            # Create receipts directory if it doesn't exist
            os.makedirs('receipts', exist_ok=True)
            
            # Generate receipt filename
            filename = f"receipts/receipt_{invoice['invoice_number']}.pdf"
            
            # Get invoice items
            items = self.invoice_model.get_invoice_items(invoice['id'])
            
            # Get customer details
            customer = None
            if invoice['customer_id']:
                customer = self.customer_model.get_customer_by_id(invoice['customer_id'])
                
            # Get cashier details
            cashier = self.auth_controller.user_model.get_user_by_id(invoice['user_id'])
            
            # Generate PDF
            generate_receipt(
                filename,
                invoice,
                items,
                customer,
                cashier['full_name'] if cashier else "Unknown"
            )
            
            return filename
        except Exception as e:
            print(f"Error generating receipt: {e}")
            return None

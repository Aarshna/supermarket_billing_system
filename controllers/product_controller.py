from models.product import Product
from models.category import Category

class ProductController:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.product_model = Product(db_manager)
        self.category_model = Category(db_manager)
        
    # Product methods
    def get_all_products(self):
        """Get all products"""
        return self.product_model.get_all_products()
        
    def get_product_by_id(self, product_id):
        """Get a product by ID"""
        return self.product_model.get_product_by_id(product_id)
        
    def search_products(self, search_term):
        """Search for products by name"""
        return self.product_model.search_products(search_term)
        
    def add_product(self, name, description, category_id, price, cost_price, stock, reorder_level=10):
        """Add a new product"""
        return self.product_model.add_product(
            name, description, category_id, price, cost_price, stock, reorder_level
        )
        
    def update_product(self, product_id, name, description, category_id, price, cost_price):
        """Update product details (without stock)"""
        return self.product_model.update_product(
            product_id, name, description, category_id, price, cost_price
        )
        
    def update_product_with_stock(self, product_id, name, description, category_id, price, cost_price, stock):
        """Update product details and stock"""
        # First update the product details
        result = self.product_model.update_product(
            product_id, name, description, category_id, price, cost_price
        )
        
        # Then update the stock separately
        if result:
            return self.product_model.update_stock(product_id, stock)
        return result
        
    def delete_product(self, product_id):
        """Delete a product"""
        return self.product_model.delete_product(product_id)
        
    def update_stock(self, product_id, quantity, transaction_type='adjustment', notes='Stock update', user_id=1):
        """Update product stock"""
        return self.product_model.update_stock(product_id, quantity, transaction_type, notes, user_id)
        
    def get_low_stock_products(self, threshold=10):
        """Get products with low stock"""
        return self.product_model.get_low_stock_products(threshold)
        
    def get_out_of_stock_products(self):
        """Get products that are out of stock"""
        return self.product_model.get_out_of_stock_products()
        
    # Category methods
    def get_all_categories(self):
        """Get all categories"""
        return self.category_model.get_all_categories()
        
    def get_all_categories_with_counts(self):
        """Get all categories with product counts"""
        return self.category_model.get_all_categories_with_counts()
        
    def get_category_by_id(self, category_id):
        """Get a category by ID"""
        return self.category_model.get_category_by_id(category_id)
        
    def get_category_by_name(self, name):
        """Get a category by name"""
        return self.category_model.get_category_by_name(name)
        
    def add_category(self, name, description=None):
        """Add a new category"""
        return self.category_model.add_category(name, description)
        
    def update_category(self, category_id, name, description=None):
        """Update an existing category"""
        return self.category_model.update_category(category_id, name, description)
        
    def delete_category(self, category_id):
        """Delete a category"""
        return self.category_model.delete_category(category_id)
        
    # Inventory report
    def get_inventory_report(self, filter_option="all"):
        """Get inventory report"""
        return self.product_model.get_inventory_report(filter_option)

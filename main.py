import tkinter as tk
import os
from db_manager import DatabaseManager
from controllers.main_controller import MainController

def initialize_default_data(db_manager):
    print("Checking for default data...")
    
    # Check if categories exist
    db_manager.connect()
    categories = db_manager.fetch_all("SELECT * FROM categories")
    
    # If no categories, create default ones
    if not categories:
        print("Adding default categories...")
        default_categories = ["Groceries", "Dairy", "Beverages", "Snacks", "Household", "Personal Care",
                              "Bakery", "Fruits", "Vegetables", "Meat", "Frozen Foods", "Canned Goods",
                              "Condiments", "Cereals", "Electronics", "Stationery"]
        for category in default_categories:
            db_manager.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category,)
            )
        db_manager.commit()

    # Check if products exist
    products = db_manager.fetch_all("SELECT * FROM products")
    
    # If no products, create default ones
    if not products:
        print("Adding default products...")
        # Get category IDs first
        categories = db_manager.fetch_all("SELECT id, name FROM categories")
        category_dict = {cat['name']: cat['id'] for cat in categories}
        
        # Extensive list of products with actual category IDs
        sample_products = [
            # Groceries
            ("Rice (5kg)", category_dict.get("Groceries", 1), 12.99, 50),
            ("Flour (2kg)", category_dict.get("Groceries", 1), 4.99, 60),
            ("Sugar (1kg)", category_dict.get("Groceries", 1), 2.49, 70),
            ("Salt (500g)", category_dict.get("Groceries", 1), 1.29, 80),
            ("Pepper (100g)", category_dict.get("Groceries", 1), 3.99, 40),
            ("Cooking Oil (1L)", category_dict.get("Groceries", 1), 5.99, 45),
            ("Pasta (500g)", category_dict.get("Groceries", 1), 1.99, 100),
            ("Instant Noodles", category_dict.get("Groceries", 1), 0.99, 150),
            
            # Dairy
            ("Milk (1L)", category_dict.get("Dairy", 1), 2.99, 100),
            ("Cheese (250g)", category_dict.get("Dairy", 1), 4.49, 50),
            ("Yogurt (500g)", category_dict.get("Dairy", 1), 3.49, 60),
            ("Butter (250g)", category_dict.get("Dairy", 1), 3.99, 40),
            ("Eggs (12)", category_dict.get("Dairy", 1), 2.99, 80),
            ("Ice Cream (1L)", category_dict.get("Dairy", 1), 5.99, 30),
            ("Cream Cheese (200g)", category_dict.get("Dairy", 1), 2.99, 40),
            ("Sour Cream (250ml)", category_dict.get("Dairy", 1), 1.99, 35),
            
            # Beverages
            ("Cola (2L)", category_dict.get("Beverages", 1), 1.99, 120),
            ("Orange Juice (1L)", category_dict.get("Beverages", 1), 2.49, 80),
            ("Apple Juice (1L)", category_dict.get("Beverages", 1), 2.49, 75),
            ("Coffee (200g)", category_dict.get("Beverages", 1), 7.99, 40),
            ("Tea (100 bags)", category_dict.get("Beverages", 1), 4.99, 50),
            ("Energy Drink (250ml)", category_dict.get("Beverages", 1), 1.99, 100),
            ("Bottled Water (1.5L)", category_dict.get("Beverages", 1), 0.99, 200),
            ("Sparkling Water (1L)", category_dict.get("Beverages", 1), 1.49, 80),
            
            # Snacks
            ("Potato Chips (200g)", category_dict.get("Snacks", 1), 2.99, 90),
            ("Chocolate Bar", category_dict.get("Snacks", 1), 1.49, 120),
            ("Cookies (300g)", category_dict.get("Snacks", 1), 3.49, 70),
            ("Popcorn (150g)", category_dict.get("Snacks", 1), 2.29, 60),
            ("Nuts (250g)", category_dict.get("Snacks", 1), 4.99, 40),
            ("Crackers (200g)", category_dict.get("Snacks", 1), 2.79, 65),
            ("Candy (100g)", category_dict.get("Snacks", 1), 1.99, 80),
            ("Gum (10 pieces)", category_dict.get("Snacks", 1), 0.99, 150),
            
            # Household
            ("Laundry Detergent (2L)", category_dict.get("Household", 1), 8.99, 40),
            ("Dish Soap (500ml)", category_dict.get("Household", 1), 2.99, 60),
            ("Toilet Paper (12 rolls)", category_dict.get("Household", 1), 7.99, 50),
            ("Paper Towels (6 rolls)", category_dict.get("Household", 1), 5.99, 55),
            ("Garbage Bags (30 bags)", category_dict.get("Household", 1), 4.99, 70),
            ("Light Bulbs (4 pack)", category_dict.get("Household", 1), 6.99, 30),
            ("Batteries (AA, 8 pack)", category_dict.get("Household", 1), 7.99, 40),
            ("Air Freshener", category_dict.get("Household", 1), 3.49, 45),
            
            # Personal Care
            ("Shampoo (400ml)", category_dict.get("Personal Care", 1), 4.99, 60),
            ("Conditioner (400ml)", category_dict.get("Personal Care", 1), 4.99, 55),
            ("Toothpaste (100ml)", category_dict.get("Personal Care", 1), 2.99, 80),
            ("Toothbrush", category_dict.get("Personal Care", 1), 1.99, 100),
            ("Shower Gel (250ml)", category_dict.get("Personal Care", 1), 3.49, 70),
            ("Deodorant", category_dict.get("Personal Care", 1), 3.99, 65),
            ("Hand Soap (250ml)", category_dict.get("Personal Care", 1), 2.49, 75),
            ("Facial Tissues (100)", category_dict.get("Personal Care", 1), 1.99, 90),
            
            # Bakery
            ("Bread (White)", category_dict.get("Bakery", 1), 1.99, 80),
            ("Bread (Whole Wheat)", category_dict.get("Bakery", 1), 2.49, 60),
            ("Bagels (6 pack)", category_dict.get("Bakery", 1), 3.99, 40),
            ("Muffins (4 pack)", category_dict.get("Bakery", 1), 4.99, 30),
            ("Croissants (3 pack)", category_dict.get("Bakery", 1), 3.99, 35),
            ("Donuts (6 pack)", category_dict.get("Bakery", 1), 5.99, 25),
            ("Cake (Chocolate)", category_dict.get("Bakery", 1), 14.99, 15),
            ("Pie (Apple)", category_dict.get("Bakery", 1), 12.99, 20),
            
            # Fruits
            ("Apples (1kg)", category_dict.get("Fruits", 1), 3.99, 60),
            ("Bananas (1kg)", category_dict.get("Fruits", 1), 1.99, 80),
            ("Oranges (1kg)", category_dict.get("Fruits", 1), 2.99, 70),
            ("Grapes (500g)", category_dict.get("Fruits", 1), 4.49, 40),
            ("Strawberries (250g)", category_dict.get("Fruits", 1), 3.99, 30),
            ("Blueberries (125g)", category_dict.get("Fruits", 1), 3.49, 25),
            ("Watermelon (whole)", category_dict.get("Fruits", 1), 5.99, 20),
            ("Pineapple", category_dict.get("Fruits", 1), 3.99, 25),
            
            # Vegetables
            ("Potatoes (2kg)", category_dict.get("Vegetables", 1), 4.99, 50),
            ("Onions (1kg)", category_dict.get("Vegetables", 1), 2.49, 60),
            ("Tomatoes (500g)", category_dict.get("Vegetables", 1), 2.99, 45),
            ("Lettuce", category_dict.get("Vegetables", 1), 1.99, 40),
            ("Carrots (500g)", category_dict.get("Vegetables", 1), 1.99, 55),
            ("Broccoli", category_dict.get("Vegetables", 1), 2.49, 35),
            ("Peppers (3 pack)", category_dict.get("Vegetables", 1), 3.99, 30),
            ("Cucumber", category_dict.get("Vegetables", 1), 1.49, 45),
            
            # Meat
            ("Chicken Breast (500g)", category_dict.get("Meat", 1), 7.99, 40),
            ("Ground Beef (500g)", category_dict.get("Meat", 1), 6.99, 45),
            ("Pork Chops (500g)", category_dict.get("Meat", 1), 8.99, 35),
            ("Bacon (250g)", category_dict.get("Meat", 1), 5.99, 50),
            ("Sausages (8 pack)", category_dict.get("Meat", 1), 4.99, 40),
            ("Fish Fillets (400g)", category_dict.get("Meat", 1), 9.99, 30),
            ("Shrimp (300g)", category_dict.get("Meat", 1), 12.99, 25),
            ("Deli Meat (200g)", category_dict.get("Meat", 1), 4.99, 40),
            
            # Frozen Foods
            ("Frozen Pizza", category_dict.get("Frozen Foods", 1), 5.99, 40),
            ("Frozen Vegetables (500g)", category_dict.get("Frozen Foods", 1), 2.99, 50),
            ("Ice Cream (2L)", category_dict.get("Frozen Foods", 1), 7.99, 30),
            ("Frozen Meals", category_dict.get("Frozen Foods", 1), 4.99, 45),
            ("Frozen Fries (1kg)", category_dict.get("Frozen Foods", 1), 3.99, 35),
            ("Frozen Fish Sticks (500g)", category_dict.get("Frozen Foods", 1), 6.99, 30),
            ("Frozen Berries (400g)", category_dict.get("Frozen Foods", 1), 5.99, 25),
            ("Frozen Desserts", category_dict.get("Frozen Foods", 1), 8.99, 20),
            
            # Canned Goods
            ("Canned Soup", category_dict.get("Canned Goods", 1), 1.99, 70),
            ("Canned Tuna", category_dict.get("Canned Goods", 1), 2.49, 65),
            ("Canned Beans", category_dict.get("Canned Goods", 1), 1.49, 80),
            ("Canned Corn", category_dict.get("Canned Goods", 1), 1.29, 75),
            ("Canned Tomatoes", category_dict.get("Canned Goods", 1), 1.79, 70),
            ("Canned Fruit", category_dict.get("Canned Goods", 1), 2.29, 60),
            ("Canned Vegetables", category_dict.get("Canned Goods", 1), 1.69, 65),
            ("Canned Meat", category_dict.get("Canned Goods", 1), 3.49, 50),
            
            # Condiments
            ("Ketchup (500ml)", category_dict.get("Condiments", 1), 2.99, 60),
            ("Mustard (250ml)", category_dict.get("Condiments", 1), 1.99, 55),
            ("Mayonnaise (400ml)", category_dict.get("Condiments", 1), 3.99, 50),
            ("Salsa (300ml)", category_dict.get("Condiments", 1), 3.49, 45),
            ("Soy Sauce (250ml)", category_dict.get("Condiments", 1), 2.79, 50),
            ("Hot Sauce (150ml)", category_dict.get("Condiments", 1), 2.49, 40),
            ("Honey (500g)", category_dict.get("Condiments", 1), 6.99, 35),
            ("Jam (300g)", category_dict.get("Condiments", 1), 3.99, 45),
            
            # Cereals
            ("Corn Flakes (500g)", category_dict.get("Cereals", 1), 3.99, 50),
            ("Oatmeal (1kg)", category_dict.get("Cereals", 1), 4.99, 45),
            ("Granola (500g)", category_dict.get("Cereals", 1), 5.99, 40),
            ("Chocolate Cereal (400g)", category_dict.get("Cereals", 1), 4.49, 35),
            ("Muesli (750g)", category_dict.get("Cereals", 1), 6.99, 30),
            ("Rice Krispies (400g)", category_dict.get("Cereals", 1), 3.99, 40),
            ("Bran Flakes (500g)", category_dict.get("Cereals", 1), 4.79, 35),
            ("Cereal Bars (8 pack)", category_dict.get("Cereals", 1), 3.99, 50),
            
            # Electronics
            ("Batteries (AAA, 8 pack)", category_dict.get("Electronics", 1), 7.99, 40),
            ("USB Cable", category_dict.get("Electronics", 1), 9.99, 30),
            ("Headphones", category_dict.get("Electronics", 1), 19.99, 20),
            ("Phone Charger", category_dict.get("Electronics", 1), 14.99, 25),
            ("Memory Card (32GB)", category_dict.get("Electronics", 1), 12.99, 15),
            ("Power Bank", category_dict.get("Electronics", 1), 24.99, 10),
            ("Mouse", category_dict.get("Electronics", 1), 14.99, 15),
            ("Keyboard", category_dict.get("Electronics", 1), 29.99, 10),
            
            # Stationery
            ("Pen (10 pack)", category_dict.get("Stationery", 1), 4.99, 60),
            ("Pencil (12 pack)", category_dict.get("Stationery", 1), 3.99, 55),
            ("Notebook", category_dict.get("Stationery", 1), 2.99, 50),
            ("Sticky Notes", category_dict.get("Stationery", 1), 1.99, 45),
            ("Scissors", category_dict.get("Stationery", 1), 3.99, 30),
            ("Tape", category_dict.get("Stationery", 1), 1.99, 40),
            ("Stapler", category_dict.get("Stationery", 1), 5.99, 25),
            ("Paper Clips (100)", category_dict.get("Stationery", 1), 1.49, 50)
        ]
        
        # Insert products and create initial stock transactions
        for product in sample_products:
            name, category_id, price, stock = product
            
            # Insert the product
            db_manager.execute(
                "INSERT INTO products (name, category_id, price, stock) VALUES (?, ?, ?, ?)",
                (name, category_id, price, stock)
            )
            
            # Get the last inserted product ID
            product_id = db_manager.fetch_one("SELECT last_insert_rowid() as id")['id']
            
            # Create an initial stock transaction
            db_manager.execute(
                "INSERT INTO stock_transactions (product_id, quantity, type, notes, user_id) VALUES (?, ?, ?, ?, ?)",
                (product_id, stock, 'initial', 'Initial stock', 1)  # Assuming admin user ID is 1
            )
            
        db_manager.commit()
        
        # Check if admin user exists
        admin_user = db_manager.fetch_one("SELECT * FROM users WHERE username = 'admin'")
        if not admin_user:
            print("Creating admin user...")
            # Create admin user with password 'admin'
            db_manager.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                ('admin', 'admin', 'Administrator', 'admin')
            )
            db_manager.commit()
    
    db_manager.disconnect()
    print("Default data initialization complete")

def main():
    # Create database directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create receipts directory if it doesn't exist
    os.makedirs('receipts', exist_ok=True)
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Initialize database
    db_path = os.path.join('data', 'supermarket.db')
    db_manager = DatabaseManager(db_path)
    
    # Initialize database schema if needed
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        db_manager.initialize_database()
        print("Database initialized successfully")
        
    # Initialize default data
    initialize_default_data(db_manager)
    
    # Create the main window
    root = tk.Tk()
    
    # Set application icon if available
    try:
        icon_path = os.path.join('assets', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    # Initialize the controller
    app = MainController(root, db_manager)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()


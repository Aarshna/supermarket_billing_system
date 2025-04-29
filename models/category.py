class Category:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def get_all_categories(self):
        """Get all categories"""
        try:
            self.db_manager.connect()
            query = """
                SELECT id, name, description
                FROM categories
                ORDER BY name
            """
            categories = self.db_manager.fetch_all(query)
            self.db_manager.disconnect()
            
            return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            self.db_manager.disconnect()
            return []
            
    def get_all_categories_with_counts(self):
        """Get all categories with product counts"""
        try:
            self.db_manager.connect()
            query = """
                SELECT c.id, c.name, c.description,
                       COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                GROUP BY c.id
                ORDER BY c.name
            """
            categories = self.db_manager.fetch_all(query)
            self.db_manager.disconnect()
            
            return categories
        except Exception as e:
            print(f"Error getting categories with counts: {e}")
            self.db_manager.disconnect()
            return []
            
    def get_category_by_id(self, category_id):
        """Get category by ID"""
        try:
            self.db_manager.connect()
            query = """
                SELECT id, name, description
                FROM categories
                WHERE id = ?
            """
            category = self.db_manager.fetch_one(query, (category_id,))
            self.db_manager.disconnect()
            
            return category
        except Exception as e:
            print(f"Error getting category by ID: {e}")
            self.db_manager.disconnect()
            return None
            
    def get_category_by_name(self, name):
        """Get category by name"""
        try:
            self.db_manager.connect()
            query = """
                SELECT id, name, description
                FROM categories
                WHERE name = ?
            """
            category = self.db_manager.fetch_one(query, (name,))
            self.db_manager.disconnect()
            
            return category
        except Exception as e:
            print(f"Error getting category by name: {e}")
            self.db_manager.disconnect()
            return None
            
    def add_category(self, name, description=None):
        """Add a new category"""
        try:
            self.db_manager.connect()
            
            # Check if category with same name already exists
            check_query = "SELECT id FROM categories WHERE name = ?"
            existing = self.db_manager.fetch_one(check_query, (name,))
            
            if existing:
                self.db_manager.disconnect()
                return False
                
            # Insert new category
            query = """
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """
            self.db_manager.execute(query, (name, description))
            self.db_manager.commit()
            self.db_manager.disconnect()
            
            return True
        except Exception as e:
            print(f"Error adding category: {e}")
            self.db_manager.disconnect()
            return False
            
    def update_category(self, category_id, name, description=None):
        """Update an existing category"""
        try:
            self.db_manager.connect()
            
            # Check if category with same name already exists (excluding this one)
            check_query = "SELECT id FROM categories WHERE name = ? AND id != ?"
            existing = self.db_manager.fetch_one(check_query, (name, category_id))
            
            if existing:
                self.db_manager.disconnect()
                return False
                
            # Update category
            query = """
                UPDATE categories
                SET name = ?, description = ?
                WHERE id = ?
            """
            self.db_manager.execute(query, (name, description, category_id))
            self.db_manager.commit()
            self.db_manager.disconnect()
            
            return True
        except Exception as e:
            print(f"Error updating category: {e}")
            self.db_manager.disconnect()
            return False
            
    def delete_category(self, category_id):
        """Delete a category"""
        try:
            self.db_manager.connect()
            
            # Check if category has products
            check_query = "SELECT COUNT(*) as count FROM products WHERE category_id = ?"
            result = self.db_manager.fetch_one(check_query, (category_id,))
            
            if result and result['count'] > 0:
                self.db_manager.disconnect()
                return False
                
            # Delete category
            query = "DELETE FROM categories WHERE id = ?"
            self.db_manager.execute(query, (category_id,))
            self.db_manager.commit()
            self.db_manager.disconnect()
            
            return True
        except Exception as e:
            print(f"Error deleting category: {e}")
            self.db_manager.disconnect()
            return False

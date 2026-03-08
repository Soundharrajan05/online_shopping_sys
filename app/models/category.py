"""Category model for product categorization"""

from app.database.db_universal import Database


class Category:
    """Category model for organizing products"""
    
    def __init__(self, category_id, category_name):
        """
        Initialize Category instance
        
        Args:
            category_id: Unique identifier for the category
            category_name: Name of the category
        """
        self.category_id = category_id
        self.category_name = category_name
    
    @staticmethod
    def create(category_name):
        """
        Create a new category
        
        Args:
            category_name: Name of the category to create
        
        Returns:
            Category instance if successful, None otherwise
        
        Raises:
            Exception: If database operation fails
        """
        query = "INSERT INTO categories (category_name) VALUES (%s)"
        try:
            category_id = Database.execute_query(query, (category_name,), fetch=False)
            return Category(category_id, category_name)
        except Exception as e:
            print(f"Error creating category: {e}")
            raise
    
    @staticmethod
    def get_all():
        """
        Retrieve all categories from the database
        
        Returns:
            List of Category instances
        """
        query = "SELECT category_id, category_name FROM categories ORDER BY category_name"
        try:
            results = Database.execute_query(query, fetch=True)
            return [Category(row[0], row[1]) for row in results]
        except Exception as e:
            print(f"Error retrieving categories: {e}")
            raise
    
    @staticmethod
    def exists(category_name):
        """
        Check if a category with the given name already exists
        
        Args:
            category_name: Name of the category to check
        
        Returns:
            True if category exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM categories WHERE category_name = %s"
        try:
            results = Database.execute_query(query, (category_name,), fetch=True)
            return results[0][0] > 0
        except Exception as e:
            print(f"Error checking category existence: {e}")
            raise
    
    def to_dict(self):
        """
        Convert Category instance to dictionary
        
        Returns:
            Dictionary representation of the category
        """
        return {
            'category_id': self.category_id,
            'category_name': self.category_name
        }

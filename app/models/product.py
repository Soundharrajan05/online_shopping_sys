"""Product model for managing products in the system"""

from app.database.db_universal import Database


class Product:
    """Product model for managing product catalog"""
    
    def __init__(self, product_id, product_name, description, price, 
                 stock_quantity, image_url, category_id):
        """
        Initialize Product instance
        
        Args:
            product_id: Unique identifier for the product
            product_name: Name of the product
            description: Product description
            price: Product price
            stock_quantity: Available stock quantity
            image_url: URL to product image
            category_id: Foreign key to categories table
        """
        self.product_id = product_id
        self.product_name = product_name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.image_url = image_url
        self.category_id = category_id
    
    @staticmethod
    def create(product_name, description, price, stock_quantity, image_url, category_id):
        """
        Create a new product
        
        Args:
            product_name: Name of the product
            description: Product description
            price: Product price
            stock_quantity: Initial stock quantity
            image_url: URL to product image
            category_id: Category ID for the product
        
        Returns:
            Product instance if successful
        
        Raises:
            Exception: If database operation fails
        """
        query = """
            INSERT INTO products 
            (product_name, description, price, stock_quantity, image_url, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            product_id = Database.execute_query(
                query, 
                (product_name, description, price, stock_quantity, image_url, category_id),
                fetch=False
            )
            return Product(product_id, product_name, description, price, 
                         stock_quantity, image_url, category_id)
        except Exception as e:
            print(f"Error creating product: {e}")
            raise
    
    @staticmethod
    def get_all(category_id=None, search_term=None):
        """
        Retrieve all products with optional filtering
        
        Args:
            category_id: Optional category ID to filter by
            search_term: Optional search term to filter product names
        
        Returns:
            List of Product instances
        """
        query = """
            SELECT product_id, product_name, description, price, 
                   stock_quantity, image_url, category_id
            FROM products
            WHERE 1=1
        """
        params = []
        
        if category_id is not None:
            query += " AND category_id = %s"
            params.append(category_id)
        
        if search_term:
            query += " AND product_name LIKE %s"
            params.append(f"%{search_term}%")
        
        query += " ORDER BY product_name"
        
        try:
            results = Database.execute_query(query, tuple(params) if params else None, fetch=True)
            return [Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) 
                   for row in results]
        except Exception as e:
            print(f"Error retrieving products: {e}")
            raise
    
    @staticmethod
    def get_by_id(product_id):
        """
        Retrieve a product by its ID
        
        Args:
            product_id: ID of the product to retrieve
        
        Returns:
            Product instance if found, None otherwise
        """
        query = """
            SELECT product_id, product_name, description, price, 
                   stock_quantity, image_url, category_id
            FROM products
            WHERE product_id = %s
        """
        try:
            results = Database.execute_query(query, (product_id,), fetch=True)
            if results:
                row = results[0]
                return Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            return None
        except Exception as e:
            print(f"Error retrieving product by ID: {e}")
            raise
    
    @staticmethod
    def update(product_id, product_name=None, description=None, price=None, 
               stock_quantity=None, image_url=None, category_id=None):
        """
        Update product fields
        
        Args:
            product_id: ID of the product to update
            product_name: New product name (optional)
            description: New description (optional)
            price: New price (optional)
            stock_quantity: New stock quantity (optional)
            image_url: New image URL (optional)
            category_id: New category ID (optional)
        
        Returns:
            Number of rows affected
        
        Raises:
            Exception: If database operation fails
        """
        # Build dynamic update query based on provided fields
        update_fields = []
        params = []
        
        if product_name is not None:
            update_fields.append("product_name = %s")
            params.append(product_name)
        
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        
        if price is not None:
            update_fields.append("price = %s")
            params.append(price)
        
        if stock_quantity is not None:
            update_fields.append("stock_quantity = %s")
            params.append(stock_quantity)
        
        if image_url is not None:
            update_fields.append("image_url = %s")
            params.append(image_url)
        
        if category_id is not None:
            update_fields.append("category_id = %s")
            params.append(category_id)
        
        if not update_fields:
            return 0  # No fields to update
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
        params.append(product_id)
        
        try:
            rows_affected = Database.execute_query(query, tuple(params), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error updating product: {e}")
            raise
    
    @staticmethod
    def delete(product_id):
        """
        Delete a product
        
        Args:
            product_id: ID of the product to delete
        
        Returns:
            Number of rows affected
        
        Raises:
            Exception: If database operation fails
        """
        query = "DELETE FROM products WHERE product_id = %s"
        try:
            rows_affected = Database.execute_query(query, (product_id,), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error deleting product: {e}")
            raise
    
    @staticmethod
    def reduce_stock(product_id, quantity):
        """
        Reduce stock quantity for a product
        
        Args:
            product_id: ID of the product
            quantity: Quantity to reduce by
        
        Returns:
            Number of rows affected
        
        Raises:
            Exception: If database operation fails or insufficient stock
        """
        query = """
            UPDATE products 
            SET stock_quantity = stock_quantity - %s 
            WHERE product_id = %s AND stock_quantity >= %s
        """
        try:
            rows_affected = Database.execute_query(
                query, 
                (quantity, product_id, quantity), 
                fetch=False
            )
            if rows_affected == 0:
                raise ValueError(f"Insufficient stock for product {product_id}")
            return rows_affected
        except Exception as e:
            print(f"Error reducing stock: {e}")
            raise
    
    def to_dict(self):
        """
        Convert Product instance to dictionary
        
        Returns:
            Dictionary representation of the product
        """
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'description': self.description,
            'price': float(self.price),
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'category_id': self.category_id
        }

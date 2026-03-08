"""Cart model for managing shopping cart operations"""

from app.database.db_universal import Database


class Cart:
    """Cart model for managing user shopping carts"""
    
    def __init__(self, cart_id, user_id, product_id, quantity):
        """
        Initialize Cart instance
        
        Args:
            cart_id: Unique identifier for the cart entry
            user_id: Foreign key to users table
            product_id: Foreign key to products table
            quantity: Quantity of the product in cart
        """
        self.cart_id = cart_id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
    
    @staticmethod
    def add_item(user_id, product_id, quantity):
        """
        Add or update cart item with stock validation
        
        Args:
            user_id: ID of the user
            product_id: ID of the product to add
            quantity: Quantity to add
        
        Returns:
            Cart ID of the added/updated item
        
        Raises:
            ValueError: If insufficient stock or invalid quantity
            Exception: If database operation fails
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check stock availability
        stock_query = "SELECT stock_quantity FROM products WHERE product_id = %s"
        stock_result = Database.execute_query(stock_query, (product_id,), fetch=True)
        
        if not stock_result:
            raise ValueError(f"Product {product_id} not found")
        
        available_stock = stock_result[0][0]
        
        # Check if item already in cart
        check_query = """
            SELECT cart_id, quantity 
            FROM cart 
            WHERE user_id = %s AND product_id = %s
        """
        existing = Database.execute_query(check_query, (user_id, product_id), fetch=True)
        
        if existing:
            # Update existing cart item
            cart_id = existing[0][0]
            current_quantity = existing[0][1]
            new_quantity = current_quantity + quantity
            
            if new_quantity > available_stock:
                raise ValueError(f"Insufficient stock. Available: {available_stock}, Requested: {new_quantity}")
            
            update_query = """
                UPDATE cart 
                SET quantity = %s 
                WHERE cart_id = %s
            """
            Database.execute_query(update_query, (new_quantity, cart_id), fetch=False)
            return cart_id
        else:
            # Insert new cart item
            if quantity > available_stock:
                raise ValueError(f"Insufficient stock. Available: {available_stock}, Requested: {quantity}")
            
            insert_query = """
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """
            cart_id = Database.execute_query(insert_query, (user_id, product_id, quantity), fetch=False)
            return cart_id
    
    @staticmethod
    def get_user_cart(user_id):
        """
        Query all cart items for user with product details
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of dictionaries containing cart and product information
        """
        query = """
            SELECT c.cart_id, c.user_id, c.product_id, c.quantity,
                   p.product_name, p.description, p.price, p.stock_quantity, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
            ORDER BY c.cart_id
        """
        try:
            results = Database.execute_query(query, (user_id,), fetch=True)
            cart_items = []
            for row in results:
                cart_items.append({
                    'cart_id': row[0],
                    'user_id': row[1],
                    'product_id': row[2],
                    'quantity': row[3],
                    'product_name': row[4],
                    'description': row[5],
                    'price': float(row[6]),
                    'stock_quantity': row[7],
                    'image_url': row[8],
                    'subtotal': float(row[6]) * row[3]
                })
            return cart_items
        except Exception as e:
            print(f"Error retrieving cart: {e}")
            raise
    
    @staticmethod
    def update_quantity(cart_id, quantity):
        """
        Update cart item quantity with stock validation
        
        Args:
            cart_id: ID of the cart item
            quantity: New quantity (0 to remove)
        
        Returns:
            Number of rows affected
        
        Raises:
            ValueError: If insufficient stock or invalid quantity
            Exception: If database operation fails
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if quantity == 0:
            # Remove item if quantity is 0
            return Cart.remove_item(cart_id)
        
        # Get product_id and check stock
        check_query = """
            SELECT c.product_id, p.stock_quantity
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.cart_id = %s
        """
        result = Database.execute_query(check_query, (cart_id,), fetch=True)
        
        if not result:
            raise ValueError(f"Cart item {cart_id} not found")
        
        product_id = result[0][0]
        available_stock = result[0][1]
        
        if quantity > available_stock:
            raise ValueError(f"Insufficient stock. Available: {available_stock}, Requested: {quantity}")
        
        update_query = """
            UPDATE cart 
            SET quantity = %s 
            WHERE cart_id = %s
        """
        try:
            rows_affected = Database.execute_query(update_query, (quantity, cart_id), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error updating cart quantity: {e}")
            raise
    
    @staticmethod
    def remove_item(cart_id):
        """
        Delete cart item
        
        Args:
            cart_id: ID of the cart item to remove
        
        Returns:
            Number of rows affected
        
        Raises:
            Exception: If database operation fails
        """
        query = "DELETE FROM cart WHERE cart_id = %s"
        try:
            rows_affected = Database.execute_query(query, (cart_id,), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error removing cart item: {e}")
            raise
    
    @staticmethod
    def clear_cart(user_id):
        """
        Delete all cart items for user
        
        Args:
            user_id: ID of the user
        
        Returns:
            Number of rows affected
        
        Raises:
            Exception: If database operation fails
        """
        query = "DELETE FROM cart WHERE user_id = %s"
        try:
            rows_affected = Database.execute_query(query, (user_id,), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error clearing cart: {e}")
            raise
    
    @staticmethod
    def calculate_total(user_id):
        """
        Calculate total amount for user's cart
        
        Args:
            user_id: ID of the user
        
        Returns:
            Total amount as float
        """
        query = """
            SELECT SUM(p.price * c.quantity) as total
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """
        try:
            result = Database.execute_query(query, (user_id,), fetch=True)
            if result and result[0][0] is not None:
                return float(result[0][0])
            return 0.0
        except Exception as e:
            print(f"Error calculating cart total: {e}")
            raise

"""Order and OrderItem models for managing orders in the system"""

from app.database.db_universal import Database


class Order:
    """Order model for managing customer orders"""
    
    def __init__(self, order_id, user_id, total_amount, order_date, order_status):
        """
        Initialize Order instance
        
        Args:
            order_id: Unique identifier for the order
            user_id: Foreign key to users table
            total_amount: Total amount for the order
            order_date: Timestamp when order was created
            order_status: Status of the order (Pending, Shipped, Delivered)
        """
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.order_date = order_date
        self.order_status = order_status
    
    @staticmethod
    def create(user_id, total_amount):
        """
        Create a new order with Pending status
        
        Args:
            user_id: ID of the user placing the order
            total_amount: Total amount for the order
        
        Returns:
            Order ID of the created order
        
        Raises:
            Exception: If database operation fails
        """
        query = """
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (%s, %s, 'Pending')
        """
        try:
            order_id = Database.execute_query(
                query,
                (user_id, total_amount),
                fetch=False
            )
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            raise
    
    @staticmethod
    def get_user_orders(user_id):
        """
        Query all orders for a specific user
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of Order instances ordered by date descending
        """
        query = """
            SELECT order_id, user_id, total_amount, order_date, order_status
            FROM orders
            WHERE user_id = %s
            ORDER BY order_date DESC
        """
        try:
            results = Database.execute_query(query, (user_id,), fetch=True)
            return [Order(row[0], row[1], row[2], row[3], row[4]) for row in results]
        except Exception as e:
            print(f"Error retrieving user orders: {e}")
            raise
    
    @staticmethod
    def get_all_orders():
        """
        Query all orders from all users (admin function)
        
        Returns:
            List of dictionaries containing order and user information
        """
        query = """
            SELECT o.order_id, o.user_id, o.total_amount, o.order_date, o.order_status,
                   u.name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            ORDER BY o.order_date DESC
        """
        try:
            results = Database.execute_query(query, None, fetch=True)
            orders = []
            for row in results:
                orders.append({
                    'order_id': row[0],
                    'user_id': row[1],
                    'total_amount': float(row[2]),
                    'order_date': row[3],
                    'order_status': row[4],
                    'user_name': row[5],
                    'user_email': row[6]
                })
            return orders
        except Exception as e:
            print(f"Error retrieving all orders: {e}")
            raise
    
    @staticmethod
    def get_by_id(order_id):
        """
        Query order by its ID
        
        Args:
            order_id: ID of the order to retrieve
        
        Returns:
            Order instance if found, None otherwise
        """
        query = """
            SELECT order_id, user_id, total_amount, order_date, order_status
            FROM orders
            WHERE order_id = %s
        """
        try:
            results = Database.execute_query(query, (order_id,), fetch=True)
            if results:
                row = results[0]
                return Order(row[0], row[1], row[2], row[3], row[4])
            return None
        except Exception as e:
            print(f"Error retrieving order by ID: {e}")
            raise
    
    @staticmethod
    def update_status(order_id, status):
        """
        Update order status
        
        Args:
            order_id: ID of the order to update
            status: New status ('Pending', 'Shipped', 'Delivered')
        
        Returns:
            Number of rows affected
        
        Raises:
            ValueError: If status is invalid
            Exception: If database operation fails
        """
        valid_statuses = ['Pending', 'Shipped', 'Delivered']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        query = """
            UPDATE orders
            SET order_status = %s
            WHERE order_id = %s
        """
        try:
            rows_affected = Database.execute_query(query, (status, order_id), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error updating order status: {e}")
            raise
    
    def to_dict(self):
        """
        Convert Order instance to dictionary
        
        Returns:
            Dictionary representation of the order
        """
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'order_date': self.order_date,
            'order_status': self.order_status
        }


class OrderItem:
    """OrderItem model for managing items within orders"""
    
    def __init__(self, order_item_id, order_id, product_id, quantity, price):
        """
        Initialize OrderItem instance
        
        Args:
            order_item_id: Unique identifier for the order item
            order_id: Foreign key to orders table
            product_id: Foreign key to products table
            quantity: Quantity of the product ordered
            price: Price at time of order
        """
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    @staticmethod
    def create(order_id, product_id, quantity, price):
        """
        Create a new order item
        
        Args:
            order_id: ID of the order
            product_id: ID of the product
            quantity: Quantity ordered
            price: Price at time of order
        
        Returns:
            Order item ID of the created item
        
        Raises:
            Exception: If database operation fails
        """
        query = """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """
        try:
            order_item_id = Database.execute_query(
                query,
                (order_id, product_id, quantity, price),
                fetch=False
            )
            return order_item_id
        except Exception as e:
            print(f"Error creating order item: {e}")
            raise
    
    @staticmethod
    def get_order_items(order_id):
        """
        Query all items for an order with product details
        
        Args:
            order_id: ID of the order
        
        Returns:
            List of dictionaries containing order item and product information
        """
        query = """
            SELECT oi.order_item_id, oi.order_id, oi.product_id, oi.quantity, oi.price,
                   p.product_name, p.description, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
            ORDER BY oi.order_item_id
        """
        try:
            results = Database.execute_query(query, (order_id,), fetch=True)
            order_items = []
            for row in results:
                order_items.append({
                    'order_item_id': row[0],
                    'order_id': row[1],
                    'product_id': row[2],
                    'quantity': row[3],
                    'price': float(row[4]),
                    'product_name': row[5],
                    'description': row[6],
                    'image_url': row[7],
                    'subtotal': float(row[4]) * row[3]
                })
            return order_items
        except Exception as e:
            print(f"Error retrieving order items: {e}")
            raise
    
    def to_dict(self):
        """
        Convert OrderItem instance to dictionary
        
        Returns:
            Dictionary representation of the order item
        """
        return {
            'order_item_id': self.order_item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': float(self.price)
        }

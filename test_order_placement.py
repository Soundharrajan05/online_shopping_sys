"""
Test script to debug order placement issue
"""
import sys
from app.database.db_universal import Database
from config import config

# Initialize database
db_config = config['development']
Database.init_db({
    'DB_HOST': db_config.DB_HOST,
    'DB_USER': db_config.DB_USER,
    'DB_PASSWORD': db_config.DB_PASSWORD,
    'DB_NAME': db_config.DB_NAME,
    'DB_POOL_SIZE': db_config.DB_POOL_SIZE
})

print("Testing order placement...")

# Test user_id (assuming customer@test.com has user_id = 2)
user_id = 2

try:
    connection = Database.get_connection()
    cursor = connection.cursor()
    
    # Check if user has items in cart
    cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
    cart_count = cursor.fetchone()[0]
    print(f"Cart items for user {user_id}: {cart_count}")
    
    if cart_count == 0:
        print("Cart is empty. Add items to cart first.")
        sys.exit(0)
    
    # Get cart items
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.price, p.stock_quantity, p.product_name
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()
    
    print("\nCart items:")
    for product_id, quantity, price, stock, name in cart_items:
        print(f"  - {name}: Qty={quantity}, Price=${price}, Stock={stock}")
    
    # Check stock
    for product_id, quantity, price, stock_quantity, product_name in cart_items:
        if stock_quantity < quantity:
            print(f"\nERROR: Insufficient stock for {product_name}")
            print(f"  Available: {stock_quantity}, Requested: {quantity}")
            cursor.close()
            connection.close()
            sys.exit(1)
    
    # Calculate total
    total_amount = sum(quantity * float(price) for _, quantity, price, _, _ in cart_items)
    print(f"\nTotal amount: ${total_amount:.2f}")
    
    # Try to create order
    print("\nAttempting to create order...")
    cursor.execute("""
        INSERT INTO orders (user_id, total_amount, order_status)
        VALUES (%s, %s, 'Pending')
    """, (user_id, total_amount))
    order_id = cursor.lastrowid
    print(f"Order created with ID: {order_id}")
    
    # Create order items
    print("Creating order items...")
    for product_id, quantity, price, _, _ in cart_items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, product_id, quantity, price))
    print("Order items created")
    
    # Update stock
    print("Updating stock...")
    for product_id, quantity, _, _, _ in cart_items:
        cursor.execute("""
            UPDATE products
            SET stock_quantity = stock_quantity - %s
            WHERE product_id = %s AND stock_quantity >= %s
        """, (quantity, product_id, quantity))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Insufficient stock for product {product_id}")
    print("Stock updated")
    
    # Clear cart
    print("Clearing cart...")
    cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    print("Cart cleared")
    
    # Commit
    connection.commit()
    print("\n✓ Order placed successfully!")
    print(f"Order ID: {order_id}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
    if 'connection' in locals() and connection:
        connection.rollback()
        if 'cursor' in locals() and cursor:
            cursor.close()
        connection.close()

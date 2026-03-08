"""
Comprehensive input validation and sanitization functions

This module provides validation and sanitization for all user inputs
to prevent SQL injection, XSS, and other security vulnerabilities.

Validates: Requirements 11.1
"""

import re
import html
from decimal import Decimal, InvalidOperation


def sanitize_string(value, max_length=None):
    """
    Sanitize string input to prevent XSS attacks
    
    Args:
        value: String to sanitize
        max_length: Optional maximum length
    
    Returns:
        Sanitized string
    """
    if value is None:
        return ""
    
    # Convert to string and strip whitespace
    value = str(value).strip()
    
    # HTML escape to prevent XSS
    value = html.escape(value)
    
    # Truncate if max_length specified
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email string to validate
    
    Returns:
        Tuple (is_valid, sanitized_email, error_message)
    """
    if not email:
        return False, "", "Email is required"
    
    # Sanitize
    email = sanitize_string(email, max_length=100)
    
    # Validate format
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, email, "Invalid email format"
    
    return True, email, ""


def validate_password(password):
    """
    Validate password strength
    
    Args:
        password: Password string to validate
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 100:
        return False, "Password must be less than 100 characters"
    
    return True, ""


def validate_name(name):
    """
    Validate and sanitize name input
    
    Args:
        name: Name string to validate
    
    Returns:
        Tuple (is_valid, sanitized_name, error_message)
    """
    if not name:
        return False, "", "Name is required"
    
    # Sanitize
    name = sanitize_string(name, max_length=100)
    
    if len(name) == 0:
        return False, "", "Name cannot be empty"
    
    if len(name) > 100:
        return False, name, "Name must be less than 100 characters"
    
    return True, name, ""


def validate_positive_integer(value, field_name="Value", min_value=0, max_value=None):
    """
    Validate positive integer input
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_value: Minimum allowed value (default: 0)
        max_value: Maximum allowed value (optional)
    
    Returns:
        Tuple (is_valid, integer_value, error_message)
    """
    if value is None or value == "":
        return False, None, f"{field_name} is required"
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return False, None, f"{field_name} must be a valid integer"
    
    if int_value < min_value:
        return False, int_value, f"{field_name} must be at least {min_value}"
    
    if max_value is not None and int_value > max_value:
        return False, int_value, f"{field_name} must be at most {max_value}"
    
    return True, int_value, ""


def validate_positive_decimal(value, field_name="Value", min_value=0.0, max_value=None, max_decimal_places=2):
    """
    Validate positive decimal/float input (for prices, amounts)
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_value: Minimum allowed value (default: 0.0)
        max_value: Maximum allowed value (optional)
        max_decimal_places: Maximum decimal places allowed (default: 2)
    
    Returns:
        Tuple (is_valid, decimal_value, error_message)
    """
    if value is None or value == "":
        return False, None, f"{field_name} is required"
    
    try:
        # Use Decimal for precise decimal arithmetic
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return False, None, f"{field_name} must be a valid number"
    
    if decimal_value < Decimal(str(min_value)):
        return False, float(decimal_value), f"{field_name} must be at least {min_value}"
    
    if max_value is not None and decimal_value > Decimal(str(max_value)):
        return False, float(decimal_value), f"{field_name} must be at most {max_value}"
    
    # Check decimal places
    decimal_str = str(decimal_value)
    if '.' in decimal_str:
        decimal_places = len(decimal_str.split('.')[1])
        if decimal_places > max_decimal_places:
            return False, float(decimal_value), f"{field_name} can have at most {max_decimal_places} decimal places"
    
    return True, float(decimal_value), ""


def validate_text_field(value, field_name="Field", min_length=0, max_length=None, required=True):
    """
    Validate and sanitize text field input
    
    Args:
        value: Text to validate
        field_name: Name of the field for error messages
        min_length: Minimum length (default: 0)
        max_length: Maximum length (optional)
        required: Whether the field is required (default: True)
    
    Returns:
        Tuple (is_valid, sanitized_value, error_message)
    """
    if value is None or value == "":
        if required:
            return False, "", f"{field_name} is required"
        else:
            return True, "", ""
    
    # Sanitize
    sanitized = sanitize_string(value, max_length=max_length)
    
    if len(sanitized) < min_length:
        return False, sanitized, f"{field_name} must be at least {min_length} characters"
    
    if max_length and len(sanitized) > max_length:
        return False, sanitized, f"{field_name} must be at most {max_length} characters"
    
    return True, sanitized, ""


def validate_url(url, field_name="URL", required=False):
    """
    Validate URL format
    
    Args:
        url: URL string to validate
        field_name: Name of the field for error messages
        required: Whether the field is required (default: False)
    
    Returns:
        Tuple (is_valid, sanitized_url, error_message)
    """
    if not url or url.strip() == "":
        if required:
            return False, "", f"{field_name} is required"
        else:
            return True, "", ""
    
    # Sanitize
    url = sanitize_string(url, max_length=255)
    
    # Basic URL validation (http/https)
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        return False, url, f"{field_name} must be a valid URL starting with http:// or https://"
    
    return True, url, ""


def validate_enum(value, valid_values, field_name="Value", required=True):
    """
    Validate that value is one of the allowed enum values
    
    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of the field for error messages
        required: Whether the field is required (default: True)
    
    Returns:
        Tuple (is_valid, value, error_message)
    """
    if value is None or value == "":
        if required:
            return False, None, f"{field_name} is required"
        else:
            return True, None, ""
    
    # Sanitize
    value = sanitize_string(value)
    
    if value not in valid_values:
        return False, value, f"{field_name} must be one of: {', '.join(valid_values)}"
    
    return True, value, ""


def validate_category_name(category_name):
    """
    Validate category name
    
    Args:
        category_name: Category name to validate
    
    Returns:
        Tuple (is_valid, sanitized_name, error_message)
    """
    return validate_text_field(
        category_name,
        field_name="Category name",
        min_length=1,
        max_length=100,
        required=True
    )


def validate_product_name(product_name):
    """
    Validate product name
    
    Args:
        product_name: Product name to validate
    
    Returns:
        Tuple (is_valid, sanitized_name, error_message)
    """
    return validate_text_field(
        product_name,
        field_name="Product name",
        min_length=1,
        max_length=200,
        required=True
    )


def validate_product_description(description):
    """
    Validate product description
    
    Args:
        description: Product description to validate
    
    Returns:
        Tuple (is_valid, sanitized_description, error_message)
    """
    return validate_text_field(
        description,
        field_name="Product description",
        min_length=0,
        max_length=1000,
        required=False
    )


def validate_price(price):
    """
    Validate product price
    
    Args:
        price: Price to validate
    
    Returns:
        Tuple (is_valid, price_value, error_message)
    """
    return validate_positive_decimal(
        price,
        field_name="Price",
        min_value=0.01,
        max_value=999999.99,
        max_decimal_places=2
    )


def validate_stock_quantity(stock_quantity):
    """
    Validate stock quantity
    
    Args:
        stock_quantity: Stock quantity to validate
    
    Returns:
        Tuple (is_valid, quantity_value, error_message)
    """
    return validate_positive_integer(
        stock_quantity,
        field_name="Stock quantity",
        min_value=0,
        max_value=999999
    )


def validate_cart_quantity(quantity):
    """
    Validate cart item quantity
    
    Args:
        quantity: Quantity to validate
    
    Returns:
        Tuple (is_valid, quantity_value, error_message)
    """
    return validate_positive_integer(
        quantity,
        field_name="Quantity",
        min_value=1,
        max_value=9999
    )


def validate_order_status(status):
    """
    Validate order status
    
    Args:
        status: Order status to validate
    
    Returns:
        Tuple (is_valid, status_value, error_message)
    """
    valid_statuses = ['Pending', 'Shipped', 'Delivered']
    return validate_enum(
        status,
        valid_statuses,
        field_name="Order status",
        required=True
    )

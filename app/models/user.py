"""User model for authentication and user management"""

from app.database.db_universal import execute_query
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """User model representing a system user (customer or admin)"""
    
    def __init__(self, user_id, name, email, password, role, created_at):
        """
        Initialize User object
        
        Args:
            user_id: Unique user identifier
            name: User's full name
            email: User's email address
            password: Hashed password
            role: User role ('customer' or 'admin')
            created_at: Account creation timestamp
        """
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def create(name, email, password, role='customer'):
        """
        Create a new user in the database
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password (will be hashed)
            role: User role ('customer' or 'admin'), defaults to 'customer'
        
        Returns:
            User ID of the newly created user
        
        Raises:
            Exception: If user creation fails
        """
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        query = """
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """
        params = (name, email, hashed_password, role)
        user_id = execute_query(query, params, fetch=False)
        return user_id
    
    @staticmethod
    def find_by_email(email):
        """
        Find a user by email address
        
        Args:
            email: Email address to search for
        
        Returns:
            User object if found, None otherwise
        """
        query = """
            SELECT user_id, name, email, password, role, created_at
            FROM users
            WHERE email = %s
        """
        params = (email,)
        results = execute_query(query, params, fetch=True)
        
        if results:
            row = results[0]
            return User(
                user_id=row[0],
                name=row[1],
                email=row[2],
                password=row[3],
                role=row[4],
                created_at=row[5]
            )
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """
        Find a user by user ID
        
        Args:
            user_id: User ID to search for
        
        Returns:
            User object if found, None otherwise
        """
        query = """
            SELECT user_id, name, email, password, role, created_at
            FROM users
            WHERE user_id = %s
        """
        params = (user_id,)
        results = execute_query(query, params, fetch=True)
        
        if results:
            row = results[0]
            return User(
                user_id=row[0],
                name=row[1],
                email=row[2],
                password=row[3],
                role=row[4],
                created_at=row[5]
            )
        return None
    
    def verify_password(self, password):
        """
        Verify a password against the stored hash
        
        Args:
            password: Plain text password to verify
        
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password, password)
    
    def to_dict(self, include_password=False):
        """
        Convert User object to dictionary
        
        Args:
            include_password: Whether to include password hash (default: False)
        
        Returns:
            Dictionary representation of the user
        """
        user_dict = {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }
        if include_password:
            user_dict['password'] = self.password
        return user_dict

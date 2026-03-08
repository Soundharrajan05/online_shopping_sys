"""Authentication blueprint for user registration, login, and logout"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.utils.validation import validate_email, validate_password, validate_name
from app.utils.error_handler import log_error, get_user_friendly_message

# Import decorators for use by other modules
from app.auth.decorators import login_required, admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration
    
    GET: Display registration form
    POST: Process registration and create new user account
    """
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        # Validate and sanitize name
        name_valid, sanitized_name, name_error = validate_name(name)
        if not name_valid:
            flash(name_error, 'error')
            return render_template('auth/register.html', name=sanitized_name, email=email)
        
        # Validate and sanitize email
        email_valid, sanitized_email, email_error = validate_email(email)
        if not email_valid:
            flash(email_error, 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        
        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            flash(password_error, 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        
        # Check if email already exists
        try:
            existing_user = User.find_by_email(sanitized_email)
            if existing_user:
                flash('Email already registered. Please use a different email or login.', 'error')
                return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        except Exception as e:
            log_error(e, "register - check existing user")
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        
        # Create new user
        try:
            user_id = User.create(sanitized_name, sanitized_email, password, role='customer')
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            log_error(e, "register - create user")
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login
    
    GET: Display login form
    POST: Authenticate user and create session
    """
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        # Validate input
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html', email=email)
        
        # Sanitize email
        email_valid, sanitized_email, email_error = validate_email(email)
        if not email_valid:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', email=email)
        
        try:
            # Find user by email
            user = User.find_by_email(sanitized_email)
            
            # Verify credentials
            if user and user.verify_password(password):
                # Create session
                session['user_id'] = user.user_id
                session['role'] = user.role
                session['name'] = user.name
                
                flash(f'Welcome back, {user.name}!', 'success')
                
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('user.browse_products'))
            else:
                flash('Invalid email or password', 'error')
                return render_template('auth/login.html', email=email)
        except Exception as e:
            log_error(e, "login")
            flash('Login failed. Please try again.', 'error')
            return render_template('auth/login.html', email=email)
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout
    
    Clear session data and redirect to login page
    """
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))

# Testing Setup Guide

## Database Setup for Property-Based Tests

The property-based tests require a MySQL database connection. Follow these steps to set up the test environment:

### Option 1: Install MySQL Locally (Recommended - Already Set Up!)

1. **Download and Install MySQL** ✓ DONE
   - MySQL 9.6.0 is already installed on your system

2. **Create Test Database** ✓ DONE
   - The `shopping_system_test` database has been created
   - All tables have been set up with the proper schema

3. **Set Environment Variable**
   - The DB_PASSWORD is already configured in `.env` file
   - For manual testing, set it in your terminal:
   ```powershell
   $env:DB_PASSWORD='your_password'
   ```

4. **Run Tests**
   ```powershell
   # Quick way - use the helper script
   .\run_tests.ps1 -Verbose
   
   # Or manually with environment variable
   $env:DB_PASSWORD='your_password'; pytest tests/test_auth_properties.py -v
   
   # Run all tests
   .\run_tests.ps1 tests/ -Verbose
   ```

### Option 2: Use Docker (Recommended)

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop

2. **Start MySQL Container**
   ```bash
   docker run --name mysql-test -e MYSQL_ROOT_PASSWORD=testpass -e MYSQL_DATABASE=shopping_system_test -p 3306:3306 -d mysql:8.0
   ```

3. **Wait for MySQL to Start**
   ```bash
   docker exec -it mysql-test mysql -uroot -ptestpass -e "SELECT 1"
   ```

4. **Load Schema**
   ```bash
   docker exec -i mysql-test mysql -uroot -ptestpass shopping_system_test < schema.sql
   ```

5. **Set Environment Variables**
   ```bash
   set DB_PASSWORD=testpass
   ```

6. **Run Tests**
   ```bash
   pytest tests/test_auth_properties.py -v
   ```

### Option 3: Run Tests Without Database (Mock Mode)

For quick testing without database setup, use the mock-based test:

```bash
pytest tests/test_auth_properties_mock.py -v
```

This version uses mocks to simulate database operations and can run without MySQL.

## Running All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run only property tests
pytest tests/ -k "property" -v

# Run with specific number of examples
pytest tests/ --hypothesis-max-examples=50 -v
```

## Test Structure

- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_auth_properties.py` - Property-based tests for authentication (requires database)
- `tests/test_auth_properties_mock.py` - Mock-based property tests (no database required)
- `tests/README.md` - This file

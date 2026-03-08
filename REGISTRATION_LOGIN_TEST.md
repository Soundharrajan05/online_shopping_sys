# Registration Login Issue - Diagnostic Tool

## Issue

User registers successfully, but cannot login with the same email/password.

## Diagnostic Tool Added

### `/test-new-user/<email>` - Analyze Registered User

This endpoint will:
1. Check if user exists in database
2. Show user details (ID, name, email, role, created date)
3. Analyze password hash format
4. Provide form to test password verification

### `/test-password-verify` - Test Password Match

This endpoint will:
1. Take the email and password
2. Retrieve stored hash from database
3. Test if password matches hash
4. Show detailed results

## Steps to Diagnose

### 1. Push Changes

```bash
git add app/__init__.py REGISTRATION_LOGIN_TEST.md
git commit -m "Add diagnostic tool for registration/login issue"
git push origin main
```

### 2. Wait for Redeploy (5-10 minutes)

### 3. Register a New User

Visit:
```
https://online-shopping-sys.onrender.com/auth/register
```

Register with:
- Name: `Test User`
- Email: `testuser123@example.com`
- Password: `testpass123`

Should show: "Registration successful! Please login."

### 4. Test the New User

Visit (replace with your email):
```
https://online-shopping-sys.onrender.com/test-new-user/testuser123@example.com
```

This will show:
- ✓ User found (or ✗ if not created)
- User details
- Password hash format analysis
- Form to test password

### 5. Test Password Verification

On the same page, enter the password you used during registration (`testpass123`) and click "Test Password".

Results will show:
- ✓ PASSWORD MATCHES (password is correct)
- ✗ PASSWORD DOES NOT MATCH (password is wrong)

### 6. Based on Results

#### If "User not found":
**Problem:** Registration didn't create the user
**Solution:** Check registration error logs

#### If "Password hash format incorrect":
**Problem:** Password not hashed correctly
**Solution:** Check User.create() method

#### If "PASSWORD DOES NOT MATCH":
**Problem:** Password verification failing
**Possible causes:**
1. You entered different password than registration
2. Hash algorithm mismatch
3. Password sanitization issue

#### If "PASSWORD MATCHES":
**Problem:** Something else is wrong with login flow
**Solution:** Use `/real-login-test` to see where login fails

## Common Causes

### Cause 1: Email Sanitization Mismatch

Registration sanitizes email one way, login sanitizes differently.

**Test:** Check if email in database matches exactly what you're typing in login.

### Cause 2: Password Whitespace

Registration might trim password, login might not (or vice versa).

**Test:** Try password without any spaces.

### Cause 3: Case Sensitivity

Email might be stored in different case than you're typing.

**Test:** Try exact case as shown in `/test-new-user`.

### Cause 4: Hash Algorithm Version

Different versions of werkzeug might use different defaults.

**Test:** Check if hash starts with `pbkdf2:sha256:`.

## Quick Test Sequence

1. Register: `testuser999@example.com` / `password123`
2. Visit: `/test-new-user/testuser999@example.com`
3. Enter password: `password123`
4. See if it matches
5. If matches, try login with same credentials
6. If login fails, use `/real-login-test`

## Expected Behavior

**Registration:**
```
User.create() called
→ generate_password_hash(password, method='pbkdf2:sha256')
→ INSERT INTO users (name, email, password, role)
→ Returns user_id
```

**Login:**
```
User.find_by_email(email) called
→ SELECT ... FROM users WHERE email = %s
→ Returns User object with password hash
→ user.verify_password(password) called
→ check_password_hash(stored_hash, entered_password)
→ Returns True/False
```

Both should use same algorithm: `pbkdf2:sha256`

## Share Results

After running the diagnostic:
1. Take screenshot of `/test-new-user/<email>` page
2. Take screenshot of password verification result
3. Share both screenshots
4. I will provide exact fix based on results

This will pinpoint the exact issue.

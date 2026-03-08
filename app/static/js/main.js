// Main JavaScript for Online Shopping System

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    initAutoCloseAlerts();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize quantity controls
    initQuantityControls();
    
    // Initialize confirmation dialogs
    initConfirmationDialogs();
    
    // Add fade-in animation to cards
    initAnimations();
});

/**
 * Auto-close alert messages after 5 seconds
 */
function initAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Initialize Bootstrap form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize quantity increment/decrement controls
 */
function initQuantityControls() {
    // Increment buttons
    document.querySelectorAll('.quantity-increment').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-input');
            const max = parseInt(input.getAttribute('max')) || 999;
            const current = parseInt(input.value) || 0;
            if (current < max) {
                input.value = current + 1;
            }
        });
    });
    
    // Decrement buttons
    document.querySelectorAll('.quantity-decrement').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-input');
            const min = parseInt(input.getAttribute('min')) || 1;
            const current = parseInt(input.value) || 0;
            if (current > min) {
                input.value = current - 1;
            }
        });
    });
    
    // Validate quantity input
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const min = parseInt(this.getAttribute('min')) || 1;
            const max = parseInt(this.getAttribute('max')) || 999;
            let value = parseInt(this.value) || min;
            
            if (value < min) value = min;
            if (value > max) value = max;
            
            this.value = value;
        });
    });
}

/**
 * Initialize confirmation dialogs for destructive actions
 */
function initConfirmationDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Initialize fade-in animations
 */
function initAnimations() {
    const cards = document.querySelectorAll('.card, .cart-item');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 50);
    });
}

/**
 * Show loading spinner
 */
function showLoading() {
    let spinner = document.querySelector('.spinner-overlay');
    if (!spinner) {
        spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden">Loading...</span></div>';
        document.body.appendChild(spinner);
    }
    spinner.classList.add('active');
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.classList.remove('active');
    }
}

/**
 * Update cart item quantity via AJAX (if needed in future)
 */
function updateCartQuantity(cartId, quantity) {
    showLoading();
    
    fetch(`/user/cart/update/${cartId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            location.reload();
        } else {
            alert(data.message || 'Failed to update cart');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        alert('An error occurred while updating the cart');
    });
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Search products with debounce
 */
const searchInput = document.querySelector('#product-search');
if (searchInput) {
    searchInput.addEventListener('input', debounce(function(e) {
        const searchTerm = e.target.value;
        if (searchTerm.length >= 3 || searchTerm.length === 0) {
            // Submit the search form or filter products
            const form = e.target.closest('form');
            if (form) {
                form.submit();
            }
        }
    }, 500));
}

// Export functions for use in other scripts
window.shopApp = {
    showLoading,
    hideLoading,
    updateCartQuantity,
    formatCurrency
};

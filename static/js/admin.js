// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Flash message close functionality
    const flashCloseButtons = document.querySelectorAll('.flash-close');
    flashCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = '#dee2e6';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Image preview for file uploads
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = input.parentElement.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview';
                        input.parentElement.appendChild(preview);
                    }
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 1rem;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Confirm delete actions
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Number input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // SKU auto-generation (optional)
    const nameInput = document.querySelector('#name');
    const skuInput = document.querySelector('#sku');
    if (nameInput && skuInput && !skuInput.value) {
        nameInput.addEventListener('input', function() {
            const name = this.value.trim();
            if (name) {
                const sku = name.toUpperCase()
                    .replace(/[^A-Z0-9]/g, '')
                    .substring(0, 6) + 
                    Math.floor(Math.random() * 1000).toString().padStart(3, '0');
                skuInput.value = sku;
            }
        });
    }
});

// Price type toggle function (for product forms)
function togglePriceFields() {
    const priceType = document.getElementById('price_type');
    const weightGroup = document.getElementById('weight_group');
    const priceGroup = document.getElementById('price_group');
    const weightInput = document.getElementById('weight_in_grams');
    const priceInput = document.getElementById('base_price');
    
    if (!priceType) return;
    
    if (priceType.value === 'per_gram') {
        if (weightGroup) weightGroup.style.display = 'block';
        if (priceGroup) priceGroup.style.display = 'none';
        if (weightInput) weightInput.required = true;
        if (priceInput) {
            priceInput.required = false;
            priceInput.value = 0;
        }
    } else {
        if (weightGroup) weightGroup.style.display = 'none';
        if (priceGroup) priceGroup.style.display = 'block';
        if (weightInput) {
            weightInput.required = false;
            weightInput.value = 0;
        }
        if (priceInput) priceInput.required = true;
    }
}

// Rate calculator function
function updateCalculator() {
    const metalSelect = document.getElementById('calc_metal');
    const weightInput = document.getElementById('calc_weight');
    
    if (!metalSelect || !weightInput) return;
    
    const metal = metalSelect.value;
    const weight = parseFloat(weightInput.value) || 0;
    
    // These rates should be passed from the template
    const rates = window.metalRates || {
        gold: { rate: 6500, margin: 10 },
        silver: { rate: 85, margin: 15 }
    };
    
    const baseRate = rates[metal].rate;
    const margin = rates[metal].margin;
    const finalRate = baseRate * (1 + margin / 100);
    const totalPrice = finalRate * weight;
    
    const baseRateEl = document.getElementById('calc_base_rate');
    const marginEl = document.getElementById('calc_margin');
    const finalRateEl = document.getElementById('calc_final_rate');
    const totalEl = document.getElementById('calc_total');
    
    if (baseRateEl) baseRateEl.textContent = `₹${baseRate.toFixed(2)}/g`;
    if (marginEl) marginEl.textContent = `${margin}%`;
    if (finalRateEl) finalRateEl.textContent = `₹${finalRate.toFixed(2)}/g`;
    if (totalEl) totalEl.textContent = `₹${totalPrice.toFixed(2)}`;
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions for global use
window.togglePriceFields = togglePriceFields;
window.updateCalculator = updateCalculator;
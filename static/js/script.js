// Main JavaScript for Samrat Jewellers

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Flash message close functionality
    const flashCloseButtons = document.querySelectorAll('.flash-close');
    flashCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.parentElement;
            flashMessage.style.opacity = '0';
            flashMessage.style.transform = 'translateX(100%)';
            setTimeout(() => {
                flashMessage.remove();
            }, 300);
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message.parentElement) {
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    message.remove();
                }, 300);
            }
        }, 5000);
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Category card hover effects
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Loading animation for buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                
                // Remove loading state after 2 seconds (adjust as needed)
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.innerHTML = originalText;
                }, 2000);
            }
        });
    });
    
    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Rate freshness color coding
    updateRateFreshness();
    
    // Update rate freshness every minute
    setInterval(updateRateFreshness, 60000);
});

// Function to update rate freshness indicators
function updateRateFreshness() {
    const rateTimeElements = document.querySelectorAll('.rate-time span');
    
    rateTimeElements.forEach(element => {
        const text = element.textContent;
        const minutesMatch = text.match(/(\d+)\s*min/);
        const hoursMatch = text.match(/(\d+)\s*hrs?/);
        
        let minutes = 0;
        if (minutesMatch) {
            minutes = parseInt(minutesMatch[1]);
        } else if (hoursMatch) {
            minutes = parseInt(hoursMatch[1]) * 60;
        }
        
        // Remove existing classes
        element.classList.remove('rate-fresh', 'rate-moderate', 'rate-old');
        
        // Add appropriate class based on time
        if (minutes < 30) {
            element.classList.add('rate-fresh');
        } else if (minutes < 120) {
            element.classList.add('rate-moderate');
        } else {
            element.classList.add('rate-old');
        }
    });
}

// WhatsApp integration helper
function formatWhatsAppMessage(productName, sku, weight, price, metalType, currentRate) {
    const timestamp = new Date().toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    let message = `Hello! I'm interested in the following product:\n\n`;
    message += `🔸 Product: ${productName}\n`;
    message += `🔸 SKU: ${sku}\n`;
    
    if (weight && weight > 0) {
        message += `🔸 Weight: ${weight}g\n`;
        message += `🔸 Metal: ${metalType}\n`;
        message += `🔸 Current ${metalType} rate: ₹${currentRate}/gram\n`;
    }
    
    message += `🔸 Price: ₹${price}\n`;
    message += `🔸 Inquiry time: ${timestamp}\n\n`;
    message += `Please provide more details about availability and purchase process.\n\n`;
    message += `Thank you!`;
    
    return message;
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

// Utility function to format numbers
function formatNumber(number, decimals = 2) {
    return parseFloat(number).toFixed(decimals);
}

// Search functionality (if needed)
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (searchInput && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    }
}

// Perform search (placeholder - implement with actual search logic)
function performSearch(query) {
    // This would typically make an AJAX request to search products
    console.log('Searching for:', query);
    
    // Placeholder implementation
    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = `<div class="search-item">Searching for "${query}"...</div>`;
    searchResults.style.display = 'block';
}

// Form validation helpers
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^[+]?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

// Animation helpers
function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const change = end - start;
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (change * progress);
        element.textContent = Math.floor(current);
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

// Initialize animations when elements come into view
function initializeAnimations() {
    const animatedElements = document.querySelectorAll('[data-animate]');
    
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const animationType = element.dataset.animate;
                
                switch (animationType) {
                    case 'fadeIn':
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                        break;
                    case 'slideIn':
                        element.style.transform = 'translateX(0)';
                        break;
                    case 'scaleIn':
                        element.style.transform = 'scale(1)';
                        break;
                }
                
                animationObserver.unobserve(element);
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        animationObserver.observe(element);
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    
    // You could send error reports to your server here
    // sendErrorReport(e.error);
});

// Performance monitoring
window.addEventListener('load', function() {
    // Log page load time
    const loadTime = performance.now();
    console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
    
    // You could send performance metrics to your analytics here
    // sendPerformanceMetrics(loadTime);
});

// Export functions for use in other scripts
window.SamratJewellers = {
    formatWhatsAppMessage,
    formatCurrency,
    formatNumber,
    validateEmail,
    validatePhone,
    animateValue
};
# Samrat Jewellers - eCommerce Web Application

A complete eCommerce web application for Samrat Jewellers built with Flask, MySQL, and modern web technologies. Features a clean iOS-style UI with glassmorphism effects and WhatsApp integration for customer inquiries.

## Features

### Frontend
- **Modern iOS-style UI** with glassmorphism effects
- **Responsive design** optimized for mobile and desktop
- **Live metal rates** display with freshness indicators
- **Product catalog** with categories and filtering
- **WhatsApp integration** for customer inquiries
- **Clean animations** and smooth transitions

### Backend
- **Flask web framework** with Jinja2 templating
- **MySQL database** for data storage
- **Admin dashboard** for product and rate management
- **Secure authentication** with password hashing
- **Live metal rate** integration (API ready)
- **Image upload** and management

### Key Pages
- **Home**: Hero section, metal rates, featured products
- **Shop**: Product catalog with category filters
- **Product Details**: Detailed product information with WhatsApp inquiry
- **About**: Company information and values
- **Contact**: Multiple contact methods and inquiry form
- **Admin Dashboard**: Complete product and rate management

## Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd samrat-jewllers
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL database**
   ```bash
   mysql -u root -p < database_setup.sql
   ```

5. **Configure database connection**
   Edit the `DB_CONFIG` in `app.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_mysql_password',
       'database': 'samrat_jewellers'
   }
   ```

6. **Create upload directories**
   ```bash
   mkdir -p static/images/products
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   - Website: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin/login
   - Default admin credentials: admin@samratjewellers.com / admin123

## Configuration

### WhatsApp Integration
1. Go to Admin Panel → Settings
2. Update the WhatsApp number (with country code, no + sign)
3. Test the WhatsApp link functionality

### Metal Rates API Integration
To integrate with a live metal rates API:

1. **Choose an API provider** (e.g., metals-api.com, goldapi.io)
2. **Get API credentials**
3. **Update the `update_metal_rates_api()` function** in `app.py`:
   ```python
   def update_metal_rates_api():
       try:
           # Replace with actual API call
           response = requests.get('https://api.metals.live/v1/spot/gold', 
                                 headers={'Authorization': 'Bearer YOUR_API_KEY'})
           data = response.json()
           
           # Update database with real rates
           gold_rate = data['gold']['price_per_gram_inr']
           silver_rate = data['silver']['price_per_gram_inr']
           
           # ... rest of the function
       except Exception as e:
           print(f"Error updating rates: {e}")
           return False
   ```

4. **Set up automatic updates** using cron jobs or task scheduler

### Email Configuration (Optional)
For contact form submissions, configure email settings:
```python
# Add to app.py
import smtplib
from email.mime.text import MIMEText

SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password'
}
```

## Database Schema

### Products Table
- `id`: Primary key
- `name`: Product name
- `sku`: Unique product identifier
- `category`: Product category
- `description`: Product description
- `price_type`: 'fixed' or 'per_gram'
- `weight_in_grams`: Weight for per-gram products
- `base_price`: Base/fixed price
- `metal_type`: 'gold' or 'silver'
- `image`: Image filename
- `stock`: Available quantity

### Metal Rates Table
- `id`: Primary key
- `metal`: 'gold' or 'silver'
- `rate_per_gram`: Current rate per gram
- `margin_percent`: Profit margin percentage
- `source`: Rate source ('API' or 'Manual')
- `fetched_at`: Last update timestamp

### Users Table
- `id`: Primary key
- `name`: User name
- `email`: Email address
- `password_hash`: Hashed password
- `role`: User role ('admin' or 'user')

### Settings Table
- `id`: Primary key
- `setting_key`: Setting identifier
- `setting_value`: Setting value
- `updated_at`: Last update timestamp

## Admin Panel Features

### Dashboard
- Product count statistics
- Current metal rates display
- Recent products list
- Quick action buttons

### Product Management
- Add new products with images
- Edit existing products
- Delete products
- View product details
- Stock management

### Metal Rates Management
- Manual rate updates
- Margin percentage settings
- Rate freshness indicators
- Price calculation preview

### Settings
- WhatsApp number configuration
- System information display
- Integration guides

## Customization

### Styling
- Main styles: `static/css/style.css`
- Admin styles: `static/css/admin.css`
- Color scheme defined in CSS variables
- Glassmorphism effects and animations

### JavaScript
- Main functionality: `static/js/script.js`
- Admin functionality: `static/js/admin.js`
- WhatsApp integration helpers
- Form validation and animations

### Templates
- Base template: `templates/base.html`
- Page templates: `templates/*.html`
- Admin templates: `templates/admin/*.html`
- Jinja2 templating with dynamic data

## Security Features

- **Password hashing** using Werkzeug
- **SQL injection protection** with parameterized queries
- **File upload validation** for images
- **Session management** for admin authentication
- **Input validation** on both client and server side

## Performance Optimization

- **Image optimization** recommendations
- **Lazy loading** for images
- **Minified CSS/JS** (production ready)
- **Database indexing** on frequently queried fields
- **Caching strategies** for metal rates

## Deployment

### Production Setup
1. **Use a production WSGI server** (Gunicorn, uWSGI)
2. **Configure reverse proxy** (Nginx, Apache)
3. **Set up SSL certificates** for HTTPS
4. **Configure environment variables** for sensitive data
5. **Set up database backups**
6. **Configure logging** and monitoring

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DB_HOST=your-db-host
export DB_USER=your-db-user
export DB_PASSWORD=your-db-password
export WHATSAPP_NUMBER=your-whatsapp-number
```

## API Integration Examples

### Metal Rates APIs
- **Metals API**: https://metals-api.com/
- **Gold API**: https://goldapi.io/
- **Precious Metals API**: https://preciousmetals-api.com/

### WhatsApp Business API
- **Official WhatsApp Business API**
- **Third-party providers** (Twilio, MessageBird)

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check MySQL credentials and service status
2. **Image upload issues**: Verify directory permissions
3. **WhatsApp links not working**: Check number format and URL encoding
4. **Metal rates not updating**: Verify API credentials and network connectivity

### Debug Mode
Enable debug mode for development:
```python
app.run(debug=True)
```

## Support

For technical support or customization requests:
- Email: support@samratjewellers.com
- Documentation: Check inline code comments
- Issues: Create GitHub issues for bugs

## License

This project is proprietary software for Samrat Jewellers. All rights reserved.

## Changelog

### Version 1.0.0
- Initial release with complete eCommerce functionality
- iOS-style UI with glassmorphism effects
- WhatsApp integration for customer inquiries
- Admin dashboard for product and rate management
- Live metal rates with API integration support
- Responsive design for all devices
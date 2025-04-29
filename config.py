import os

# Database configuration
DATABASE_DIR = "data"
DATABASE_NAME = "supermarket.db"
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

# Application settings
APP_NAME = "Supermarket Billing System"
APP_VERSION = "1.0.0"

# Company information
COMPANY_NAME = "Supermarket Billing System"
COMPANY_ADDRESS = "123 Main Street, City, Country"
COMPANY_PHONE = "+1 (555) 123-4567"
COMPANY_EMAIL = "info@supermarket.com"

# Currency settings
CURRENCY_SYMBOL = "$"
CURRENCY_CODE = "USD"

# Tax settings
DEFAULT_TAX_RATE = 0.10  # 10%

# System settings
RECEIPT_DIRECTORY = "receipts"
REPORT_DIRECTORY = "reports"

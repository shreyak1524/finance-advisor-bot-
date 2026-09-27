"""
Shared constants used across models, routes, templates and JS.
Keeping them in one place avoids typos and keeps dropdowns consistent.
"""

EXPENSE_CATEGORIES = [
    "Rent",
    "Food",
    "Transport",
    "Education",
    "Healthcare",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Travel",
    "Groceries",
    "Household",
    "Other",
]

# Categories treated as "Needs" for the 50/30/20 style budget generator.
NEED_CATEGORIES = {"Rent", "Food", "Groceries", "Transport", "Bills & Utilities",
                    "Healthcare", "Education", "Household"}
# Categories treated as "Wants".
WANT_CATEGORIES = {"Shopping", "Entertainment", "Travel", "Other"}

INCOME_SOURCES = [
    "Salary",
    "Freelancing",
    "Part-time work",
    "Business",
    "Allowance",
    "Investment",
    "Other",
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Debit Card",
    "Credit Card",
    "Bank Transfer",
    "Other",
]

GOAL_TYPES = [
    "Emergency Fund",
    "New Laptop",
    "Vacation",
    "Education",
    "Bike",
    "Investment",
    "Custom Goal",
]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

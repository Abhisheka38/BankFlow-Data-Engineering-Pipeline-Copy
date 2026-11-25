
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "data" / "sample"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Fixed seed makes generated data reproducible
random.seed(42)


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def random_date(start_date, end_date):
    """Generate a random date between two dates."""
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, days))


def random_datetime(start_date, end_date):
    """Generate a random datetime between two datetimes."""
    seconds = int((end_date - start_date).total_seconds())
    return start_date + timedelta(seconds=random.randint(0, seconds))


def add_months(original_date, months):
    """Add months to a date while handling month boundaries."""
    month_index = original_date.month - 1 + months
    year = original_date.year + month_index // 12
    month = month_index % 12 + 1

    import calendar
    day = min(
        original_date.day,
        calendar.monthrange(year, month)[1]
    )

    return date(year, month, day)


def save_dataset(data, filename):
    """Save a list of records as a CSV dataset."""
    dataframe = pd.DataFrame(data)

    output_path = OUTPUT_DIR / filename

    dataframe.to_csv(output_path, index=False)

    print(
        f"Created {filename}: "
        f"{len(dataframe)} records"
    )


# --------------------------------------------------
# 3. GENERATE BRANCHES
# --------------------------------------------------

cities = [
    ("Colombo", "Colombo", "Western"),
    ("Kandy", "Kandy", "Central"),
    ("Galle", "Galle", "Southern"),
    ("Jaffna", "Jaffna", "Northern"),
    ("Kurunegala", "Kurunegala", "North Western"),
    ("Anuradhapura", "Anuradhapura", "North Central"),
    ("Badulla", "Badulla", "Uva"),
    ("Ratnapura", "Ratnapura", "Sabaragamuwa"),
    ("Trincomalee", "Trincomalee", "Eastern"),
    ("Matara", "Matara", "Southern"),
]

branches = []

for i in range(1, 21):

    city, district, province = cities[(i - 1) % len(cities)]

    branches.append({
        "branch_id": f"BR{i:04d}",
        "branch_name": f"Branch {i:02d}",
        "city": city,
        "district": district,
        "province": province,
        "opened_date": random_date(
            date(1980, 1, 1),
            date(2023, 12, 31)
        )
    })

branch_ids = [branch["branch_id"] for branch in branches]


# --------------------------------------------------
# 4. GENERATE CUSTOMERS
# --------------------------------------------------

first_names = [
    "Amal", "Nimal", "Kamal", "Saman", "Kasun",
    "Nuwan", "Tharushi", "Dinushi", "Kavindi",
    "Sanduni", "Ishara", "Chathura"
]

last_names = [
    "Perera", "Silva", "Fernando", "Jayasinghe",
    "Wickramasinghe", "Gunawardena", "De Silva",
    "Bandara", "Senanayake", "Rajapaksha"
]

occupations = [
    "Teacher", "Engineer", "Accountant",
    "Doctor", "Business Owner", "Software Developer",
    "Student", "Manager", "Nurse", "Self Employed"
]

customers = []

for i in range(1, 1001):

    customers.append({
        "customer_id": f"CUST{i:05d}",
        "first_name": random.choice(first_names),
        "last_name": random.choice(last_names),
        "date_of_birth": random_date(
            date(1960, 1, 1),
            date(2005, 12, 31)
        ),
        "gender": random.choice(["Male", "Female"]),
        "city": random.choice(cities)[0],
        "occupation": random.choice(occupations),
        "registration_date": random_date(
            date(2020, 1, 1),
            date(2025, 12, 31)
        ),
        "home_branch_id": random.choice(branch_ids),
        "customer_status": random.choice(
            ["Active", "Inactive"]
        )
    })

customer_ids = [customer["customer_id"] for customer in customers]

customer_branch = {
    customer["customer_id"]: customer["home_branch_id"]
    for customer in customers
}


# --------------------------------------------------
# 5. GENERATE ACCOUNTS
# --------------------------------------------------

accounts = []

account_types = [
    "Savings",
    "Current",
    "Fixed Deposit"
]

account_counter = 1

for i, customer in enumerate(customers):

    # First 200 customers have two accounts.
    # Remaining 800 customers have one account.
    number_of_accounts = 2 if i < 200 else 1

    for _ in range(number_of_accounts):

        accounts.append({
            "account_id": f"ACC{account_counter:06d}",
            "customer_id": customer["customer_id"],
            "branch_id": customer["home_branch_id"],
            "account_type": random.choice(account_types),
            "currency": "LKR",
            "opened_date": random_date(
                date(2020, 1, 1),
                date(2026, 1, 1)
            ),
            "current_balance": round(
                random.uniform(1000, 2000000), 2
            ),
            "account_status": random.choice(
                ["Active", "Inactive", "Closed"]
            )
        })

        account_counter += 1

account_ids = [account["account_id"] for account in accounts]

account_branch = {
    account["account_id"]: account["branch_id"]
    for account in accounts
}


# --------------------------------------------------
# 6. GENERATE TRANSACTIONS
# --------------------------------------------------

transactions = []

transaction_types = ["Debit", "Credit"]

channels = [
    "ATM",
    "Mobile Banking",
    "Online Banking",
    "Branch"
]

transaction_descriptions = [
    "Cash Withdrawal",
    "Cash Deposit",
    "Fund Transfer",
    "Bill Payment",
    "Salary Credit",
    "Online Purchase"
]

for i in range(1, 10001):

    account_id = random.choice(account_ids)

    transactions.append({
        "transaction_id": f"TXN{i:07d}",
        "account_id": account_id,
        "branch_id": account_branch[account_id],
        "transaction_timestamp": random_datetime(
            datetime(2025, 1, 1),
            datetime(2026, 10, 31, 23, 59, 59)
        ),
        "transaction_type": random.choice(transaction_types),
        "amount": round(
            random.uniform(100, 500000), 2
        ),
        "currency": "LKR",
        "channel": random.choice(channels),
        "transaction_status": random.choice(
            ["Successful", "Pending", "Failed"]
        ),
        "description": random.choice(transaction_descriptions)
    })


# --------------------------------------------------
# 7. GENERATE LOANS
# --------------------------------------------------

loans = []

loan_types = [
    "Personal",
    "Housing",
    "Vehicle",
    "Business"
]

selected_customers = random.sample(customer_ids, 500)

for i, customer_id in enumerate(selected_customers, start=1):

    loan_date = random_date(
        date(2024, 1, 1),
        date(2025, 12, 31)
    )

    loans.append({
        "loan_id": f"LOAN{i:05d}",
        "customer_id": customer_id,
        "branch_id": customer_branch[customer_id],
        "loan_type": random.choice(loan_types),
        "principal_amount": round(
            random.uniform(100000, 10000000), 2
        ),
        "annual_interest_rate": round(
            random.uniform(8, 18), 2
        ),
        "term_months": random.choice(
            [12, 24, 36, 48, 60]
        ),
        "loan_date": loan_date,
        "loan_status": random.choice(
            ["Active", "Closed", "Defaulted"]
        )
    })


# --------------------------------------------------
# 8. GENERATE LOAN PAYMENTS
# --------------------------------------------------

payments = []

payment_methods = [
    "Bank Transfer",
    "Standing Order",
    "Branch Deposit",
    "Online Banking"
]

payment_counter = 1

for loan in loans:

    # Six monthly payment records per loan
    number_of_payments = 6

    estimated_total = loan["principal_amount"] * (
        1 + (
            loan["annual_interest_rate"] / 100
            * number_of_payments / 12
        )
    )

    monthly_payment = round(
        estimated_total / number_of_payments, 2
    )

    for month in range(1, number_of_payments + 1):

        payments.append({
            "payment_id": f"PAY{payment_counter:06d}",
            "loan_id": loan["loan_id"],
            "payment_date": add_months(
                loan["loan_date"], month
            ),
            "amount_paid": monthly_payment,
            "payment_method": random.choice(payment_methods),
            "payment_status": random.choice(
                ["Paid", "Pending", "Failed"]
            )
        })

        payment_counter += 1


# --------------------------------------------------
# 9. SAVE ALL SIX DATASETS
# --------------------------------------------------

print("\nGenerating BankFlow banking datasets...\n")

save_dataset(branches, "branches.csv")
save_dataset(customers, "customers.csv")
save_dataset(accounts, "accounts.csv")
save_dataset(transactions, "transactions.csv")
save_dataset(loans, "loans.csv")
save_dataset(payments, "payments.csv")

print("\nAll banking datasets generated successfully!")
print(f"Dataset location: {OUTPUT_DIR}")

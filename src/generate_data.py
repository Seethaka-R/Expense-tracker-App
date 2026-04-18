"""
generate_data.py  —  Synthetic Expense Dataset Generator
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import date, timedelta

np.random.seed(42)
random.seed(42)

CATEGORIES = {
    "Food & Dining":    (350,  120),
    "Rent":             (12000, 400),
    "Transportation":   (180,   70),
    "Entertainment":    (600,  250),
    "Utilities":        (1500, 300),
    "Healthcare":       (900,  450),
    "Shopping":         (1100, 550),
    "Education":        (2000, 800),
    "Travel":           (3500, 1500),
    "Miscellaneous":    (280,  130),
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
CATEGORY_WEIGHTS = [0.25, 0.08, 0.15, 0.10, 0.07, 0.06, 0.10, 0.05, 0.04, 0.10]

DESCRIPTIONS = {
    "Food & Dining":    ["Swiggy Order", "Zomato Delivery", "Restaurant Dinner", "Grocery Store", "Cafe Coffee", "Lunch Canteen"],
    "Rent":             ["Monthly Rent", "House Rent", "PG Rent", "Apartment Rent"],
    "Transportation":   ["Uber Ride", "Ola Cab", "Metro Card", "Auto Rickshaw", "Petrol Fill", "Bus Pass"],
    "Entertainment":    ["Netflix", "Amazon Prime", "Movie Tickets", "Concert", "Gaming", "Spotify"],
    "Utilities":        ["Electricity Bill", "Water Bill", "Internet Bill", "Gas Bill", "Mobile Recharge"],
    "Healthcare":       ["Doctor Visit", "Medicine Purchase", "Lab Tests", "Dental Checkup", "Pharmacy"],
    "Shopping":         ["Amazon Order", "Flipkart Purchase", "Clothes Shopping", "Electronics", "Books"],
    "Education":        ["Course Fee", "Books Purchase", "Online Course", "Tuition Fee", "Workshop"],
    "Travel":           ["Flight Tickets", "Hotel Stay", "Train Booking", "Trip Expenses", "Visa Fee"],
    "Miscellaneous":    ["ATM Withdrawal", "Gift Purchase", "Charity Donation", "Subscription", "Others"],
}


def generate_expenses(n_records: int = 600, year: int = 2024) -> pd.DataFrame:
    records = []
    start = pd.Timestamp(f"{year}-01-01")
    end   = pd.Timestamp(f"{year}-12-31")
    date_range = pd.date_range(start, end)

    for _ in range(n_records):
        category = random.choices(list(CATEGORIES.keys()), weights=CATEGORY_WEIGHTS, k=1)[0]
        mean, std = CATEGORIES[category]
        amount = max(10, round(abs(np.random.normal(mean, std)), 2))
        date = random.choice(list(date_range))
        payment = random.choice(PAYMENT_METHODS)
        description = random.choice(DESCRIPTIONS[category])

        records.append({
            "date":           date.strftime("%Y-%m-%d"),
            "category":       category,
            "amount":         amount,
            "payment_method": payment,
            "description":    description,
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def save_dataset(df: pd.DataFrame, path: str = "data/raw/expenses.csv") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[OK] Dataset saved -> {path}  ({len(df)} rows)")


if __name__ == "__main__":
    df = generate_expenses()
    save_dataset(df)
    print(df.head())

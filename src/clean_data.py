"""
clean_data.py  —  Data Cleaning & Feature Engineering
"""

import pandas as pd
import os


def load_data(path: str = "data/raw/expenses.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    print(f"[OK] Loaded {len(df)} rows from {path}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df = df.dropna(subset=["amount", "date"])
    df["amount"] = df["amount"].abs().round(2)
    df["payment_method"] = df["payment_method"].fillna("Unknown").str.strip()
    df["category"] = df["category"].str.strip()
    df["amount"] = df["amount"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    print(f"[OK] Cleaned data: {len(df)} rows remain")
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df["year"]        = df["date"].dt.year
    df["month"]       = df["date"].dt.month
    df["month_name"]  = df["date"].dt.strftime("%b")
    df["week"]        = df["date"].dt.isocalendar().week.astype(int)
    df["day"]         = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.day_name()
    df["quarter"]     = df["date"].dt.quarter
    df["is_weekend"]  = df["date"].dt.dayofweek >= 5
    print("[OK] Features added: month, week, quarter, day_of_week, is_weekend")
    return df


def save_clean(df: pd.DataFrame, path: str = "data/processed/expenses_clean.csv") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[OK] Clean data saved -> {path}")


if __name__ == "__main__":
    df = load_data()
    df = clean(df)
    df = add_features(df)
    save_clean(df)

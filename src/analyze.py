"""
analyze.py  —  Core Analysis Functions
"""

import pandas as pd
import os


def load_clean(path: str = "data/processed/expenses_clean.csv") -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def category_summary(df):
    s = (df.groupby("category")["amount"]
         .agg(["sum","mean","count"])
         .rename(columns={"sum":"total","mean":"avg","count":"transactions"})
         .sort_values("total", ascending=False).round(2))
    s["pct"] = (s["total"] / s["total"].sum() * 100).round(1)
    return s


def monthly_trend(df):
    return (df.groupby(["month","month_name"])["amount"]
            .sum().reset_index()
            .sort_values("month").round(2))


def payment_summary(df):
    return (df.groupby("payment_method")["amount"]
            .agg(["sum","count"])
            .rename(columns={"sum":"total","count":"transactions"})
            .sort_values("total", ascending=False).round(2))


def weekend_vs_weekday(df):
    return (df.groupby("is_weekend")["amount"]
            .agg(["sum","mean","count"])
            .rename(index={True:"Weekend",False:"Weekday"}).round(2))


def top_expenses(df, n=10):
    return (df[["date","category","amount","payment_method","description"]]
            .sort_values("amount", ascending=False).head(n))


def quarterly_summary(df):
    return df.groupby("quarter")["amount"].sum().round(2)


def generate_insights(df):
    total       = df["amount"].sum()
    top_cat     = df.groupby("category")["amount"].sum()
    top_month   = df.groupby("month_name")["amount"].sum()
    avg_monthly = df.groupby("month")["amount"].sum().mean()
    wk  = df[df["is_weekend"]]["amount"].sum()
    wd  = df[~df["is_weekend"]]["amount"].sum()
    top_pay     = df["payment_method"].value_counts().idxmax()

    return [
        f"Total annual expenditure: Rs {total:,.2f}",
        f"Highest spending category: {top_cat.idxmax()} (Rs {top_cat.max():,.2f})",
        f"Most expensive month: {top_month.idxmax()} (Rs {top_month.max():,.2f})",
        f"Average monthly spending: Rs {avg_monthly:,.2f}",
        f"Most used payment method: {top_pay}",
        f"Weekend spending: Rs {wk:,.2f}  |  Weekday spending: Rs {wd:,.2f}",
        f"Lowest spending category: {top_cat.idxmin()} (Rs {top_cat.min():,.2f})",
        f"Total transactions recorded: {len(df)}",
    ]


def save_insights(insights, path="outputs/reports/insights.txt"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("=" * 52 + "\n")
        f.write("  EXPENSE TRACKER — AUTO-GENERATED INSIGHTS\n")
        f.write("=" * 52 + "\n\n")
        for i, line in enumerate(insights, 1):
            f.write(f"{i}. {line}\n")
    print(f"[OK] Insights saved -> {path}")


if __name__ == "__main__":
    df = load_clean()
    print(category_summary(df))
    for line in generate_insights(df):
        print(" *", line)
    save_insights(generate_insights(df))

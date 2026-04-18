"""
visualize.py  —  Chart Generation (8 charts)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "figure.dpi": 150, "axes.titlesize": 14,
    "axes.titleweight": "bold", "axes.labelsize": 11,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
})

OUT = "outputs/charts"
os.makedirs(OUT, exist_ok=True)

INR = mticker.FuncFormatter(lambda x, _: f"Rs {x:,.0f}")


def _save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, f"{name}.png"), bbox_inches="tight")
    plt.close()
    print(f"  [OK] {name}.png saved")


def chart_category_bar(df):
    cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    colors = sns.color_palette("muted", len(cat))
    bars = ax.bar(cat.index, cat.values, color=colors, edgecolor="white", linewidth=0.5)
    ax.yaxis.set_major_formatter(INR)
    ax.set_title("Category-wise Total Spending")
    ax.set_xlabel("Category"); ax.set_ylabel("Amount (Rs)")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                f"Rs {bar.get_height():,.0f}", ha="center", va="bottom", fontsize=7)
    plt.xticks(rotation=30, ha="right")
    _save("01_category_bar")


def chart_category_pie(df):
    cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts, autotexts = ax.pie(
        cat.values, labels=cat.index, autopct="%1.1f%%",
        startangle=140, colors=sns.color_palette("pastel", len(cat)), pctdistance=0.82)
    for t in autotexts: t.set_fontsize(8)
    ax.set_title("Spending Distribution by Category", pad=20)
    _save("02_category_pie")


def chart_monthly_trend(df):
    monthly = df.groupby("month")["amount"].sum().reset_index()
    labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["month"], monthly["amount"], marker="o", linewidth=2.5,
            color="#4C72B0", markersize=8)
    ax.fill_between(monthly["month"], monthly["amount"], alpha=0.12, color="#4C72B0")
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(INR)
    ax.set_title("Monthly Spending Trend"); ax.set_ylabel("Amount (Rs)")
    _save("03_monthly_trend")


def chart_payment_methods(df):
    pm = df.groupby("payment_method")["amount"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    pm.plot(kind="barh", ax=ax, color=sns.color_palette("Set2", len(pm)), edgecolor="white")
    ax.xaxis.set_major_formatter(INR)
    ax.set_title("Spending by Payment Method"); ax.set_xlabel("Amount (Rs)")
    _save("04_payment_methods")


def chart_heatmap(df):
    pivot = df.pivot_table(values="amount", index="category",
                           columns="month", aggfunc="sum", fill_value=0)
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", fmt=".0f",
                linewidths=0.4, linecolor="white", cbar_kws={"label":"Amount (Rs)"})
    ax.set_title("Category x Month Spending Heatmap")
    _save("05_heatmap")


def chart_weekend_vs_weekday(df):
    data = df.groupby("is_weekend")["amount"].sum()
    data.index = ["Weekday", "Weekend"]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(data.index, data.values,
                  color=["#4C72B0","#DD8452"], width=0.4, edgecolor="white")
    ax.yaxis.set_major_formatter(INR)
    ax.set_title("Weekday vs Weekend Spending"); ax.set_ylabel("Total Amount (Rs)")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                f"Rs {bar.get_height():,.0f}", ha="center", fontsize=10, fontweight="bold")
    _save("06_weekend_vs_weekday")


def chart_top_expenses(df):
    top = df.nlargest(10, "amount").copy()
    top["label"] = top["description"].str[:22] + " (" + top["category"].str[:8] + ")"
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top["label"], top["amount"],
            color=sns.color_palette("Reds_r", len(top)), edgecolor="white")
    ax.xaxis.set_major_formatter(INR)
    ax.set_title("Top 10 Highest Expenses"); ax.set_xlabel("Amount (Rs)")
    ax.invert_yaxis()
    _save("07_top_expenses")


def chart_quarterly(df):
    q = df.groupby("quarter")["amount"].sum()
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar([f"Q{i}" for i in q.index], q.values,
                  color=sns.color_palette("Blues_d", 4), width=0.5, edgecolor="white")
    ax.yaxis.set_major_formatter(INR)
    ax.set_title("Quarterly Spending Comparison"); ax.set_ylabel("Amount (Rs)")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                f"Rs {bar.get_height():,.0f}", ha="center", fontsize=9)
    _save("08_quarterly")


def run_all_charts(df):
    print("\n-- Generating charts --")
    chart_category_bar(df)
    chart_category_pie(df)
    chart_monthly_trend(df)
    chart_payment_methods(df)
    chart_heatmap(df)
    chart_weekend_vs_weekday(df)
    chart_top_expenses(df)
    chart_quarterly(df)
    print("[OK] All 8 charts saved to outputs/charts/")


if __name__ == "__main__":
    import sys; sys.path.insert(0, "src")
    from clean_data import load_data, clean, add_features
    df = load_data(); df = clean(df); df = add_features(df)
    run_all_charts(df)

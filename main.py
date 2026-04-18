"""
main.py  —  Run Full Pipeline
Usage: python main.py
"""
import sys, os
sys.path.insert(0, "src")

from generate_data import generate_expenses, save_dataset
from clean_data    import load_data, clean, add_features, save_clean
from analyze       import load_clean, category_summary, monthly_trend, \
                          top_expenses, weekend_vs_weekday, quarterly_summary, \
                          generate_insights, save_insights
from visualize     import run_all_charts


def main():
    print("=" * 56)
    print("   EXPENSE TRACKER — Data Science Pipeline")
    print("=" * 56)

    print("\n[Phase 1] Generating synthetic data...")
    df_raw = generate_expenses(n_records=600, year=2024)
    save_dataset(df_raw)

    print("\n[Phase 2] Cleaning & feature engineering...")
    df = load_data()
    df = clean(df)
    df = add_features(df)
    save_clean(df)

    print("\n[Phase 3] Running analysis...")
    df = load_clean()
    print("\n  Category Summary:")
    print(category_summary(df).to_string())
    print("\n  Top 10 Expenses:")
    print(top_expenses(df, 10).to_string(index=False))

    print("\n[Phase 4] Generating insights...")
    insights = generate_insights(df)
    for line in insights:
        print("  *", line)
    save_insights(insights)

    print("\n[Phase 5] Generating visualizations...")
    run_all_charts(df)

    print("\n" + "=" * 56)
    print("   COMPLETE! Run: streamlit run app.py")
    print("=" * 56)


if __name__ == "__main__":
    main()

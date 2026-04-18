"""
app.py  —  Expense Tracker Dashboard
Run: streamlit run app.py
Requires: streamlit pandas numpy matplotlib seaborn
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import os, sys

sys.path.insert(0, "src")

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #f8f9fc; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .kpi-card {
        background: white; border-radius: 16px; padding: 18px 20px;
        border-left: 5px solid; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 8px;
    }
    .kpi-card.blue  { border-color: #4361ee; }
    .kpi-card.green { border-color: #06d6a0; }
    .kpi-card.amber { border-color: #f77f00; }
    .kpi-card.red   { border-color: #ef233c; }
    .kpi-label { font-size: 12px; color: #718096; font-weight: 500; margin-bottom: 4px; }
    .kpi-value { font-size: 22px; font-weight: 700; color: #1a202c; line-height: 1.1; }
    .kpi-sub   { font-size: 11px; color: #a0aec0; margin-top: 4px; }
    .section-title {
        font-size: 17px; font-weight: 700; color: #1a202c;
        padding: 6px 0 4px; border-bottom: 2px solid #e2e8f0; margin-bottom: 14px;
    }
    .insight-card {
        background: white; border-radius: 12px; padding: 12px 16px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06); margin-bottom: 10px;
        border-left: 4px solid #4361ee; font-size: 14px; color: #2d3748;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 6px 18px; background: #edf2f7; font-size: 14px;
    }
    .stTabs [aria-selected="true"] { background: #4361ee !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "figure.dpi": 120, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})
INR = mticker.FuncFormatter(lambda x, _: f"Rs {x:,.0f}")

COLORS = {
    "Food & Dining": "#4361ee", "Rent": "#7209b7", "Transportation": "#06d6a0",
    "Entertainment": "#f77f00", "Utilities": "#3a86ff", "Healthcare": "#ef233c",
    "Shopping": "#fb8500", "Education": "#8338ec", "Travel": "#2dc653",
    "Miscellaneous": "#adb5bd",
}
MONTH_LABELS = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
BUDGET_DEFAULT = {
    "Food & Dining": 25000, "Rent": 150000, "Transportation": 10000,
    "Entertainment": 8000, "Utilities": 5000, "Healthcare": 5000,
    "Shopping": 10000, "Education": 12000, "Travel": 12000, "Miscellaneous": 5000,
}


@st.cache_data
def load_data():
    path = "data/processed/expenses_clean.csv"
    if not os.path.exists(path):
        from generate_data import generate_expenses, save_dataset
        from clean_data import load_data as ld, clean, add_features, save_clean
        df_raw = generate_expenses(600, 2024)
        save_dataset(df_raw)
        df = ld(); df = clean(df); df = add_features(df); save_clean(df)
    return pd.read_csv(path, parse_dates=["date"])

df_all = load_data()

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💸 Expense Tracker")
    st.markdown("*Data Science Project 2024*")
    st.markdown("---")
    st.markdown("### Filters")
    sel_cat = st.multiselect("Categories", sorted(df_all["category"].unique()),
                              default=sorted(df_all["category"].unique()))
    sel_mon = st.multiselect("Months", list(range(1, 13)), default=list(range(1, 13)),
                              format_func=lambda m: MONTH_LABELS[m])
    sel_pay = st.multiselect("Payment Methods", sorted(df_all["payment_method"].unique()),
                              default=sorted(df_all["payment_method"].unique()))
    st.markdown("---")
    st.markdown("### Annual Budget (Rs)")
    custom_budget = {}
    for cat in sorted(BUDGET_DEFAULT.keys()):
        custom_budget[cat] = st.number_input(cat, min_value=0,
                                              value=BUDGET_DEFAULT[cat], step=1000)
    st.markdown("---")
    st.caption("Python · Pandas · Matplotlib · Streamlit")

df = df_all[
    df_all["category"].isin(sel_cat) &
    df_all["month"].isin(sel_mon) &
    df_all["payment_method"].isin(sel_pay)
].copy()

if df.empty:
    st.warning("No data for current filters."); st.stop()

# ─── Header ────────────────────────────────────────────────────
st.markdown("""
<div style='padding:12px 0 8px'>
  <h1 style='font-size:30px;font-weight:800;color:#1a202c;margin:0'>
    💸 Personal Expense Dashboard
  </h1>
  <p style='color:#718096;font-size:14px;margin:4px 0 0'>
    Synthetic Financial Data &nbsp;|&nbsp; Year 2024 &nbsp;|&nbsp; Python &amp; Streamlit
  </p>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ─── KPIs ──────────────────────────────────────────────────────
total       = df["amount"].sum()
avg_txn     = df["amount"].mean()
monthly_avg = df.groupby("month")["amount"].sum().mean()
max_exp     = df["amount"].max()
top_cat     = df.groupby("category")["amount"].sum().idxmax()
top_pay     = df["payment_method"].value_counts().idxmax()

def kpi(col, cls, label, value, sub=""):
    col.markdown(f"""
    <div class="kpi-card {cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6 = st.columns(6)
kpi(c1,"blue",  "Total Spend",     f"Rs {total:,.0f}",      f"{len(df)} transactions")
kpi(c2,"green", "Monthly Avg",      f"Rs {monthly_avg:,.0f}","per month")
kpi(c3,"amber", "Avg Transaction",  f"Rs {avg_txn:,.0f}",   "per expense")
kpi(c4,"red",   "Highest Expense",  f"Rs {max_exp:,.0f}",   "single txn")
kpi(c5,"blue",  "Top Category",    top_cat,                  "most spending")
kpi(c6,"green", "Top Payment",     top_pay,                  "most used")
st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────



# Custom CSS for dark/deep tab text styling
st.markdown("""
<style>

/* Tab container */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

/* Individual tabs */
.stTabs [data-baseweb="tab"] {
    background-color: #1a1a1a;
    color: #e0e0e0;
    padding: 10px 22px;
    border-radius: 10px 10px 0px 0px;
    font-weight: 700;
    font-size: 16px;
    border: 1px solid #333333;
}

/* Selected tab */
.stTabs [aria-selected="true"] {
    background-color: #000000;
    color: #00ffcc;
    border-bottom: 2px solid #00ffcc;
}

/* Hover effect */
.stTabs [data-baseweb="tab"]:hover {
    background-color: #111111;
    color: #ffffff;
}

</style>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "📊 Overview", "📅 Trends", "🔥 Deep Dive", "💰 Budget", "📋 Transactions"
])

# ══════════════════ TAB 1: OVERVIEW ════════════════════════════
with tab1:
    cL, cR = st.columns([1.3, 1])

    with cL:
        st.markdown('<div class="section-title">Category-wise Total Spending</div>',
                    unsafe_allow_html=True)
        cat = df.groupby("category")["amount"].sum().sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(7, 4.5))
        bars = ax.barh(cat.index, cat.values,
                       color=[COLORS.get(c,"#adb5bd") for c in cat.index],
                       edgecolor="white", height=0.6)
        ax.xaxis.set_major_formatter(INR)
        for b in bars:
            ax.text(b.get_width() + total*0.004, b.get_y()+b.get_height()/2,
                    f"Rs {b.get_width():,.0f}", va="center", fontsize=7.5)
        ax.set_xlim(0, cat.max()*1.25)
        ax.set_title("Category Spending")
        plt.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close()

    with cR:
        st.markdown('<div class="section-title">Spending Share (Donut)</div>',
                    unsafe_allow_html=True)
        cat_pie = df.groupby("category")["amount"].sum()
        fig2, ax2 = plt.subplots(figsize=(5.5, 5))
        wedges, _, autotexts = ax2.pie(
            cat_pie.values, labels=None, autopct="%1.0f%%", startangle=140,
            colors=[COLORS.get(c,"#adb5bd") for c in cat_pie.index],
            pctdistance=0.75, wedgeprops=dict(width=0.58))
        for t in autotexts: t.set_fontsize(7.5)
        ax2.legend(wedges, cat_pie.index, loc="center left",
                   bbox_to_anchor=(1, 0.5), fontsize=8, frameon=False)
        ax2.set_title("Spending Distribution", pad=12)
        plt.tight_layout(); st.pyplot(fig2, use_container_width=True); plt.close()

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="section-title">Payment Method</div>', unsafe_allow_html=True)
        pm = df.groupby("payment_method")["amount"].sum().sort_values()
        fig3, ax3 = plt.subplots(figsize=(5.5, 3.5))
        ax3.barh(pm.index, pm.values, color=sns.color_palette("Set2", len(pm)), height=0.5)
        ax3.xaxis.set_major_formatter(INR)
        ax3.set_title("By Payment Method")
        plt.tight_layout(); st.pyplot(fig3, use_container_width=True); plt.close()

    with cb:
        st.markdown('<div class="section-title">Weekend vs Weekday</div>', unsafe_allow_html=True)
        wk = df.groupby("is_weekend")["amount"].sum()
        wk.index = ["Weekday","Weekend"]
        fig4, ax4 = plt.subplots(figsize=(5.5, 3.5))
        bars4 = ax4.bar(wk.index, wk.values, color=["#4361ee","#f77f00"],
                        width=0.4, edgecolor="white")
        ax4.yaxis.set_major_formatter(INR)
        ax4.set_title("Weekday vs Weekend")
        for b in bars4:
            ax4.text(b.get_x()+b.get_width()/2, b.get_height()+total*0.005,
                     f"Rs {b.get_height():,.0f}", ha="center", fontsize=9, fontweight="bold")
        plt.tight_layout(); st.pyplot(fig4, use_container_width=True); plt.close()

# ══════════════════ TAB 2: TRENDS ══════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Monthly Spending Trend</div>',
                unsafe_allow_html=True)
    monthly = df.groupby(["month","month_name"])["amount"].sum().reset_index().sort_values("month")
    monthly["rolling"] = monthly["amount"].rolling(3, center=True).mean()
    mlbls = [MONTH_LABELS[m] for m in monthly["month"]]
    fig5, ax5 = plt.subplots(figsize=(12, 4.5))
    ax5.plot(mlbls, monthly["amount"], marker="o", lw=2.5, color="#4361ee",
             markersize=8, label="Monthly Spend")
    ax5.fill_between(mlbls, monthly["amount"], alpha=0.1, color="#4361ee")
    ax5.plot(mlbls, monthly["rolling"], lw=2, color="#f77f00",
             linestyle="--", label="3-Month Avg")
    for x, y in zip(mlbls, monthly["amount"]):
        ax5.text(x, y + total*0.002, f"Rs {y/1000:.0f}K", ha="center", fontsize=8)
    ax5.yaxis.set_major_formatter(INR); ax5.set_title("Monthly Spending Trend")
    ax5.legend(fontsize=9)
    plt.tight_layout(); st.pyplot(fig5, use_container_width=True); plt.close()

    st.markdown('<div class="section-title">Category Breakdown by Month (Stacked)</div>',
                unsafe_allow_html=True)
    cat_month = df.pivot_table(values="amount", index="category",
                               columns="month", aggfunc="sum", fill_value=0)
    cat_month.columns = [MONTH_LABELS[c] for c in cat_month.columns]
    fig6, ax6 = plt.subplots(figsize=(12, 5))
    bottom = np.zeros(cat_month.shape[1])
    for cn in cat_month.index:
        vals = cat_month.loc[cn].values
        ax6.bar(cat_month.columns, vals, bottom=bottom,
                color=COLORS.get(cn,"#adb5bd"), label=cn, width=0.7, edgecolor="white")
        bottom += vals
    ax6.yaxis.set_major_formatter(INR)
    ax6.set_title("Category x Month Stacked Spending")
    ax6.legend(loc="upper right", fontsize=8, frameon=False, ncol=2)
    plt.tight_layout(); st.pyplot(fig6, use_container_width=True); plt.close()

    st.markdown('<div class="section-title">Quarterly Overview</div>', unsafe_allow_html=True)
    q_data = df.groupby("quarter")["amount"].sum()
    q_clrs = ["#4361ee","#7209b7","#06d6a0","#f77f00"]
    qcols = st.columns(4)
    for i, q in enumerate(q_data.index):
        top_q = df[df["quarter"]==q]["category"].value_counts().idxmax()
        qcols[i].markdown(f"""
        <div class="kpi-card" style="border-left-color:{q_clrs[i]}">
            <div class="kpi-label">Q{q} Spending</div>
            <div class="kpi-value">Rs {q_data[q]:,.0f}</div>
            <div class="kpi-sub">{top_q} tops</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════ TAB 3: DEEP DIVE ═══════════════════════════
with tab3:
    st.markdown('<div class="section-title">Category x Month Heatmap</div>',
                unsafe_allow_html=True)
    pivot = df.pivot_table(values="amount", index="category",
                           columns="month", aggfunc="sum", fill_value=0)
    pivot.columns = [MONTH_LABELS[c] for c in pivot.columns]
    fig7, ax7 = plt.subplots(figsize=(13, 5.5))
    sns.heatmap(pivot, ax=ax7, cmap="YlOrRd", fmt=".0f",
                linewidths=0.4, linecolor="white", cbar_kws={"label":"Amount (Rs)","shrink":0.8})
    ax7.set_title("Category x Month Heatmap"); ax7.set_xlabel(""); ax7.set_ylabel("")
    plt.tight_layout(); st.pyplot(fig7, use_container_width=True); plt.close()

    cl3, cr3 = st.columns(2)
    with cl3:
        st.markdown('<div class="section-title">Top 10 Highest Expenses</div>',
                    unsafe_allow_html=True)
        top10 = df.nlargest(10, "amount").copy()
        top10["label"] = top10["description"].str[:20] + " (" + top10["category"].str[:8] + ")"
        fig8, ax8 = plt.subplots(figsize=(6.5, 5))
        ax8.barh(top10["label"].values[::-1], top10["amount"].values[::-1],
                 color=[COLORS.get(c,"#adb5bd") for c in top10["category"].values[::-1]],
                 edgecolor="white", height=0.65)
        ax8.xaxis.set_major_formatter(INR); ax8.set_title("Top 10 Highest Expenses")
        plt.tight_layout(); st.pyplot(fig8, use_container_width=True); plt.close()

    with cr3:
        st.markdown('<div class="section-title">Day of Week Pattern</div>',
                    unsafe_allow_html=True)
        day_ord = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("day_of_week")["amount"].agg(["sum","mean"]).reindex(day_ord).reset_index()
        fig9, ax9 = plt.subplots(figsize=(6.5, 5))
        ax9b = ax9.twinx()
        ax9.bar(dow["day_of_week"], dow["sum"], color="#4361ee", alpha=0.8, width=0.5)
        ax9b.plot(dow["day_of_week"], dow["mean"], marker="o", color="#f77f00", lw=2, markersize=6)
        ax9.yaxis.set_major_formatter(INR); ax9b.yaxis.set_major_formatter(INR)
        ax9.set_title("Day-of-Week Spending"); ax9.set_ylabel("Total (Rs)"); ax9b.set_ylabel("Avg (Rs)")
        plt.xticks(rotation=30, ha="right")
        handles = [mpatches.Patch(color="#4361ee", label="Total"),
                   mpatches.Patch(color="#f77f00", label="Avg")]
        ax9.legend(handles=handles, fontsize=8)
        plt.tight_layout(); st.pyplot(fig9, use_container_width=True); plt.close()

    st.markdown('<div class="section-title">Auto-Generated Insights</div>', unsafe_allow_html=True)
    from analyze import generate_insights
    insights = generate_insights(df)
    icons = ["💰","🏆","📅","📊","💳","📆","📉","🔢"]
    ins_cols = st.columns(2)
    for i, line in enumerate(insights):
        with ins_cols[i % 2]:
            st.markdown(f"""
            <div class="insight-card">
                <span style="font-size:18px;margin-right:8px;">{icons[i%len(icons)]}</span>{line}
            </div>""", unsafe_allow_html=True)

# ══════════════════ TAB 4: BUDGET ══════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Budget vs Actual — Progress</div>',
                unsafe_allow_html=True)
    cat_totals = df.groupby("category")["amount"].sum()
    bdf = pd.DataFrame({"actual": cat_totals, "budget": pd.Series(custom_budget)}).dropna()
    bdf.index.name = "category"
    bdf["pct"]  = (bdf["actual"] / bdf["budget"] * 100).round(1)
    bdf["diff"] = (bdf["actual"] - bdf["budget"]).round(0)

    for cn, row in bdf.sort_values("pct", ascending=False).iterrows():
        pct = min(row["pct"], 100)
        bc  = "#ef233c" if row["pct"]>100 else ("#f77f00" if row["pct"]>80 else "#06d6a0")
        sc  = "#ef233c" if row["diff"]>0 else "#06d6a0"
        st_ = "Over Budget" if row["diff"]>0 else "Within Budget"
        dtxt = f"Over Rs {row['diff']:,.0f}" if row["diff"]>0 else f"Saved Rs {-row['diff']:,.0f}"
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:14px 20px;
                    box-shadow:0 1px 8px rgba(0,0,0,0.06);margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px">
            <span style="font-weight:600;font-size:14px;color:#1a202c">{cn}</span>
            <span style="font-size:13px;color:{sc};font-weight:600">{st_} ({row['pct']:.0f}%)</span>
          </div>
          <div style="background:#edf2f7;border-radius:8px;height:10px">
            <div style="background:{bc};width:{pct}%;height:10px;border-radius:8px"></div>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:12px;color:#718096">
            <span>Actual: Rs {row['actual']:,.0f}</span>
            <span>Budget: Rs {row['budget']:,.0f}</span>
            <span>{dtxt}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Budget vs Actual Chart</div>', unsafe_allow_html=True)
    bdf_r = bdf.reset_index()
    x = np.arange(len(bdf_r)); w = 0.38
    figb, axb = plt.subplots(figsize=(12, 5))
    axb.bar(x-w/2, bdf_r["actual"], w, label="Actual", color="#4361ee", edgecolor="white")
    axb.bar(x+w/2, bdf_r["budget"], w, label="Budget", color="#e2e8f0", edgecolor="#cbd5e0")
    axb.set_xticks(x); axb.set_xticklabels(bdf_r["category"], rotation=30, ha="right")
    axb.yaxis.set_major_formatter(INR); axb.set_title("Actual vs Budget by Category")
    axb.legend(fontsize=10); axb.yaxis.grid(True, alpha=0.4); axb.set_axisbelow(True)
    plt.tight_layout(); st.pyplot(figb, use_container_width=True); plt.close()

# ══════════════════ TAB 5: TRANSACTIONS ════════════════════════
with tab5:
    st.markdown('<div class="section-title">Transaction Log</div>', unsafe_allow_html=True)
    search = st.text_input("🔍 Search", placeholder="e.g. Swiggy, Travel, Rent…")
    ts1, ts2 = st.columns(2)
    with ts1: sc_ = st.selectbox("Sort by", ["date","amount","category"], index=1)
    with ts2: asc = st.radio("Order", ["Descending","Ascending"], horizontal=True)=="Ascending"

    txn = df[["date","category","amount","payment_method","description"]].copy()
    txn["date"] = txn["date"].dt.strftime("%Y-%m-%d")
    if search:
        mask = (txn["description"].str.contains(search, case=False, na=False) |
                txn["category"].str.contains(search, case=False, na=False))
        txn = txn[mask]
    txn = txn.sort_values(sc_, ascending=asc).reset_index(drop=True)
    txn["amount"] = txn["amount"].apply(lambda x: f"Rs {x:,.2f}")
    txn.columns = ["Date","Category","Amount","Payment Method","Description"]

    st.dataframe(txn, use_container_width=True, height=420)
    st.markdown(f"**Showing {len(txn)} transactions**")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Dataset as CSV", csv,
                       "expenses_2024.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#a0aec0;font-size:13px;padding:10px 0'>
  Built with Python · Pandas · Matplotlib · Seaborn · Streamlit &nbsp;|&nbsp;
  Expense Tracker Data Science Project &nbsp;|&nbsp; 2024 Synthetic Data
</div>""", unsafe_allow_html=True)

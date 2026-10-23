"""Analyze a synthetic retail sales dataset and produce KPIs and charts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "retail_sales_raw.csv"
OUTPUT_DIR = ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

REQUIRED_COLUMNS = [
    "order_id", "order_date", "region", "category", "product",
    "quantity", "unit_price_inr", "discount_pct",
    "payment_method", "customer_type",
]


def load_and_clean(path: Path) -> tuple[pd.DataFrame, dict]:
    """Load raw CSV, validate expected columns, and clean invalid records."""
    raw = pd.read_csv(path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(raw.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    initial_rows = len(raw)
    df = raw.copy()

    text_columns = [
        "order_id", "region", "category", "product",
        "payment_method", "customer_type",
    ]
    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for column in ["quantity", "unit_price_inr", "discount_pct"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Rows must contain core order and sales fields to be analyzed.
    required_for_analysis = [
        "order_id", "order_date", "category", "product",
        "quantity", "unit_price_inr", "discount_pct",
    ]
    df = df.dropna(subset=required_for_analysis)
    after_required_fields = len(df)

    df = df[
        (df["quantity"] >= 1)
        & (df["unit_price_inr"] >= 0)
        & (df["discount_pct"].between(0, 1))
    ].copy()
    after_valid_values = len(df)

    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    final_rows = len(df)

    # Region/payment/customer type are not required for revenue calculation;
    # label missing optional dimensions explicitly instead of dropping sales.
    for column in ["region", "payment_method", "customer_type"]:
        df[column] = df[column].fillna("Unknown")

    df["gross_sales_inr"] = df["quantity"] * df["unit_price_inr"]
    df["discount_amount_inr"] = df["gross_sales_inr"] * df["discount_pct"]
    df["net_sales_inr"] = df["gross_sales_inr"] - df["discount_amount_inr"]
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    audit = {
        "input_rows": int(initial_rows),
        "rows_after_required_field_check": int(after_required_fields),
        "rows_after_valid_value_check": int(after_valid_values),
        "duplicate_order_ids_removed": int(after_valid_values - final_rows),
        "final_rows": int(final_rows),
        "rows_removed_total": int(initial_rows - final_rows),
    }
    return df, audit


def save_bar_chart(series: pd.Series, title: str, ylabel: str, path: Path,
                   horizontal: bool = False) -> None:
    """Save a readable bar chart from a sorted pandas Series."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    if horizontal:
        series.sort_values().plot(kind="barh", ax=ax)
    else:
        series.plot(kind="bar", ax=ax)
        ax.tick_params(axis="x", rotation=25)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.grid(axis="x" if horizontal else "y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sales, audit = load_and_clean(INPUT_FILE)

    total_net_sales = float(sales["net_sales_inr"].sum())
    total_gross_sales = float(sales["gross_sales_inr"].sum())
    total_discount = float(sales["discount_amount_inr"].sum())
    order_count = int(sales["order_id"].nunique())
    units_sold = int(sales["quantity"].sum())

    kpis = {
        "dataset_type": "synthetic",
        "currency": "INR",
        "orders": order_count,
        "units_sold": units_sold,
        "gross_sales_inr": round(total_gross_sales, 2),
        "discount_amount_inr": round(total_discount, 2),
        "net_sales_inr": round(total_net_sales, 2),
        "average_order_value_inr": round(total_net_sales / order_count, 2)
        if order_count else 0,
        "average_discount_pct": round(float(sales["discount_pct"].mean() * 100), 2),
        "cleaning_audit": audit,
    }

    category_sales = sales.groupby("category")["net_sales_inr"].sum().sort_values(ascending=False)
    region_sales = sales.groupby("region")["net_sales_inr"].sum().sort_values(ascending=False)
    monthly_sales = sales.groupby("month")["net_sales_inr"].sum().sort_index()
    customer_aov = sales.groupby("customer_type")["net_sales_inr"].mean().sort_values(ascending=False)
    payment_mix = sales["payment_method"].value_counts()

    kpis["top_category_by_net_sales"] = str(category_sales.index[0]) if len(category_sales) else None
    kpis["top_region_by_net_sales"] = str(region_sales.index[0]) if len(region_sales) else None
    kpis["highest_average_order_value_customer_type"] = str(customer_aov.index[0]) if len(customer_aov) else None

    with (OUTPUT_DIR / "kpi_summary.json").open("w", encoding="utf-8") as file:
        json.dump(kpis, file, indent=2)

    save_bar_chart(
        category_sales, "Net Sales by Product Category", "Net sales (INR)",
        FIGURE_DIR / "sales_by_category.png", horizontal=True
    )
    save_bar_chart(
        region_sales, "Net Sales by Region", "Net sales (INR)",
        FIGURE_DIR / "sales_by_region.png", horizontal=True
    )

    fig, ax = plt.subplots(figsize=(10, 5.5))
    monthly_sales.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Monthly Net Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Net sales (INR)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "monthly_sales_trend.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    save_bar_chart(
        customer_aov, "Average Order Value by Customer Type", "Average order value (INR)",
        FIGURE_DIR / "average_order_value_by_customer_type.png"
    )
    save_bar_chart(
        payment_mix, "Orders by Payment Method", "Number of orders",
        FIGURE_DIR / "orders_by_payment_method.png"
    )

    print("\n=== RETAIL SALES ANALYSIS ===")
    print(f"Orders analyzed:       {order_count:,}")
    print(f"Units sold:            {units_sold:,}")
    print(f"Gross sales:           ₹{total_gross_sales:,.2f}")
    print(f"Discounts:             ₹{total_discount:,.2f}")
    print(f"Net sales:             ₹{total_net_sales:,.2f}")
    print(f"Average order value:   ₹{kpis['average_order_value_inr']:,.2f}")
    print(f"Top category:          {kpis['top_category_by_net_sales']}")
    print(f"Top region:            {kpis['top_region_by_net_sales']}")
    print(f"Rows removed:          {audit['rows_removed_total']:,}")
    print(f"\nOutputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

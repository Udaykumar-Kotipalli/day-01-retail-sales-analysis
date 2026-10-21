# Day 1 — Retail Sales Analysis (Python)

An original, beginner-friendly data analytics project that cleans a retail dataset, calculates sales KPIs, explores category/region/monthly performance, and turns results into practical business recommendations.

> **Dataset note:** `data/retail_sales_raw.csv` is a synthetic dataset generated specifically for this portfolio project. It is not real company data and should not be presented as real-world business evidence.

## Business question

What can a small retailer learn from its order-level sales data about revenue, product categories, regions, discounts, and customer mix?

## Objectives

- Inspect and clean missing or invalid values.
- Calculate revenue after discounts.
- Summarize revenue, orders, units, and average order value (AOV).
- Compare category, region, monthly, and customer-type performance.
- Generate clear charts and a machine-readable KPI summary.
- Document limitations and recommendations without overstating what synthetic data proves.

## Tools

- Python 3.10+
- pandas
- numpy
- matplotlib

## Repository structure

```text
day-01-retail-sales-analysis/
├── data/
│   └── retail_sales_raw.csv
├── outputs/
│   ├── figures/
│   └── kpi_summary.json
├── src/
│   └── analyze_sales.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Run locally

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies and run:
```bash
pip install -r requirements.txt
python src/analyze_sales.py
```

The script reads `data/retail_sales_raw.csv`, cleans the data, prints a KPI summary, writes `outputs/kpi_summary.json`, and saves charts in `outputs/figures/`.

## Metric definitions

- **Gross sales:** `quantity × unit_price_inr`, before discount.
- **Net sales:** gross sales minus the order-level discount.
- **Average order value:** total net sales divided by the number of valid orders.
- **Orders:** count of unique order IDs.
- **Units sold:** sum of quantity for valid rows.

## Data cleaning rules

1. Trim whitespace in text fields.
2. Parse order dates and numeric fields.
3. Drop rows missing required fields (`order_id`, `order_date`, `category`, `product`, `quantity`, `unit_price_inr`, `discount_pct`).
4. Remove rows with quantity less than 1 or negative prices.
5. Keep discount values between 0 and 1 inclusive.
6. Deduplicate on `order_id`.

The raw file is preserved; cleaning is performed in memory so the original input remains unchanged.

## Analysis questions

1. Which product categories contribute the most net sales?
2. Which regions contribute the most net sales?
3. How does net sales change month to month?
4. How does customer type relate to order value?
5. What share of orders use each payment method?

## Results

Run the analysis script to generate the results for this dataset. Because this is synthetic data, results demonstrate the workflow rather than real market behavior.

## Limitations

- Synthetic data cannot validate real customer behavior or business performance.
- There is no cost or margin data, so **profit cannot be calculated**.
- There are no customer IDs, so repeat-purchase frequency and customer lifetime value cannot be measured.
- The data is generated for a portfolio exercise; conclusions should not be generalized to a real retailer.

## Future improvements

- Add unit costs and analyze profit/margins.
- Add customer IDs for cohort and retention analysis.
- Build a SQL version of the same questions.
- Add automated data validation tests.

## Author

Add your GitHub profile and contact details here.

## Generated sample results

After running the script on the included synthetic dataset:

- Orders analyzed: **1,198**
- Units sold: **2,619**
- Gross sales: **₹3,479,901.54**
- Discounts: **₹241,137.48**
- Net sales: **₹3,238,764.06**
- Average order value: **₹2,703.48**
- Highest net-sales category: **Electronics**
- Highest net-sales region: **South**

These are outputs from a deterministic synthetic dataset, not real business results.

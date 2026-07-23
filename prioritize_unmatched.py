import pandas as pd

missing = pd.read_csv("cusips_needing_manual_patch.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")

value_by_cusip = holdings.groupby("cusip")["value"].sum().reset_index()
value_by_cusip = value_by_cusip.rename(columns={"value": "total_value_across_filings"})

missing_ranked = missing.merge(value_by_cusip, on="cusip", how="left")
missing_ranked = missing_ranked.sort_values("total_value_across_filings", ascending=False)

missing_ranked.to_csv("cusips_needing_manual_patch.csv", index=False)

print(missing_ranked.head(20).to_string(index=False))
print(f"\nTotal value across all 148 unresolved CUSIPs: ${missing_ranked['total_value_across_filings'].sum():,.0f}")

total_portfolio_value = holdings["value"].sum()
pct = missing_ranked['total_value_across_filings'].sum() / total_portfolio_value * 100
print(f"That's {pct:.2f}% of total portfolio value across all managers/quarters")

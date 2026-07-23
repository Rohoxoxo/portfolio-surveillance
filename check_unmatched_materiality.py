import pandas as pd

holdings = pd.read_csv("raw_13f_holdings.csv")
missing = pd.read_csv("cusips_needing_manual_patch.csv")

total_portfolio_value = holdings["value"].sum()

missing_values = holdings[holdings["cusip"].isin(missing["cusip"])].groupby("cusip").agg(
    security_name=("security_name", "first"),
    total_value=("value", "sum"),
).reset_index()

missing_values["pct_of_total_portfolio"] = missing_values["total_value"] / total_portfolio_value * 100
missing_values = missing_values.sort_values("total_value", ascending=False)

print(f"Total portfolio value across all holdings: ${total_portfolio_value:,.0f}")
print(f"Combined value of all {len(missing_values)} unresolved CUSIPs: ${missing_values['total_value'].sum():,.0f} ({missing_values['total_value'].sum() / total_portfolio_value * 100:.3f}% of total)")
print()
print("Top 20 unresolved CUSIPs by dollar value:")
print(missing_values.head(20).to_string(index=False))

missing_values.to_csv("unmatched_cusips_by_materiality.csv", index=False)
print("\nSaved full ranked list to unmatched_cusips_by_materiality.csv")

import pandas as pd

old_mapping = pd.read_csv("cusip_ticker_map.csv")
new_mapping = pd.read_csv("cusip_ticker_map_new_batch.csv")
cusip_map = pd.concat([old_mapping, new_mapping], ignore_index=True)

sectors = pd.read_csv("ticker_sector_map.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")

final = cusip_map.merge(sectors[["ticker", "sector", "industry"]], on="ticker", how="left")
final["sector"] = final["sector"].fillna("Unclassified")
final["industry"] = final["industry"].fillna("Unclassified")
final.to_csv("cusip_ticker_sector_map.csv", index=False)

value_by_cusip = holdings.groupby("cusip")["value"].sum().reset_index()
unresolved = final[final["sector"] == "Unclassified"].merge(value_by_cusip, on="cusip", how="left")

total_portfolio_value = holdings["value"].sum()
unresolved_value_pct = unresolved["value"].sum() / total_portfolio_value * 100

unresolved["reason"] = f"Sector unresolved via yfinance (Yahoo Finance has no profile data for this ticker); immaterial value (~{unresolved_value_pct:.2f}% of total portfolio) — tagged Unclassified rather than hand-researched further"
unresolved = unresolved.sort_values("value", ascending=False)
unresolved.to_csv("sector_exclusions.csv", index=False)

print(f"Final mapping table: {len(final)} rows -> cusip_ticker_sector_map.csv")
print(f"Sector breakdown:")
print(final["sector"].value_counts().head(15))
print(f"\nDocumented sector exclusions: {len(unresolved)} -> sector_exclusions.csv ({unresolved_value_pct:.2f}% of total portfolio value)")

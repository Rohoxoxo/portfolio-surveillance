import pandas as pd

sectors = pd.read_csv("ticker_sector_map.csv")
cusip_map = pd.read_csv("cusip_ticker_map.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")

unmatched_tickers = sectors[sectors["matched"] == False]["ticker"].tolist()

value_by_cusip = holdings.groupby("cusip")["value"].sum().reset_index()
cusip_with_value = cusip_map.merge(value_by_cusip, on="cusip", how="left")

unmatched_value = cusip_with_value[cusip_with_value["ticker"].isin(unmatched_tickers)]
value_by_ticker = unmatched_value.groupby(["ticker", "company_name"])["value"].sum().reset_index()
value_by_ticker = value_by_ticker.sort_values("value", ascending=False)

value_by_ticker.to_csv("unmatched_sectors_ranked.csv", index=False)

print(value_by_ticker.head(20).to_string(index=False))
total_unmatched_value = value_by_ticker["value"].sum()
total_portfolio_value = holdings["value"].sum()
print(f"\nTotal value of unmatched-sector tickers: ${total_unmatched_value:,.0f}")
print(f"That's {total_unmatched_value / total_portfolio_value * 100:.2f}% of total portfolio value")

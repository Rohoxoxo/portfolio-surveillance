import pandas as pd

failed = pd.read_csv("security_prices_failed_tickers.csv")
sector_map = pd.read_csv("cusip_ticker_sector_map.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")

value_by_cusip = holdings.groupby("cusip")["value"].sum().reset_index()
map_with_value = sector_map.merge(value_by_cusip, on="cusip", how="left")

failed_value = map_with_value[map_with_value["ticker"].isin(failed["ticker"])]
total_failed_value = failed_value["value"].sum()
total_portfolio_value = holdings["value"].sum()

print(f"Remaining failed tickers: {len(failed)}")
print(f"Total value represented: ${total_failed_value:,.0f}")
print(f"That's {total_failed_value / total_portfolio_value * 100:.2f}% of total portfolio value")

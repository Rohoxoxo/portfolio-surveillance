import pandas as pd

failed = pd.read_csv("security_prices_failed_tickers.csv")
sector_map = pd.read_csv("cusip_ticker_sector_map.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")

value_by_cusip = holdings.groupby("cusip")["value"].sum().reset_index()
map_with_value = sector_map.merge(value_by_cusip, on="cusip", how="left")

total_portfolio_value = holdings["value"].sum()
price_exclusions = map_with_value[map_with_value["ticker"].isin(failed["ticker"])].copy()

excluded_value_pct = price_exclusions["value"].sum() / total_portfolio_value * 100
price_exclusions["reason"] = f"No price history available via yfinance (delisted, foreign-listing ticker mismatch, or thinly-traded); {excluded_value_pct:.2f}% of total portfolio value — excluded from price analysis"
price_exclusions = price_exclusions.sort_values("value", ascending=False)
price_exclusions.to_csv("price_exclusions.csv", index=False)

total_tickers = sector_map["ticker"].nunique()
covered_tickers = total_tickers - failed["ticker"].nunique()

print(f"Documented {len(price_exclusions)} price exclusions -> price_exclusions.csv")
print(f"security_prices.csv covers {covered_tickers} / {total_tickers} tickers ({covered_tickers / total_tickers:.1%})")

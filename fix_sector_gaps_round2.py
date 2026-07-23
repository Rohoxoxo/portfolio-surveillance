import pandas as pd

old_mapping = pd.read_csv("cusip_ticker_map.csv")
new_mapping = pd.read_csv("cusip_ticker_map_new_batch.csv")
cusip_map = pd.concat([old_mapping, new_mapping], ignore_index=True)

sectors = pd.read_csv("ticker_sector_map.csv")

fund_keywords = ["ETF", "TRUST", "ISHARES", "SPDR", " FUND", "VANGUARD"]
name_by_ticker = cusip_map[["ticker", "company_name"]].drop_duplicates(subset="ticker")
is_fund = name_by_ticker["company_name"].fillna("").str.upper().apply(
    lambda n: any(k in n for k in fund_keywords)
)
fund_tickers = set(name_by_ticker[is_fund]["ticker"])

already_fund_tagged = set(sectors[sectors["sector"] == "Fund"]["ticker"])
newly_found_funds = fund_tickers - already_fund_tagged

sectors = sectors[~sectors["ticker"].isin(newly_found_funds)]
fund_rows = pd.DataFrame([
    {"ticker": t, "sector": "Fund", "industry": "Exchange Traded Fund", "matched": True}
    for t in newly_found_funds
])
sectors = pd.concat([sectors, fund_rows], ignore_index=True)
sectors.to_csv("ticker_sector_map.csv", index=False)

print(f"Newly tagged as Fund (round 2, VANGUARD keyword): {len(newly_found_funds)}")
print(f"Total resolved now: {sectors['matched'].sum()} / {len(sectors)}")

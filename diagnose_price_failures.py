import pandas as pd

sector_map = pd.read_csv("cusip_ticker_sector_map.csv")
failed = pd.read_csv("security_prices_failed_tickers.csv")

ticker_sector = sector_map[["ticker", "sector"]].drop_duplicates(subset="ticker")
failed_with_sector = failed.merge(ticker_sector, on="ticker", how="left")

known_bad = failed_with_sector[failed_with_sector["sector"] == "Unclassified"]
unexpected = failed_with_sector[failed_with_sector["sector"] != "Unclassified"]

print(f"Total failed: {len(failed_with_sector)}")
print(f"Already-known-bad tickers (Unclassified sector, expected to fail): {len(known_bad)}")
print(f"Unexpected failures (had a real sector, should have worked): {len(unexpected)}")
print("\nSample of unexpected failures:")
print(unexpected.head(20).to_string(index=False))

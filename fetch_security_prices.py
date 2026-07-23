import os
import time
import pandas as pd
import yfinance as yf
from datetime import timedelta

BATCH_SIZE = 50
output_file = "security_prices.csv"

mapping = pd.read_csv("cusip_ticker_sector_map.csv")
holdings = pd.read_csv("raw_13f_holdings.csv", parse_dates=["filing_date"])

unique_tickers = sorted(mapping["ticker"].dropna().unique())

start_date = holdings["filing_date"].min() - timedelta(days=180)
end_date = holdings["filing_date"].max()

if os.path.exists(output_file):
    done = pd.read_csv(output_file)
    done_tickers = set(done["ticker"].unique())
    print(f"Resuming: {len(done_tickers)} tickers already done")
else:
    done_tickers = set()
    pd.DataFrame(columns=["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]).to_csv(output_file, index=False)

remaining = [t for t in unique_tickers if t not in done_tickers]
print(f"{len(remaining)} tickers left to process out of {len(unique_tickers)} total")
print(f"Date range: {start_date.date()} to {end_date.date()}")

failed_tickers = []

for i in range(0, len(remaining), BATCH_SIZE):
    batch = remaining[i:i + BATCH_SIZE]
    try:
        raw = yf.download(batch, start=start_date, end=end_date, group_by="ticker", auto_adjust=False, progress=False, threads=True)
    except Exception as e:
        print(f"Batch failed entirely: {e}")
        failed_tickers.extend(batch)
        continue

    rows = []
    for ticker in batch:
        try:
            df = raw[ticker].reset_index().dropna(subset=["Close"])
            if len(df) == 0:
                failed_tickers.append(ticker)
                continue
            df["ticker"] = ticker
            df = df.rename(columns={
                "Date": "date", "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
            })
            rows.append(df[["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]])
        except (KeyError, Exception):
            failed_tickers.append(ticker)

    if rows:
        batch_df = pd.concat(rows, ignore_index=True)
        batch_df.to_csv(output_file, mode="a", header=False, index=False)

    print(f"Processed {min(i + BATCH_SIZE, len(remaining))} / {len(remaining)} (failed so far: {len(failed_tickers)})")
    time.sleep(0.5)

print("\nDone.")
final = pd.read_csv(output_file)
print(f"Total rows saved: {len(final)}")
print(f"Tickers with price data: {final['ticker'].nunique()} / {len(unique_tickers)}")
print(f"Tickers that failed entirely: {len(failed_tickers)}")

pd.DataFrame({"ticker": failed_tickers}).to_csv("security_prices_failed_tickers.csv", index=False)

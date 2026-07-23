import os
import time
import pandas as pd
import yfinance as yf

mapping = old_mapping = pd.read_csv("cusip_ticker_map.csv")
new_mapping = pd.read_csv("cusip_ticker_map_new_batch.csv")
mapping = pd.concat([old_mapping, new_mapping], ignore_index=True)

unique_tickers = sorted(mapping["ticker"].dropna().unique())

output_file = "ticker_sector_map.csv"

if os.path.exists(output_file):
    done = pd.read_csv(output_file)
    done_tickers = set(done["ticker"])
    print(f"Resuming: {len(done_tickers)} tickers already done")
else:
    done_tickers = set()
    pd.DataFrame(columns=["ticker", "sector", "industry", "matched"]).to_csv(output_file, index=False)

remaining = [t for t in unique_tickers if t not in done_tickers]
print(f"{len(remaining)} tickers left to process out of {len(unique_tickers)} total")

for i, ticker in enumerate(remaining, 1):
    try:
        info = yf.Ticker(ticker).info
        sector = info.get("sector")
        industry = info.get("industry")
        matched = sector is not None
    except Exception:
        sector = None
        industry = None
        matched = False

    row = pd.DataFrame([{"ticker": ticker, "sector": sector, "industry": industry, "matched": matched}])
    row.to_csv(output_file, mode="a", header=False, index=False)

    if i % 50 == 0:
        print(f"Processed {i} / {len(remaining)}")

    time.sleep(0.15)

print("Done.")
final = pd.read_csv(output_file)
print(f"Total resolved: {final['matched'].sum()} / {len(final)}")

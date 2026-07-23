import time
import pandas as pd
import yfinance as yf
from datetime import timedelta

output_file = "security_prices.csv"
failed_file = "security_prices_failed_tickers.csv"

sector_map = pd.read_csv("cusip_ticker_sector_map.csv")
failed = pd.read_csv(failed_file)
holdings = pd.read_csv("raw_13f_holdings.csv", parse_dates=["filing_date"])

ticker_sector = sector_map[["ticker", "sector"]].drop_duplicates(subset="ticker")
failed_with_sector = failed.merge(ticker_sector, on="ticker", how="left")
retry_list = failed_with_sector[failed_with_sector["sector"] != "Unclassified"]["ticker"].tolist()

start_date = holdings["filing_date"].min() - timedelta(days=180)
end_date = holdings["filing_date"].max()

print(f"Retrying {len(retry_list)} tickers sequentially (no threading, slower but safer)")

still_failed = []
succeeded = 0

for i, ticker in enumerate(retry_list, 1):
    try:
        df = yf.Ticker(ticker).history(start=start_date, end=end_date, auto_adjust=False)
        if len(df) == 0:
            still_failed.append(ticker)
        else:
            df = df.reset_index()
            df["ticker"] = ticker
            df = df.rename(columns={
                "Date": "date", "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume",
            })
            if "Adj Close" in df.columns:
                df = df.rename(columns={"Adj Close": "adj_close"})
            else:
                df["adj_close"] = df["close"]
            df[["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]].to_csv(
                output_file, mode="a", header=False, index=False
            )
            succeeded += 1
    except Exception:
        still_failed.append(ticker)

    if i % 100 == 0:
        print(f"Processed {i} / {len(retry_list)} (succeeded so far: {succeeded})")

    time.sleep(0.5)

print(f"\nRetry done. Succeeded: {succeeded} / {len(retry_list)}")

remaining_failed = failed[~failed["ticker"].isin([t for t in retry_list if t not in still_failed])]
remaining_failed.to_csv(failed_file, index=False)
print(f"Still failed (all causes): {len(remaining_failed)}")

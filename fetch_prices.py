import pandas as pd
import yfinance as yf
from datetime import timedelta

BENCHMARK_TICKERS = ["SPY", "XLK", "XLF", "XLE"]

holdings = pd.read_csv("raw_13f_holdings.csv", parse_dates=["filing_date"])

start_date = holdings["filing_date"].min() - timedelta(days=180)
end_date = holdings["filing_date"].max()

print(f"Pulling benchmark prices from {start_date.date()} to {end_date.date()}")

raw = yf.download(
    BENCHMARK_TICKERS,
    start=start_date,
    end=end_date,
    group_by="ticker",
    auto_adjust=False,
)

rows = []
for ticker in BENCHMARK_TICKERS:
    df = raw[ticker].reset_index()
    df["ticker"] = ticker
    df = df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
    })
    rows.append(df[["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]])

prices = pd.concat(rows, ignore_index=True)
prices.to_csv("benchmark_prices.csv", index=False)

print(f"Saved {len(prices)} rows to benchmark_prices.csv")
print(prices.groupby("ticker")["date"].agg(["min", "max", "count"]))

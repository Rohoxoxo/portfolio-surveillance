import pandas as pd

holdings = pd.read_csv("raw_13f_holdings.csv")

unique_cusips = holdings["cusip"].drop_duplicates().reset_index(drop=True)

print(f"Total holding rows: {len(holdings)}")
print(f"Unique CUSIPs: {len(unique_cusips)}")
print(unique_cusips.head(10))

unique_cusips.to_csv("unique_cusips.csv", index=False, header=["cusip"])
print("Saved to unique_cusips.csv")

import pandas as pd

mapping = pd.read_csv("cusip_ticker_map_raw.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")

unmatched = mapping[mapping["matched"] == False][["cusip"]]

unmatched_named = unmatched.merge(
    holdings[["cusip", "security_name"]].drop_duplicates(subset="cusip"),
    on="cusip",
    how="left",
)

unmatched_named.to_csv("unmatched_cusips.csv", index=False)
print(f"Unmatched CUSIPs: {len(unmatched_named)}")
print(unmatched_named.head(20))

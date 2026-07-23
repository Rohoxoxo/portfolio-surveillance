import pandas as pd

first_pass = pd.read_csv("cusip_ticker_map_raw.csv")
cins_retry = pd.read_csv("cusip_ticker_map_cins_retry.csv")
holdings = pd.read_csv("raw_13f_holdings.csv")
existing = pd.read_csv("cusip_ticker_sector_map.csv")

first_pass_matched = first_pass[first_pass["matched"] == True]
cins_matched = cins_retry[cins_retry["matched"] == True]

new_matched = pd.concat([first_pass_matched, cins_matched], ignore_index=True)
new_matched = new_matched.drop(columns=["matched"])

new_matched.to_csv("cusip_ticker_map_new_batch.csv", index=False)
print(f"Newly resolved this batch: {len(new_matched)} CUSIPs -> saved to cusip_ticker_map_new_batch.csv")

all_cusips = set(holdings["cusip"].unique())
resolved_cusips = set(existing["cusip"]) | set(new_matched["cusip"])
still_missing = all_cusips - resolved_cusips

missing_df = pd.DataFrame({"cusip": sorted(still_missing)})
missing_df = missing_df.merge(
    holdings[["cusip", "security_name"]].drop_duplicates(subset="cusip"),
    on="cusip",
    how="left",
)
missing_df.to_csv("cusips_needing_manual_patch.csv", index=False)
print(f"Still unresolved (across full 5,721 CUSIPs): {len(missing_df)} -> saved to cusips_needing_manual_patch.csv")

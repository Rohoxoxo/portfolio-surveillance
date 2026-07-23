import pandas as pd

unique_cusips = pd.read_csv("unique_cusips.csv")
existing_map = pd.read_csv("cusip_ticker_sector_map.csv")

existing_cusips = set(existing_map["cusip"].unique())
all_cusips = set(unique_cusips["cusip"].unique())

new_cusips = all_cusips - existing_cusips

print(f"Total unique CUSIPs now: {len(all_cusips)}")
print(f"Already mapped: {len(existing_cusips)}")
print(f"New CUSIPs needing mapping: {len(new_cusips)}")

pd.DataFrame({"cusip": sorted(new_cusips)}).to_csv("new_cusips_to_map.csv", index=False)
print("Saved to new_cusips_to_map.csv")

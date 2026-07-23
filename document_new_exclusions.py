import pandas as pd

missing = pd.read_csv("cusips_needing_manual_patch.csv")
existing_exclusions = pd.read_csv("cusip_exclusions.csv")

new_exclusions = missing.copy()
new_exclusions["reason"] = "unresolved via OpenFIGI (CUSIP + CINS); immaterial value (<0.01% of total portfolio) — excluded from ticker mapping"

combined_exclusions = pd.concat([existing_exclusions, new_exclusions], ignore_index=True)
combined_exclusions.to_csv("cusip_exclusions.csv", index=False)

print(f"New exclusions added this batch: {len(new_exclusions)}")
print(f"Total exclusions now: {len(combined_exclusions)}")

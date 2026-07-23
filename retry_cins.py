import os
import time
import pandas as pd
import requests

API_KEY = os.environ["OPENFIGI_API_KEY"]
URL = "https://api.openfigi.com/v3/mapping"
BATCH_SIZE = 100

unmatched = pd.read_csv("unmatched_cusips.csv")

is_cins = unmatched["cusip"].str[0].str.isalpha()
cins_candidates = unmatched[is_cins]["cusip"].tolist()
still_unresolved = unmatched[~is_cins].copy()

print(f"Retrying {len(cins_candidates)} letter-prefixed CUSIPs as CINS")
print(f"{len(still_unresolved)} numeric CUSIPs skipped (not CINS pattern, stay unmatched for now)")

headers = {
    "Content-Type": "application/json",
    "X-OPENFIGI-APIKEY": API_KEY,
}

results = []

for i in range(0, len(cins_candidates), BATCH_SIZE):
    batch = cins_candidates[i:i + BATCH_SIZE]
    jobs = [{"idType": "ID_CINS", "idValue": c} for c in batch]

    response = requests.post(URL, json=jobs, headers=headers)
    response.raise_for_status()
    batch_results = response.json()

    for cusip, result in zip(batch, batch_results):
        if "data" in result and len(result["data"]) > 0:
            match = result["data"][0]
            results.append({
                "cusip": cusip,
                "ticker": match.get("ticker"),
                "company_name": match.get("name"),
                "security_type": match.get("securityType"),
                "matched": True,
            })
        else:
            results.append({
                "cusip": cusip,
                "ticker": None,
                "company_name": None,
                "security_type": None,
                "matched": False,
            })

    print(f"Processed {min(i + BATCH_SIZE, len(cins_candidates))} / {len(cins_candidates)}")
    time.sleep(0.25)

cins_results = pd.DataFrame(results)
matched_count = cins_results["matched"].sum()
print(f"\nCINS retry: matched {matched_count} / {len(cins_results)}")

cins_results.to_csv("cusip_ticker_map_cins_retry.csv", index=False)
print("Saved to cusip_ticker_map_cins_retry.csv")

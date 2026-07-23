import os
import time
import pandas as pd
import requests

API_KEY = os.environ["OPENFIGI_API_KEY"]
URL = "https://api.openfigi.com/v3/mapping"
BATCH_SIZE = 100

cusips = pd.read_csv("new_cusips_to_map.csv")["cusip"].tolist()

headers = {
    "Content-Type": "application/json",
    "X-OPENFIGI-APIKEY": API_KEY,
}

results = []

for i in range(0, len(cusips), BATCH_SIZE):
    batch = cusips[i:i + BATCH_SIZE]
    jobs = [{"idType": "ID_CUSIP", "idValue": c} for c in batch]

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

    print(f"Processed {min(i + BATCH_SIZE, len(cusips))} / {len(cusips)}")
    time.sleep(0.25)

mapping = pd.DataFrame(results)
mapping.to_csv("cusip_ticker_map_raw.csv", index=False)

matched_count = mapping["matched"].sum()
total = len(mapping)
print(f"\nMatched {matched_count} / {total} ({matched_count / total:.1%})")
print(f"Saved to cusip_ticker_map_raw.csv")

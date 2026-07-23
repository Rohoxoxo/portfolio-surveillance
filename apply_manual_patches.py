import pandas as pd

manual_patches = {
    "74267C106": {"ticker": "PRA",  "company_name": "ProAssurance Corp"},
    "G5S37H101": {"ticker": "MRX",  "company_name": "Marex Group plc"},
    "554489104": {"ticker": "VRE",  "company_name": "Veris Residential Inc"},
    "04351P101": {"ticker": "ASND", "company_name": "Ascendis Pharma A/S"},
    "128246105": {"ticker": "CVGW", "company_name": "Calavo Growers Inc"},
    "679369108": {"ticker": "OLPX", "company_name": "Olaplex Holdings Inc"},
    "444097109": {"ticker": "HPP",  "company_name": "Hudson Pacific Properties Inc"},
    "75605Y106": {"ticker": "HOUS", "company_name": "Anywhere Real Estate Inc"},
    "G4474Y214": {"ticker": "JHG",  "company_name": "Janus Henderson Group plc"},
    "58985J105": {"ticker": "MLNK", "company_name": "MeridianLink Inc"},
}

mapping = pd.read_csv("cusip_ticker_map.csv")
missing = pd.read_csv("cusips_needing_manual_patch.csv")

patched_rows = []
for cusip, info in manual_patches.items():
    patched_rows.append({
        "cusip": cusip,
        "ticker": info["ticker"],
        "company_name": info["company_name"],
        "security_type": "Common Stock",
    })
patched_df = pd.DataFrame(patched_rows)

mapping = pd.concat([mapping, patched_df], ignore_index=True)
mapping.to_csv("cusip_ticker_map.csv", index=False)

excluded = missing[~missing["cusip"].isin(manual_patches.keys())].copy()
excluded["reason"] = "unresolved via OpenFIGI (CUSIP + CINS); immaterial value (<0.03% of total portfolio) — excluded from ticker mapping"
excluded.to_csv("cusip_exclusions.csv", index=False)

print(f"Final mapping table: {len(mapping)} CUSIPs resolved -> cusip_ticker_map.csv")
print(f"Documented exclusions: {len(excluded)} CUSIPs -> cusip_exclusions.csv")
print(f"Coverage: {len(mapping)} / 4953 = {len(mapping)/4953:.1%}")

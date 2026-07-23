import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
import csv
import time

headers = {
    "User-Agent": "Rohit Chandel chandelrohit803@gmail.com"
}

MANAGERS = {
    "0001067983": "Berkshire Hathaway Inc",
    "0001336528": "Pershing Square Capital Management, L.P.",
    "0001037389": "Renaissance Technologies LLC",
    "0001350694": "Bridgewater Associates, LP",
    "0001649339": "Scion Asset Management, LLC",
    "0001697748": "ARK Investment Management LLC",
}

QUARTERS_TO_PULL = 8

def get_13f_filings(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    data = response.json()
    recent = data["filings"]["recent"]

    filings = []
    for form, date, accession in zip(recent["form"], recent["filingDate"], recent["accessionNumber"]):
        if form == "13F-HR":
            filings.append((date, accession))
    return filings

def get_info_table_filename(cik_nodash, accession_nodash):
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_nodash}/{accession_nodash}/index.json"
    response = requests.get(url, headers=headers)
    data = response.json()
    for item in data["directory"]["item"]:
        name = item["name"]
        if name.endswith(".xml") and name != "primary_doc.xml":
            return name
    return None

def get_holdings(cik_nodash, accession_nodash, filename):
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_nodash}/{accession_nodash}/{filename}"
    response = requests.get(url, headers=headers)

    ns = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}
    root = ET.fromstring(response.content)

    holdings = []
    for info_table in root.findall("ns:infoTable", ns):
        holdings.append({
            "name": info_table.find("ns:nameOfIssuer", ns).text,
            "cusip": info_table.find("ns:cusip", ns).text,
            "value": int(info_table.find("ns:value", ns).text),
            "shares": int(info_table.find("ns:shrsOrPrnAmt/ns:sshPrnamt", ns).text),
        })

    aggregated = defaultdict(lambda: {"name": "", "value": 0, "shares": 0})
    for h in holdings:
        key = h["cusip"]
        aggregated[key]["name"] = h["name"]
        aggregated[key]["value"] += h["value"]
        aggregated[key]["shares"] += h["shares"]

    return aggregated

all_rows = []

for cik, manager_name in MANAGERS.items():
    print(f"Fetching filings for {manager_name}...")
    filings = get_13f_filings(cik)
    latest_filings = filings[:QUARTERS_TO_PULL]

    cik_nodash = str(int(cik))

    for filing_date, accession in latest_filings:
        accession_nodash = accession.replace("-", "")
        print(f"  Quarter filed {filing_date}")

        filename = get_info_table_filename(cik_nodash, accession_nodash)
        time.sleep(0.3)

        if filename is None:
            print(f"  WARNING: no info table found, skipping")
            continue

        aggregated = get_holdings(cik_nodash, accession_nodash, filename)
        time.sleep(0.3)

        for cusip, info in aggregated.items():
            all_rows.append({
                "manager_cik": cik,
                "manager_name": manager_name,
                "filing_date": filing_date,
                "cusip": cusip,
                "security_name": info["name"],
                "value": info["value"],
                "shares": info["shares"],
            })

with open("raw_13f_holdings.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["manager_cik", "manager_name", "filing_date", "cusip", "security_name", "value", "shares"])
    writer.writeheader()
    writer.writerows(all_rows)

print(f"Done. Total rows saved: {len(all_rows)}")

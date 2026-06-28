import requests
from dotenv import load_dotenv
import os
import datetime as dt
import time
import csv
from pathlib import Path

load_dotenv()

API_KEY = os.getenv("API_KEY")
POLYGON_BASE_URL = "https://api.massive.com"
SLEEP_SECONDS = 12


def get_stock_prices(req_date):
    url = f"{POLYGON_BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{req_date}"

    try:
        params = {
            "adjusted": "true",
            "include_otc": "false",
            "apiKey": API_KEY
        }

        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()

        data = r.json()
        return data.get("results", [])

    except Exception as e:
        print(f"Error fetching {req_date}: {e}")
        return []


def extract_historical_data():

    start_date = dt.date(2025, 10, 17)
    end_date = dt.date(2025, 10, 24)

    # Directory where this Python file is located
    script_dir = Path(__file__).resolve().parent

    out_file = script_dir / (
        f"polygon_eod_grouped_{start_date:%Y%m%d}_{end_date:%Y%m%d}.csv"
    )

    print(f"Saving file to:\n{out_file}\n")

    ingest_ts = (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )

    with open(out_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "trade_date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "_src_file",
            "_ingest_ts"
        ])

        current_date = start_date

        while current_date <= end_date:

            print(f"Fetching {current_date}...")

            results = get_stock_prices(current_date)

            if results:

                print(f"{len(results)} rows")

                for row in results:

                    writer.writerow([
                        current_date,
                        row.get("T", ""),
                        row.get("o", ""),
                        row.get("h", ""),
                        row.get("l", ""),
                        row.get("c", ""),
                        row.get("v", ""),
                        out_file.name,
                        ingest_ts
                    ])

                f.flush()

            else:
                print(f"No data for {current_date}")

            current_date += dt.timedelta(days=1)
            time.sleep(SLEEP_SECONDS)

    print(f"\n✅ Saved successfully:\n{out_file}")


if __name__ == "__main__":
    extract_historical_data()

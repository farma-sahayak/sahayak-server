# agents/crop_price_updater/price_updater.py

import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict

from app.models.price_record import PriceRecord
from app.db.firestore import store_in_firestore, store_multiple_in_firestore


class CropPriceUpdater:
    BASE_URL = "https://api.data.gov.in/resource"

    def __init__(
            self,
            api_key: str,
            resource_id: str,
            commodity: str,
            state: str,
            market: Optional[str] = None,
            days_back: int = 0,
    ):
        self.api_key = api_key
        self.resource_id = resource_id
        self.commodity = commodity
        self.state = state
        self.market = market
        self.days_back = days_back

    async def fetch_multi_day_data(self):
        all_records = []

        async with httpx.AsyncClient() as client:
            for i in range(self.days_back + 1):  # include today
                fetch_date = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")

                params = {
                    "api-key": self.api_key,
                    "format": "json",
                    "filters[commodity]": self.commodity,
                    "filters[state]": self.state,
                    "filters[arrival_date]": fetch_date,
                    "limit": 1000,
                }
                if self.market:
                    params["filters[market]"] = self.market

                url = f"{self.BASE_URL}/{self.resource_id}"
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json().get("records", [])
                    all_records.extend(data)
                else:
                    print(f"[ERROR] Skipping date {fetch_date}: {response.status_code}")

                await asyncio.sleep(1)  # avoid rate limiting

        return all_records

    async def update_daily_prices(self):
        fetch_date = (datetime.today() - timedelta(days=self.days_back)).strftime("%Y-%m-%d")

        params = {
            "api-key": self.api_key,
            "format": "json",
            "filters[commodity]": self.commodity,
            "filters[state]": self.state,
            "filters[arrival_date]": fetch_date,
            "limit": 1000,
        }

        if self.market:
            params["filters[market]"] = self.market

        url = f"{self.BASE_URL}/{self.resource_id}"
        
        print(f"[DEBUG] Making API call to: {url}")
        print(f"[DEBUG] With params: {params}")

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            print(f"[DEBUG] API Response status: {response.status_code}")
            print(f"[DEBUG] API Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"[DEBUG] API Response total: {data.get('total', 'N/A')}")
            print(f"[DEBUG] API Response count: {data.get('count', 'N/A')}")
            print(f"[DEBUG] API Response message: {data.get('message', 'N/A')}")
            
            # Print the full response for debugging
            print(f"[DEBUG] Full API Response: {data}")
            
            records = data.get("records", [])
            
            print(f"[DEBUG] Fetched {len(records)} records from API")
            
            # Store records in Firestore
            firestore_records = []
            
            for entry in records:
                try:
                    record = self._parse_to_price_record(entry)
                    # Convert to dict and add state for Firestore
                    record_dict = record.dict()
                    record_dict['state'] = self.state
                    firestore_records.append(record_dict)
                    print(f"[PARSED RECORD] {record}")
                except Exception as e:
                    print(f"[ERROR] Skipping record due to parse error: {e}")
                    print(f"[ERROR] Problematic entry: {entry}")
            
            print(f"[DEBUG] Prepared {len(firestore_records)} records for Firestore")
            
            # Store all records in Firestore
            if firestore_records:
                result = await store_multiple_in_firestore(firestore_records)
                print(f"[FIRESTORE] Stored {result['success']}/{result['total']} records successfully")
            else:
                print("[WARNING] No records to store in Firestore")

    def _parse_to_price_record(self, entry: Dict) -> PriceRecord:
        date_str = entry["arrival_date"]
        date_obj = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                date_obj = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue
        if date_obj is None:
            raise ValueError(f"Unrecognized date format: {date_str}")
        return PriceRecord(
            date=date_obj,
            market=entry["market"],
            commodity=entry["commodity"],
            variety=entry.get("variety"),
            min_price=int(entry["min_price"]),
            max_price=int(entry["max_price"]),
            modal_price=int(entry["modal_price"]),
        )

    async def fetch_cleaned_data(self):
        raw_records = await self.fetch_multi_day_data()
        cleaned = []

        for entry in raw_records:
            try:
                parsed = self._parse_to_price_record(entry)
                cleaned.append(parsed.dict())
            except Exception as e:
                print(f"[ERROR] Skipping record due to parse error: {e}")

        return cleaned

    async def fetch_raw_data(self):
        fetch_date = (datetime.today() - timedelta(days=self.days_back)).strftime("%Y-%m-%d")

        params = {
            "api-key": self.api_key,
            "format": "json",
            "filters[commodity]": self.commodity,
            "filters[state]": self.state,
            # "filters[arrival_date]": fetch_date,
            "limit": 1000,
        }

        if self.market:
            params["filters[market]"] = self.market

        url = f"{self.BASE_URL}/{self.resource_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()  # 👈 this is what you want to print or return

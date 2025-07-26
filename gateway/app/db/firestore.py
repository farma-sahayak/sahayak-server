import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict, Any
from datetime import date
import json
import os

# Initialize Firebase Admin SDK
try:
    # Try to get the service account path from environment variable
    service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not service_account_path:
        # Fallback to common paths - check both local and container paths
        possible_paths = [
            # Local development paths
            "gateway/service-account-key.json",
            "service-account-key.json",
            # Container paths (when mounted to /app)
            "/app/gateway/service-account-key.json",
            "/app/service-account-key.json",
            # Alternative container paths
            "/app/.secrets/sahayak-ai-9519a-firebase-adminsdk-fbsvc-3bf1fc7d6c.json",
            ".secrets/sahayak-ai-9519a-firebase-adminsdk-fbsvc-3bf1fc7d6c.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                service_account_path = path
                break
    
    if service_account_path and os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print(f"[FIRESTORE] Initialized with service account: {service_account_path}")
    else:
        # Initialize with default credentials (for local development)
        firebase_admin.initialize_app()
        print("[FIRESTORE] Initialized with default credentials")
        
except Exception as e:
    print(f"[FIRESTORE ERROR] Failed to initialize: {e}")
    # Initialize without credentials (will use default)
    firebase_admin.initialize_app()

# Get Firestore client
db = firestore.client()

class FirestoreService:
    def __init__(self):
        self.db = db
        self.collection_name = "crops"  # Updated to match new structure

    async def store_price_record(self, record: Dict[str, Any]) -> bool:
        """
        Store a single price record in Firestore.
        
        Structure: crops/{state}/{commodity}/{date}_{market}/data
        """
        try:
            print(f"[FIRESTORE DEBUG] Attempting to store record: {record}")
            
            # Convert date to string for document ID
            date_str = record['date']
            if isinstance(date_str, date):
                date_str = date_str.strftime("%Y-%m-%d")
            
            # Create document path: crops/{state}/{commodity}/{date}_{market}
            state = record['state'].replace(" ", "_").lower()
            commodity = record['commodity'].replace(" ", "_").lower()
            market = record['market'].replace(" ", "_").lower()
            doc_id = f"{date_str}_{market}"
            
            doc_path = f"crops/{state}/{commodity}/{doc_id}"
            print(f"[FIRESTORE DEBUG] Document path: {doc_path}")
            
            # Prepare data for Firestore
            firestore_data = {
                'date': date_str,
                'market': record['market'],
                'commodity': record['commodity'],
                'state': record['state'],
                'variety': record.get('variety'),
                'min_price': record['min_price'],
                'max_price': record['max_price'],
                'modal_price': record['modal_price'],
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            print(f"[FIRESTORE DEBUG] Firestore data: {firestore_data}")
            
            # Store in Firestore using the hierarchical path
            doc_ref = self.db.document(doc_path)
            doc_ref.set(firestore_data)
            
            print(f"[FIRESTORE] Successfully stored record: {doc_path}")
            return True
            
        except Exception as e:
            print(f"[FIRESTORE ERROR] Failed to store record: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def store_price_records(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Store multiple price records in Firestore.
        Returns success and failure counts.
        """
        success_count = 0
        failure_count = 0
        
        for record in records:
            if await self.store_price_record(record):
                success_count += 1
            else:
                failure_count += 1
        
        return {
            'success': success_count,
            'failure': failure_count,
            'total': len(records)
        }

    async def get_price_records(self, date_str: str, state: str = None, commodity: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve price records from Firestore using the new hierarchical structure.
        """
        try:
            records = []
            
            if state and commodity:
                # Query specific state and commodity
                state_path = state.replace(" ", "_").lower()
                commodity_path = commodity.replace(" ", "_").lower()
                collection_ref = self.db.collection(f"crops/{state_path}/{commodity_path}")
                
                # Get all documents in this collection
                docs = collection_ref.stream()
                for doc in docs:
                    record = doc.to_dict()
                    record['id'] = doc.id
                    # Only include records for the specified date
                    if record.get('date') == date_str:
                        records.append(record)
                        
            elif state:
                # Query all commodities for a specific state
                state_path = state.replace(" ", "_").lower()
                state_ref = self.db.collection(f"crops/{state_path}")
                
                # Get all commodity collections
                commodity_collections = state_ref.list_collections()
                for commodity_collection in commodity_collections:
                    commodity_docs = commodity_collection.stream()
                    for doc in commodity_docs:
                        record = doc.to_dict()
                        record['id'] = doc.id
                        if record.get('date') == date_str:
                            records.append(record)
                            
            else:
                # Query all records for the date (expensive operation)
                print("[WARNING] Querying all records without state/commodity filter")
                all_collections = self.db.collection_group(self.collection_name)
                docs = all_collections.where('date', '==', date_str).stream()
                
                for doc in docs:
                    record = doc.to_dict()
                    record['id'] = doc.id
                    records.append(record)
            
            return records
            
        except Exception as e:
            print(f"[FIRESTORE ERROR] Failed to retrieve records: {e}")
            return []

# Global instance
firestore_service = FirestoreService()

# Convenience functions
async def store_in_firestore(record: Dict[str, Any]) -> bool:
    """Store a single price record in Firestore."""
    return await firestore_service.store_price_record(record)

async def store_multiple_in_firestore(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Store multiple price records in Firestore."""
    return await firestore_service.store_price_records(records) 
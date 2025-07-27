from fastapi import APIRouter, Query
from app.services.price_updater import CropPriceUpdater
from app.db.firestore import firestore_service

router = APIRouter()

@router.get("/daily-prices")
async def update_prices(
        api_key: str = Query(...),
        resource_id: str = Query(...),
        commodity: str = Query(...),
        state: str = Query(...),
        market: str = Query(None),
        days_back: int = Query(0)
):
    try:
        updater = CropPriceUpdater(
            api_key=api_key,
            resource_id=resource_id,
            commodity=commodity,
            state=state,
            market=market,
            days_back=days_back
        )
        
        # This will fetch data and store in Firestore
        await updater.update_daily_prices()
        
        # Fetch data from Firestore for the current date
        from datetime import datetime, timedelta
        fetch_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Get stored data from Firestore
        stored_data = await firestore_service.get_price_records(
            date_str=fetch_date,
            state=state,
            commodity=commodity
        )
        
        # Format the data as a list of markets with commodity values
        markets_data = []
        for record in stored_data:
            market_data = {
                "date": record.get("date"),
                "market": record.get("market"),
                "commodity": record.get("commodity"),
                "variety": record.get("variety"),
                "min_price": record.get("min_price"),
                "max_price": record.get("max_price"),
                "modal_price": record.get("modal_price")
            }
            markets_data.append(market_data)
        
        return {
            "status": "ok", 
            "message": f"Updated prices for {commodity} in {state}",
            "data": markets_data,
            "firestore_status": f"Data stored in Firestore. Retrieved {len(markets_data)} market records."
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.get("/sample-data")
async def get_sample_data(
        commodity: str = Query("Wheat"),
        state: str = Query("Uttar Pradesh")
):
    """
    Sample endpoint to demonstrate the correct data format
    """
    sample_data = [
        {
            "date": "2025-07-26",
            "market": "Agra",
            "commodity": commodity,
            "variety": "Dara",
            "min_price": 2500,
            "max_price": 2620,
            "modal_price": 2540
        },
        {
            "date": "2025-07-26",
            "market": "Auraiya",
            "commodity": commodity,
            "variety": "Dara",
            "min_price": 2500,
            "max_price": 2570,
            "modal_price": 2550
        },
        {
            "date": "2025-07-26",
            "market": "Babrala",
            "commodity": commodity,
            "variety": "Dara",
            "min_price": 2430,
            "max_price": 2450,
            "modal_price": 2440
        },
        {
            "date": "2025-07-26",
            "market": "Vilthararoad",
            "commodity": commodity,
            "variety": "Dara",
            "min_price": 2500,
            "max_price": 2600,
            "modal_price": 2550
        },
        {
            "date": "2025-07-26",
            "market": "Safdarganj",
            "commodity": commodity,
            "variety": "Dara",
            "min_price": 2500,
            "max_price": 2600,
            "modal_price": 2550
        }
    ]
    
    return {
        "status": "ok",
        "message": f"Sample data for {commodity} in {state}",
        "data": sample_data,
        "note": "This is sample data. Use /daily-prices endpoint with valid resource_id for real data."
    }

@router.delete("/cleanup-debug")
async def cleanup_debug_data():
    """
    Cleanup endpoint to remove debug data from Firestore
    """
    try:
        # Delete the debug document
        debug_doc_path = "crops/uttar_pradesh/wheat/2025-07-26_debug"
        doc_ref = firestore_service.db.document(debug_doc_path)
        doc_ref.delete()
        
        return {
            "status": "ok",
            "message": "Debug data cleaned up from Firestore"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

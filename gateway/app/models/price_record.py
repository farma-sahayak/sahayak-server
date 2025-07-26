from pydantic import BaseModel
from typing import Optional
from datetime import date

class PriceRecord(BaseModel):
    date: date
    market: str
    commodity: str
    variety: Optional[str] = None
    min_price: int
    max_price: int
    modal_price: int

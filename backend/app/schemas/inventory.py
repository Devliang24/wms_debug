from typing import List, Optional

from pydantic import BaseModel, Field


class TransferRequest(BaseModel):
    from_warehouse_id: int
    to_warehouse_id: int
    sku: str = Field(min_length=1, max_length=32)
    quantity: int


class WarningThresholdUpdate(BaseModel):
    warehouse_id: int
    sku: str = Field(min_length=1, max_length=32)
    warning_threshold: int


class StocktakeItemInput(BaseModel):
    sku: str = Field(min_length=1, max_length=32)
    counted_qty: int


class StocktakeSubmitRequest(BaseModel):
    warehouse_id: int
    items: List[StocktakeItemInput]
    stocktake_id: Optional[int] = None

from typing import List

from pydantic import BaseModel, Field


class OutboundItemInput(BaseModel):
    sku: str = Field(min_length=1, max_length=32)
    quantity: int


class OutboundCreateRequest(BaseModel):
    warehouse_id: int
    items: List[OutboundItemInput]

from typing import List

from pydantic import BaseModel, Field


class InboundItemInput(BaseModel):
    sku: str = Field(min_length=1, max_length=32)
    quantity: int
    unit_price: float = 0  # 元


class InboundCreateRequest(BaseModel):
    warehouse_id: int
    items: List[InboundItemInput]


class InboundUpdateRequest(BaseModel):
    items: List[InboundItemInput]

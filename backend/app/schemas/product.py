from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, max_length=50)
    unit: Optional[str] = Field(default=None, max_length=20)
    image_url: Optional[str] = Field(default=None, max_length=255)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    category: Optional[str] = Field(default=None, max_length=50)
    unit: Optional[str] = Field(default=None, max_length=20)
    image_url: Optional[str] = Field(default=None, max_length=255)

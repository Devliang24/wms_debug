from typing import Optional

from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    warehouse_ids: Optional[str] = None

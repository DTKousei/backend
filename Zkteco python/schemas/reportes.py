from pydantic import BaseModel
from typing import List, Optional

class SabanaRequest(BaseModel):
    anio: int
    mes: int
    user_ids: Optional[List[str]] = None
    area: Optional[str] = None
    
    class Config:
        extra = "allow"

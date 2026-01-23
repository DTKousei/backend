from pydantic import BaseModel
from typing import List, Optional

class SabanaRequest(BaseModel):
    anio: int
    mes: int
    user_ids: Optional[List[str]] = None
    area: Optional[str] = None
    

class SaldosRequest(BaseModel):
    anio: int
    empleado_id: Optional[str] = None

    class Config:
        extra = "allow"

class TipoReporteBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True

class TipoReporteCreate(TipoReporteBase):
    pass

class TipoReporte(TipoReporteBase):
    id: int
    class Config:
        orm_mode = True

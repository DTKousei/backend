from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DepartamentoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class DepartamentoCreate(DepartamentoBase):
    pass

class DepartamentoUpdate(DepartamentoBase):
    nombre: Optional[str] = None

class DepartamentoResponse(DepartamentoBase):
    id: int
    jefe_id: Optional[str] = None
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class UsuarioDepartamentoResponse(BaseModel):
    user_id: str
    nombre: str
    cargo: Optional[str] = None
    
    class Config:
        from_attributes = True

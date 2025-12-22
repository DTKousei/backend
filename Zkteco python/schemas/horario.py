from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time

class HorarioBase(BaseModel):
    """Schema base para horario"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del horario")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción")
    activo: bool = Field(default=True, description="Si el horario está activo")

class HorarioCreate(HorarioBase):
    """Schema para crear un horario"""
    pass

class HorarioUpdate(BaseModel):
    """Schema para actualizar un horario"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None

class HorarioResponse(HorarioBase):
    """Schema para respuesta de horario"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

# Schemas para Segmentos
class SegmentoHorarioBase(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6, description="0=Lunes, 6=Domingo")
    hora_inicio: time
    hora_fin: time
    tolerancia_minutos: int = Field(default=0, ge=0)
    orden_turno: int = Field(default=1)

class SegmentoHorarioCreate(SegmentoHorarioBase):
    horario_id: int

class SegmentoHorarioResponse(SegmentoHorarioBase):
    id: int
    horario_id: int
    
    class Config:
        from_attributes = True

class SegmentoHorarioBulkCreate(BaseModel):
    horario_id: int
    dias_semana: List[int] = Field(..., description="Lista de días 0=Lunes, 6=Domingo")
    hora_inicio: time
    hora_fin: time
    tolerancia_minutos: int = Field(default=0, ge=0)
    orden_turno: int = Field(default=1)

# Schemas para Asignaciones
class AsignacionHorarioBase(BaseModel):
    user_id: str
    horario_id: int
    fecha_inicio: datetime # Usamos datetime para simplificar, aunque modelo es Date
    fecha_fin: Optional[datetime] = None

class AsignacionHorarioCreate(AsignacionHorarioBase):
    pass

class AsignacionHorarioResponse(AsignacionHorarioBase):
    id: int
    
    class Config:
        from_attributes = True
    class Config:
        from_attributes = True

class AsignacionHorarioDetailResponse(AsignacionHorarioResponse):
    horario: HorarioResponse


from datetime import date

# Schemas para Feriados
class FeriadoBase(BaseModel):
    fecha: date
    nombre: str = Field(..., min_length=1, max_length=100)

class FeriadoCreate(FeriadoBase):
    pass

class FeriadoResponse(FeriadoBase):
    id: int
    
    class Config:
        from_attributes = True

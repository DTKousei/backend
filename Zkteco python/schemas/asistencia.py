"""
Schemas de Pydantic para Asistencias
Validación de datos de entrada y salida de la API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AsistenciaBase(BaseModel):
    """Schema base para asistencia"""
    user_id: str = Field(..., description="ID del usuario")
    timestamp: datetime = Field(..., description="Fecha y hora de la marcación")
    status: int = Field(default=0, description="Estado del registro")
    punch: int = Field(default=0, description="Tipo de marcación")


class AsistenciaResponse(AsistenciaBase):
    """Schema para respuesta de asistencia"""
    id: int
    dispositivo_id: int
    sincronizado: bool
    fecha_sincronizacion: datetime
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class AsistenciaFilter(BaseModel):
    """Schema para filtrar asistencias"""
    user_id: Optional[str] = Field(None, description="Filtrar por ID de usuario")
    dispositivo_id: Optional[int] = Field(None, description="Filtrar por dispositivo")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio del rango")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin del rango")
    limit: int = Field(default=100, ge=1, le=10000, description="Límite de registros")
    offset: int = Field(default=0, ge=0, description="Offset para paginación")


class AsistenciaSincronizacion(BaseModel):
    """Schema para respuesta de sincronización"""
    success: bool
    message: str
    registros_nuevos: int = 0
    registros_totales: int = 0
    dispositivo_id: int

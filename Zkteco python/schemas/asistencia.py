"""
Schemas de Pydantic para Asistencias
Validación de datos de entrada y salida de la API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time


class AsistenciaBase(BaseModel):
    """Schema base para asistencia"""
    user_id: Optional[str] = Field(None, description="ID del usuario (DNI)")
    uid: int = Field(..., description="UID interno del dispositivo")
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
    uid: Optional[int] = Field(None, description="Filtrar por UID")
    user_id: Optional[str] = Field(None, description="Filtrar por ID de usuario NO FUNCIONA IGUAL Q ANTES")
    dispositivo_id: Optional[int] = Field(None, description="Filtrar por dispositivo")
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


class AsistenciaDiariaResponse(BaseModel):
    """Schema para reporte de asistencia diaria"""
    id: int
    fecha: datetime
    user_id: str
    horario_id_snapshot: Optional[int]
    horas_esperadas: float
    horas_trabajadas: float
    estado_asistencia: str
    es_justificado: bool
    entrada_real: Optional[time]
    salida_real: Optional[time]
    
    class Config:
        from_attributes = True



class TipoAsistencia(str):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"

class AsistenciaManualCreate(BaseModel):
    tipo: str = Field(..., description="Tipo de marcación: 'ENTRADA' o 'SALIDA'")
    empleado_id: str = Field(..., description="ID del empleado")
    fecha_hora: datetime = Field(..., description="Fecha y hora del registro")

"""
Schemas de Pydantic para Horarios
Validación de datos de entrada y salida de la API
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, time


class HorarioBase(BaseModel):
    """Schema base para horario"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del horario")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción")
    hora_entrada: time = Field(..., description="Hora de entrada")
    hora_salida: time = Field(..., description="Hora de salida")
    dias_semana: List[str] = Field(..., description="Días de la semana que aplica")
    tolerancia_entrada: int = Field(default=0, ge=0, le=120, description="Minutos de tolerancia entrada")
    tolerancia_salida: int = Field(default=0, ge=0, le=120, description="Minutos de tolerancia salida")
    activo: bool = Field(default=True, description="Si el horario está activo")
    
    @field_validator('dias_semana')
    @classmethod
    def validar_dias(cls, v):
        dias_validos = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        for dia in v:
            if dia.lower() not in dias_validos:
                raise ValueError(f'Día inválido: {dia}. Días válidos: {dias_validos}')
        return [dia.lower() for dia in v]


class HorarioCreate(HorarioBase):
    """Schema para crear un horario"""
    pass


class HorarioUpdate(BaseModel):
    """Schema para actualizar un horario (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None
    dias_semana: Optional[List[str]] = None
    tolerancia_entrada: Optional[int] = Field(None, ge=0, le=120)
    tolerancia_salida: Optional[int] = Field(None, ge=0, le=120)
    activo: Optional[bool] = None
    
    @field_validator('dias_semana')
    @classmethod
    def validar_dias(cls, v):
        if v is None:
            return v
        dias_validos = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        for dia in v:
            if dia.lower() not in dias_validos:
                raise ValueError(f'Día inválido: {dia}. Días válidos: {dias_validos}')
        return [dia.lower() for dia in v]


class HorarioResponse(HorarioBase):
    """Schema para respuesta de horario"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

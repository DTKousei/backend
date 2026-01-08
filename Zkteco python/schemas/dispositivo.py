"""
Schemas de Pydantic para Dispositivos
Validación de datos de entrada y salida de la API
"""

from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional
from datetime import datetime


class DispositivoBase(BaseModel):
    """Schema base para dispositivo"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo del dispositivo")
    ip_address: str = Field(..., description="Dirección IP del dispositivo")
    puerto: int = Field(default=4370, ge=0, le=65535, description="Puerto TCP del dispositivo")
    ubicacion: Optional[str] = Field(None, max_length=200, description="Ubicación física")
    password: int = Field(default=0, description="Contraseña del dispositivo")
    timeout: int = Field(default=5, ge=0, le=60, description="Timeout de conexión en segundos")
    activo: bool = Field(default=True, description="Si el dispositivo está activo")


class DispositivoCreate(DispositivoBase):
    """Schema para crear un dispositivo"""
    pass


class DispositivoUpdate(BaseModel):
    """Schema para actualizar un dispositivo (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    ip_address: Optional[str] = None
    puerto: Optional[int] = Field(None, ge=1, le=65535)
    ubicacion: Optional[str] = Field(None, max_length=200)
    password: Optional[int] = None
    timeout: Optional[int] = Field(None, ge=1, le=60)
    activo: Optional[bool] = None


class DispositivoResponse(DispositivoBase):
    """Schema para respuesta de dispositivo"""
    id: int
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    platform: Optional[str] = None
    device_name: Optional[str] = None
    mac_address: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    ultima_sincronizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DispositivoInfo(BaseModel):
    """Schema para información detallada del dispositivo"""
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    platform: Optional[str] = None
    device_name: Optional[str] = None
    mac_address: Optional[str] = None
    ip_address: str
    puerto: int
    hora_dispositivo: Optional[datetime] = None


class DispositivoTestConexion(BaseModel):
    """Schema para respuesta de test de conexión"""
    success: bool
    message: str
    info: Optional[DispositivoInfo] = None

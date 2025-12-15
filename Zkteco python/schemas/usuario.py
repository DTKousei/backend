"""
Schemas de Pydantic para Usuarios
Validación de datos de entrada y salida de la API
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date


class UsuarioBase(BaseModel):
    """Schema base para usuario"""
    user_id: str = Field(..., min_length=1, max_length=20, description="ID del usuario en el dispositivo")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre completo")
    privilegio: int = Field(default=0, ge=0, le=14, description="Nivel de privilegio (0=usuario, 14=admin)")
    password: Optional[str] = Field(None, max_length=20, description="Contraseña del usuario")
    grupo: Optional[str] = Field(None, max_length=20, description="ID del grupo")
    email: Optional[EmailStr] = Field(None, description="Email del usuario")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono")
    departamento: Optional[str] = Field(None, max_length=100, description="Departamento")
    cargo: Optional[str] = Field(None, max_length=100, description="Cargo")
    
    # Nuevos campos
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento")
    direccion: Optional[str] = Field(None, max_length=255, description="Dirección")
    comentarios: Optional[str] = Field(None, max_length=500, description="Comentarios")


class UsuarioCreate(UsuarioBase):
    """Schema para crear un usuario"""
    dispositivo_id: int = Field(..., description="ID del dispositivo al que pertenece")


class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    privilegio: Optional[int] = Field(None, ge=0, le=14)
    password: Optional[str] = Field(None, max_length=20)
    grupo: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    departamento: Optional[str] = Field(None, max_length=100)
    cargo: Optional[str] = Field(None, max_length=100)
    
    # Nuevos campos
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = Field(None, max_length=255)
    comentarios: Optional[str] = Field(None, max_length=500)


class UsuarioResponse(UsuarioBase):
    """Schema para respuesta de usuario"""
    id: int
    uid: Optional[int] = None
    dispositivo_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class UsuarioSincronizar(BaseModel):
    """Schema para sincronizar usuario con dispositivo"""
    sincronizar_a_dispositivo: bool = Field(default=True, description="Si se debe sincronizar al dispositivo ZKTeco")

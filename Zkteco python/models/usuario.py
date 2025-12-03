"""
Modelo de Usuario
Representa un usuario registrado en el sistema y en los dispositivos ZKTeco
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class Usuario(Base):
    """
    Tabla de usuarios del sistema de control de asistencia
    """
    __tablename__ = "usuarios"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(20), nullable=False, unique=True, index=True, comment="ID del usuario en el dispositivo")
    uid = Column(Integer, comment="UID interno del dispositivo")
    nombre = Column(String(100), nullable=False, comment="Nombre completo del usuario")
    
    # Información de acceso
    privilegio = Column(Integer, default=0, comment="Nivel de privilegio (0=usuario, 14=admin)")
    password = Column(String(20), comment="Contraseña del usuario")
    grupo = Column(String(20), comment="ID del grupo")
    
    # Relación con dispositivo
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id", ondelete="CASCADE"), nullable=False)
    
    # Información adicional
    email = Column(String(100), comment="Email del usuario")
    telefono = Column(String(20), comment="Teléfono del usuario")
    departamento = Column(String(100), comment="Departamento")
    cargo = Column(String(100), comment="Cargo o posición")
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.now, comment="Fecha de registro")
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="Última actualización")
    
    # Relaciones
    dispositivo = relationship("Dispositivo", back_populates="usuarios")
    asistencias = relationship("Asistencia", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, user_id='{self.user_id}', nombre='{self.nombre}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "uid": self.uid,
            "nombre": self.nombre,
            "privilegio": self.privilegio,
            "grupo": self.grupo,
            "dispositivo_id": self.dispositivo_id,
            "email": self.email,
            "telefono": self.telefono,
            "departamento": self.departamento,
            "cargo": self.cargo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }

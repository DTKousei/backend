"""
Modelo de Departamento (Área)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base

class Departamento(Base):
    """
    Tabla de departamentos o áreas de la empresa
    """
    __tablename__ = "departamentos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, comment="Nombre del departamento")
    descripcion = Column(String(255), nullable=True, comment="Descripción del área")
    
    # Jefe del departamento (Referencia al DNI/user_id del usuario)
    jefe_id = Column(String(20), ForeignKey("usuarios.user_id", ondelete="SET NULL"), nullable=True, comment="DNI del jefe del área")
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    # Jefe es un Usuario
    jefe = relationship("Usuario", foreign_keys=[jefe_id], back_populates="departamentos_a_cargo")
    
    # Un departamento tiene muchos usuarios
    usuarios = relationship("Usuario", foreign_keys="[Usuario.departamento_id]", back_populates="departamento_rel")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "jefe_id": self.jefe_id,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

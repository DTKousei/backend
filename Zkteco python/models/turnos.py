"""
Modelos de Turnos y Asignaciones
"""

from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.database import Base

class SegmentosHorario(Base):
    """
    Define los segmentos de trabajo (turnos) para un horario
    Ej: Mañana 08:00-13:00, Tarde 14:00-18:00
    """
    __tablename__ = "segmentos_horario"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    horario_id = Column(Integer, ForeignKey("horarios.id", ondelete="CASCADE"), nullable=False)
    
    # Configuración del segmento
    dia_semana = Column(Integer, nullable=False, comment="0=Lunes, 6=Domingo")
    hora_inicio = Column(Time, nullable=False, comment="Hora inicio turno")
    hora_fin = Column(Time, nullable=False, comment="Hora fin turno")
    
    tolerancia_minutos = Column(Integer, default=0, comment="Tolerancia en minutos para llegada tarde")
    orden_turno = Column(Integer, default=1, comment="Orden del turno en el día (1, 2, ...)")
    
    # Relaciones
    horario = relationship("Horario", backref="segmentos")
    
    def __repr__(self):
        return f"<Segmento(id={self.id}, dia={self.dia_semana}, inicio={self.hora_inicio}, fin={self.hora_fin})>"

class AsignacionHorario(Base):
    """
    Asignación de horarios a usuarios por rangos de fecha
    """
    __tablename__ = "asignacion_horario"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(20), ForeignKey("usuarios.user_id", ondelete="CASCADE"), nullable=False)
    horario_id = Column(Integer, ForeignKey("horarios.id", ondelete="CASCADE"), nullable=False)
    
    fecha_inicio = Column(Date, nullable=False, comment="Fecha inicio validez")
    fecha_fin = Column(Date, nullable=True, comment="Fecha fin validez (Null = indefinido)")
    
    # Relaciones
    usuario = relationship("Usuario", backref="asignaciones_horario")

    horario = relationship("Horario")

class Feriados(Base):
    """
    Días feriados o no laborables
    """
    __tablename__ = "feriados"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, unique=True, nullable=False, comment="Fecha del feriado")
    nombre = Column(String(100), nullable=False, comment="Nombre de la festividad")
    
    def __repr__(self):
        return f"<Feriado({self.fecha}: {self.nombre})>"

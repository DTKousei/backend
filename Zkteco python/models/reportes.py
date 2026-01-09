"""
Modelos para Reportes de Asistencia
"""

from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base

class AsistenciaDiaria(Base):
    """
    Tabla de reporte diario procesado. 
    Almacena el resumen de asistencia de un usuario en un día específico.
    """
    __tablename__ = "asistencia_diaria"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    user_id = Column(String(20), ForeignKey("usuarios.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    
    # Snapshot del horario usado para cálculo
    horario_id_snapshot = Column(Integer, ForeignKey("horarios.id", ondelete="SET NULL"), nullable=True)
    
    # Métricas calculadas
    horas_esperadas = Column(Float, default=0.0, comment="Horas que debía trabajar")
    horas_trabajadas = Column(Float, default=0.0, comment="Horas realmente trabajadas")
    
    # Estado del día
    estado_asistencia = Column(String(50), nullable=False, default="FALTA", comment="Presente, Tarde, Falta, Feriado, Vacaciones")
    es_justificado = Column(Boolean, default=False, comment="Si la inasistencia/tardanza fue justificada")
    
    # Tiempos reales (primer ingreso y última salida del día globalm, informativo)
    entrada_real = Column(Time, nullable=True)
    salida_real = Column(Time, nullable=True)
    
    def __repr__(self):
        return f"<Reporte(user={self.user_id}, fecha={self.fecha}, estado={self.estado_asistencia})>"

class ReportesGenerados(Base):
    """
    Tabla para el registro de reportes generados (historial).
    """
    __tablename__ = "reportes_generados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo_reporte = Column(String(50), nullable=False, comment="Ej: Sabana, Excel, PDF")
    
    # Parámetros del reporte
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    area = Column(String(100), nullable=True, comment="Filtro de área aplicado (si hubo)")
    filtros = Column(String(500), nullable=True, comment="Otros filtros en formato JSON string") # SQLite compatible

    
    # Metadatos del archivo
    ruta_archivo = Column(String(255), nullable=True, comment="Ruta física donde se guardó (si aplica)")
    fecha_generacion = Column(DateTime, default=datetime.now)
    usuario_generador_id = Column(Integer, nullable=True, comment="ID del usuario admin que generó el reporte")

    def __repr__(self):
        return f"<ReporteGenerado(tipo={self.tipo_reporte}, fecha={self.fecha_generacion}, area={self.area})>"

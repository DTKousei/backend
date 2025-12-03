"""
Servicio de Horarios
Lógica de negocio para gestión de horarios
"""

from sqlalchemy.orm import Session
from models.horario import Horario
from schemas.horario import HorarioCreate, HorarioUpdate
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class HorarioService:
    """Servicio para gestión de horarios"""
    
    @staticmethod
    def crear_horario(db: Session, horario: HorarioCreate) -> Horario:
        """
        Crea un nuevo horario
        """
        db_horario = Horario(
            nombre=horario.nombre,
            descripcion=horario.descripcion,
            hora_entrada=horario.hora_entrada,
            hora_salida=horario.hora_salida,
            dias_semana=horario.dias_semana,
            tolerancia_entrada=horario.tolerancia_entrada,
            tolerancia_salida=horario.tolerancia_salida,
            activo=horario.activo
        )
        
        db.add(db_horario)
        db.commit()
        db.refresh(db_horario)
        
        logger.info(f"Horario creado: {db_horario.nombre}")
        return db_horario
    
    @staticmethod
    def obtener_horario(db: Session, horario_id: int) -> Optional[Horario]:
        """
        Obtiene un horario por su ID
        """
        return db.query(Horario).filter(Horario.id == horario_id).first()
    
    @staticmethod
    def obtener_horarios(db: Session, activo: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Horario]:
        """
        Obtiene lista de horarios con paginación
        """
        query = db.query(Horario)
        
        if activo is not None:
            query = query.filter(Horario.activo == activo)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_horario(db: Session, horario_id: int, horario_update: HorarioUpdate) -> Optional[Horario]:
        """
        Actualiza un horario existente
        """
        db_horario = HorarioService.obtener_horario(db, horario_id)
        
        if not db_horario:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = horario_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_horario, field, value)
        
        db_horario.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_horario)
        
        logger.info(f"Horario actualizado: {db_horario.id}")
        return db_horario
    
    @staticmethod
    def eliminar_horario(db: Session, horario_id: int) -> bool:
        """
        Elimina un horario
        """
        db_horario = HorarioService.obtener_horario(db, horario_id)
        
        if not db_horario:
            return False
        
        db.delete(db_horario)
        db.commit()
        
        logger.info(f"Horario eliminado: {horario_id}")
        return True

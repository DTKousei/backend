"""
Router de Sincronización
Endpoints para sincronización de hora y estado
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from models.database import get_db
from services.sincronizacion_service import SincronizacionService

router = APIRouter(prefix="/api/sincronizacion", tags=["Sincronización"])


@router.post("/hora/{dispositivo_id}")
def sincronizar_hora(
    dispositivo_id: int,
    nueva_hora: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Sincroniza la hora del dispositivo con la hora del sistema o una hora específica
    
    - **dispositivo_id**: ID del dispositivo
    - **nueva_hora**: Hora a establecer (opcional, por defecto usa hora del sistema)
    """
    resultado = SincronizacionService.sincronizar_hora_dispositivo(db, dispositivo_id, nueva_hora)
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    return resultado


@router.get("/estado")
def obtener_estado_sincronizacion(db: Session = Depends(get_db)):
    """
    Obtiene el estado de sincronización de todos los dispositivos activos
    """
    return SincronizacionService.obtener_estado_sincronizacion(db)

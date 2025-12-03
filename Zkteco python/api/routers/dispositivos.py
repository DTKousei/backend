"""
Router de Dispositivos
Endpoints para gestión de dispositivos ZKTeco
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from schemas.dispositivo import (
    DispositivoCreate,
    DispositivoUpdate,
    DispositivoResponse,
    DispositivoTestConexion,
    DispositivoInfo
)
from services.dispositivo_service import DispositivoService

router = APIRouter(prefix="/api/dispositivos", tags=["Dispositivos"])


@router.post("/", response_model=DispositivoResponse, status_code=status.HTTP_201_CREATED)
def crear_dispositivo(dispositivo: DispositivoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo dispositivo ZKTeco en el sistema
    """
    return DispositivoService.crear_dispositivo(db, dispositivo)


@router.get("/", response_model=List[DispositivoResponse])
def listar_dispositivos(
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los dispositivos con paginación
    """
    return DispositivoService.obtener_dispositivos(db, skip=skip, limit=limit, activo=activo)


@router.get("/{dispositivo_id}", response_model=DispositivoResponse)
def obtener_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un dispositivo específico por ID
    """
    dispositivo = DispositivoService.obtener_dispositivo(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo {dispositivo_id} no encontrado"
        )
    return dispositivo


@router.put("/{dispositivo_id}", response_model=DispositivoResponse)
def actualizar_dispositivo(
    dispositivo_id: int,
    dispositivo_update: DispositivoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un dispositivo existente
    """
    dispositivo = DispositivoService.actualizar_dispositivo(db, dispositivo_id, dispositivo_update)
    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo {dispositivo_id} no encontrado"
        )
    return dispositivo


@router.delete("/{dispositivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Elimina un dispositivo del sistema
    """
    if not DispositivoService.eliminar_dispositivo(db, dispositivo_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo {dispositivo_id} no encontrado"
        )


@router.post("/{dispositivo_id}/test-conexion", response_model=DispositivoTestConexion)
def test_conexion(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Prueba la conexión con el dispositivo ZKTeco
    """
    resultado = DispositivoService.test_conexion(db, dispositivo_id)
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=resultado["message"]
        )
    return resultado


@router.get("/{dispositivo_id}/info", response_model=DispositivoInfo)
def obtener_info_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Obtiene información detallada del dispositivo desde ZKTeco
    """
    info = DispositivoService.obtener_informacion_dispositivo(db, dispositivo_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo obtener información del dispositivo"
        )
    return info

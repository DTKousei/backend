"""
Router de Asistencias
Endpoints para gestión de registros de asistencia
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from models.database import get_db
from schemas.asistencia import (
    AsistenciaResponse,
    AsistenciaFilter,
    AsistenciaSincronizacion,
    AsistenciaDiariaResponse,
    AsistenciaManualCreate
)
from services.asistencia_service import AsistenciaService

router = APIRouter(prefix="/api/asistencias", tags=["Asistencias"])


@router.get("/", response_model=List[AsistenciaResponse])
def obtener_asistencias(
    user_id: Optional[str] = None,
    dispositivo_id: Optional[int] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Obtiene registros de asistencia con filtros opcionales
    
    - **user_id**: Filtrar por ID de usuario
    - **dispositivo_id**: Filtrar por dispositivo
    - **fecha_inicio**: Fecha de inicio del rango
    - **fecha_fin**: Fecha de fin del rango
    - **limit**: Límite de registros (máximo 10000)
    - **offset**: Offset para paginación
    """
    filtros = AsistenciaFilter(
        user_id=user_id,
        dispositivo_id=dispositivo_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=limit,
        offset=offset
    )
    
    return AsistenciaService.obtener_asistencias(db, filtros)


@router.get("/count")
def contar_asistencias(
    user_id: Optional[str] = None,
    dispositivo_id: Optional[int] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Cuenta el total de asistencias que coinciden con los filtros
    """
    filtros = AsistenciaFilter(
        user_id=user_id,
        dispositivo_id=dispositivo_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=1,
        offset=0
    )
    
    total = AsistenciaService.contar_asistencias(db, filtros)
    return {"total": total}


@router.get("/tiempo-real/{dispositivo_id}", response_model=List[AsistenciaResponse])
def obtener_asistencias_tiempo_real(
    dispositivo_id: int,
    ultimos_minutos: int = Query(5, ge=1, le=60, description="Últimos N minutos"),
    db: Session = Depends(get_db)
):
    """
    Obtiene asistencias en tiempo real (últimos N minutos)
    """
    return AsistenciaService.obtener_asistencias_tiempo_real(db, dispositivo_id, ultimos_minutos)


@router.post("/sincronizar/{dispositivo_id}", response_model=AsistenciaSincronizacion)
def sincronizar_asistencias(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Sincroniza asistencias desde el dispositivo ZKTeco a la base de datos
    """
    resultado = AsistenciaService.sincronizar_asistencias_desde_dispositivo(db, dispositivo_id)
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    return resultado


@router.post("/sincronizar-todos")
def sincronizar_todos_dispositivos(db: Session = Depends(get_db)):
    """
    Sincroniza asistencias de todos los dispositivos activos
    """
    from models.dispositivo import Dispositivo
    
    dispositivos = db.query(Dispositivo).filter(Dispositivo.activo == True).all()
    resultados = []
    
    for dispositivo in dispositivos:
        resultado = AsistenciaService.sincronizar_asistencias_desde_dispositivo(db, dispositivo.id)
        resultados.append({
            "dispositivo_id": dispositivo.id,
            "dispositivo_nombre": dispositivo.nombre,
            **resultado
        })
    
    return {
        "total_dispositivos": len(dispositivos),
        "resultados": resultados
    }

@router.post("/registrar", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
def registrar_asistencia_manual(
    datos: AsistenciaManualCreate,
    db: Session = Depends(get_db)
):
    """
    Registra manualmente una entrada o salida:
    - ENTRADA: Valida que no exista entrada previa sin cerrar.
    - SALIDA: Valida que exista una entrada abierta.
    """
    try:
        return AsistenciaService.registrar_manual(db, datos)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.delete("/{dispositivo_id}/limpiar")
def limpiar_asistencias_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Limpia todas las asistencias del dispositivo ZKTeco
    ¡ADVERTENCIA! Esta operación es irreversible
    """
    resultado = AsistenciaService.limpiar_asistencias_dispositivo(db, dispositivo_id)
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    return resultado


# Endpoints de Reportes y Cálculo

@router.post("/calcular", status_code=status.HTTP_200_OK)
def calcular_asistencia(
    fecha_inicio: date,
    fecha_fin: date,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Calcula o recalcula la asistencia diaria procesada para un rango de fechas.
    """
    resultados = AsistenciaService.calcular_rango_asistencia(db, fecha_inicio, fecha_fin, user_id)
    return {"message": "Cálculo completado", "dias_procesados": len(resultados)}

@router.get("/reporte", response_model=List[AsistenciaDiariaResponse])
def obtener_reporte_asistencia(
    fecha_inicio: date,
    fecha_fin: date,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el reporte procesado de asistencia diaria.
    """
    return AsistenciaService.obtener_reporte(db, fecha_inicio, fecha_fin, user_id)

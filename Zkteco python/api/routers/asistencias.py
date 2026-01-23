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
    AsistenciaManualCreate,
    ReporteUsuarioConResumen,
    ResumenAsistencia
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
    Sincroniza asistencias desde el dispositivo ZKTeco a la base de datos (TODO EL HISTORIAL)
    """
    resultado = AsistenciaService.sincronizar_asistencias_desde_dispositivo(db, dispositivo_id)
    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )
    return resultado


@router.post("/sincronizar-hoy/{dispositivo_id}", response_model=AsistenciaSincronizacion)
def sincronizar_asistencias_hoy(dispositivo_id: int, db: Session = Depends(get_db)):
    """
    Sincroniza asistencias desde el dispositivo ZKTeco a la base de datos (SOLO DÍA ACTUAL)
    """
    resultado = AsistenciaService.sincronizar_asistencias_hoy(db, dispositivo_id)
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


@router.get("/usuario/{user_id}/diario", response_model=ReporteUsuarioConResumen)
def obtener_reporte_diario_usuario(
    user_id: str,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    """
    Obtiene el reporte detallado para un usuario con resumen de totales.
    """
    # 1. Obtener detalle (lista plana)
    detalle = AsistenciaService.obtener_reporte(db, fecha_inicio, fecha_fin, user_id)
    
    # 2. Calcular totales
    total_horas = 0.0
    total_extras = 0.0
    dias_trabajados = 0
    dias_falta = 0
    dias_tarde = 0
    
    for dia in detalle:
        # detalle es una lista de dicts (según nuestra última modificación del service)
        # o lista de objetos Pydantic si el service hubiera cambiado.
        # Asumimos dict por seguridad, o acceso atributo si es objeto.
        # El service devuelve DICT ahora.
        horas = dia.get("horas_trabajadas", 0) or 0
        esperadas = dia.get("horas_esperadas", 0) or 0
        estado = dia.get("estado_asistencia", "")
        
        horas_float = float(horas)
        esperadas_float = float(esperadas)
        
        total_horas += horas_float
        
        # Calcular extra del día: si trabajó más de lo esperado
        extra_dia = max(0, horas_float - esperadas_float)
        total_extras += extra_dia
        
        if horas_float > 0:
            dias_trabajados += 1
            
        if "FALTA" in estado.upper():
            dias_falta += 1
        elif "TARDE" in estado.upper():
            dias_tarde += 1
    
    # helper formateo
    def fmt(h):
        if h is None: return "00:00"
        hours = int(h)
        minutes = int(round((h - hours) * 60))
        return f"{hours:02d}:{minutes:02d}"

    resumen = ResumenAsistencia(
        total_horas_trabajadas=round(total_horas, 2),
        total_horas_trabajadas_formato=fmt(total_horas),
        total_horas_extras=round(total_extras, 2),
        total_horas_extras_formato=fmt(total_extras),
        dias_trabajados=dias_trabajados,
        dias_falta=dias_falta,
        dias_tarde=dias_tarde
    )
    
    return ReporteUsuarioConResumen(
        resumen=resumen,
        detalle=detalle
    )


from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import requests
import logging

router = APIRouter(
    prefix="/api/asistencias",
    tags=["asistencias"]
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL del API externo (Main API)
EXTERNAL_API_URL = "http://localhost:8000/api/asistencias/reporte"

@router.get("/reporte")
def get_attendance_report(
    fecha_inicio: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    """
    Obtiene un reporte estadístico de asistencia consumiendo el API principal.
    Calcula:
    - Puntualidad (Estado 'PRESENTE')
    - Tardanzas (Estado 'TARDANZA')
    - Faltas (Estado 'FALTA')
    - Horas Extras (Entero: Suma de (horas_trabajadas - horas_esperadas) > 0)
    """
    try:
        # 1. Consumir API Externa
        response = requests.get(EXTERNAL_API_URL, params={
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })
        response.raise_for_status()
        records = response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error consumiendo API externa: {e}")
        raise HTTPException(status_code=503, detail=f"Error obteniendo datos de asistencia: {str(e)}")

    # 2. Procesar y Agrupar Datos
    employee_stats: Dict[str, Dict[str, Any]] = {}
    
    for record in records:
        user_id = record.get("user_id")
        if not user_id:
            continue
            
        if user_id not in employee_stats:
            employee_stats[user_id] = {
                "user_id": user_id,
                # "nombre": "N/A", # El API externo no parece devolver nombre en el ejemplo
                "puntual": 0,
                "tardanzas": 0,
                "faltas": 0,
                "horas_extras": 0.0, # Acumulador float
                "total_dias": 0
            }
            
        stats = employee_stats[user_id]
        stats["total_dias"] += 1
        
        # Estado
        estado = str(record.get("estado_asistencia", "")).upper().strip()
        
        if estado == "PRESENTE":
            stats["puntual"] += 1
        elif estado in ["TARDANZA", "TARDE"]:
            stats["tardanzas"] += 1
        elif estado in ["FALTA", "AUSENTE"]:
            stats["faltas"] += 1
        else:
             # Log unknown status for debugging
             logger.warning(f"Estado de asistencia desconocido: {estado} para usuario {user_id}")
            
        # Horas Extras
        horas_esp = float(record.get("horas_esperadas", 0) or 0)
        horas_trab = float(record.get("horas_trabajadas", 0) or 0)
        
        if horas_trab > horas_esp:
            overtime = horas_trab - horas_esp
            stats["horas_extras"] += overtime

    # 3. Formatear Resultados y Calcular Totales Globales
    results = []
    global_totals = {
        "puntual": 0,
        "tardanzas": 0,
        "faltas": 0,
        "horas_extras": 0
    }

    for uid, stats in employee_stats.items():
        # Convertir horas extras a entero según requerimiento
        stats["horas_extras"] = int(stats["horas_extras"])
        
        # Acumular globales
        global_totals["puntual"] += stats["puntual"]
        global_totals["tardanzas"] += stats["tardanzas"]
        global_totals["faltas"] += stats["faltas"]
        global_totals["horas_extras"] += stats["horas_extras"]
        
        results.append(stats)
    
    return {
        "rango": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "totales": global_totals, # Suma total de todos los casos
        "total_empleados": len(results),
        "data": results
    }

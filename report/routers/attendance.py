from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from services.data_fetcher import fetch_sabana_data
import logging

router = APIRouter(
    prefix="/api/asistencias",
    tags=["asistencias"]
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {date_str}. Use YYYY-MM-DD")

@router.get("/reporte")
def get_attendance_report(
    fecha_inicio: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    """
    Obtiene un reporte estadístico de asistencia para un rango de fechas.
    Calcula puntualidad, tardanzas, faltas, horas extras y justificaciones.
    """
    start_date = parse_date(fecha_inicio)
    end_date = parse_date(fecha_fin)
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin.")

    # Identificar los meses involucrados para hacer las peticiones necesarias
    # fetch_sabana_data requiere mes y año. Si el rango cruza meses, necesitamos llamar varias veces.
    # Por simplicidad y eficiencia, iteraremos por cada mes único en el rango.
    
    months_to_fetch = set()
    curr = start_date
    while curr <= end_date:
        months_to_fetch.add((curr.year, curr.month))
        # Avanzar al primer día del siguiente mes para evitar iterar día por día ineficientemente
        if curr.month == 12:
            curr = datetime(curr.year + 1, 1, 1)
        else:
            curr = datetime(curr.year, curr.month + 1, 1)
            
    # Estructura acumulada por empleado (clave: DNI/user_id)
    employee_stats = {}
    
    # Códigos de asistencia (Basado en análisis previo)
    CODES_PUNTUAL = ["A", "T/R"] # Asistido, Trabajo Remoto
    CODES_TARDANZA = ["T", "TAR"] # Tardanza
    CODES_FALTA = ["FAL", "A/B"] # Falta, Abandono
    CODES_HORAS_EXTRAS = ["HE"] # Horas Extras
    CODES_JUSTIFICADOS = ["C/S", "ONO", "LS/G", "P/E", "L/S", "P/I", "P/C", "P/S", "L/F", "C/J", "OMI", "JUST"]

    for year, month in months_to_fetch:
        try:
            # Obtener datos del mes completo
            data = fetch_sabana_data(str(month), str(year))
            employees = data.get("data", [])
            
            for emp in employees:
                user_id = emp.get("user_id")
                
                # Inicializar estadísticas para el empleado si es la primera vez que lo vemos
                if user_id not in employee_stats:
                    employee_stats[user_id] = {
                        "user_id": user_id,
                        "nombre": emp.get("nombre"),
                        "puntual": 0,
                        "tardanzas": 0,
                        "faltas": 0,
                        "horas_extras": 0,
                        "justificaciones": 0,
                        "total_dias": 0 # Días en el rango solicitado
                    }
                
                asistencia_dias = emp.get("asistencia_dias", [])
                
                # Iterar sobre los días del mes y verificar si caen en el rango
                # asistencia_dias es una lista donde índice 0 = día 1 del mes
                for day_idx, status in enumerate(asistencia_dias):
                    day_num = day_idx + 1
                    try:
                        current_date_check = datetime(year, month, day_num)
                    except ValueError:
                        continue # Día inválido (ej. 30 de febrero)
                        
                    # Verificar si la fecha actual está dentro del rango solicitado
                    if start_date <= current_date_check <= end_date:
                        stats = employee_stats[user_id]
                        stats["total_dias"] += 1
                        
                        status_upper = str(status).upper().strip()
                        
                        if status_upper in CODES_PUNTUAL:
                            stats["puntual"] += 1
                        elif status_upper in CODES_TARDANZA:
                            stats["tardanzas"] += 1
                        elif status_upper in CODES_FALTA:
                            stats["faltas"] += 1
                        elif status_upper in CODES_HORAS_EXTRAS:
                            stats["horas_extras"] += 1
                        elif status_upper in CODES_JUSTIFICADOS:
                            stats["justificaciones"] += 1
                            
        except Exception as e:
            logger.error(f"Error procesando datos para {month}/{year}: {e}")
            # Continuamos con el siguiente mes si falla uno
            continue

    # Convertir a lista para la respuesta JSON
    results = list(employee_stats.values())
    
    return {
        "rango": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "total_empleados": len(results),
        "data": results
    }

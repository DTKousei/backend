from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from calendar import monthrange
from datetime import date
from typing import List, Dict, Any, Optional
from models.usuario import Usuario
from models.reportes import AsistenciaDiaria
from models.horario import Horario # Potentially needed for labels or checking non-working days
# Si Horario logic is needed for "Feriado" vs "Domingo", we might need more logic here.
# For now relying on AsistenciaDiaria.estado_asistencia or simple calendar logic.

class ReporteService:
    """
    Servicio para la generación de reportes complejos como la Sábana de Asistencia.
    """

    # Diccionario de Códigos Cortos
    CODIGOS_ASISTENCIA = {
        "PRESENTE": "A",
        "TARDE": "T",
        "FALTA": "FAL",
        "FERIADO": "FER",
        "VACACIONES": "VAC",
        "LICENCIA": "L/S",      # Licencia sin goce (ejemplo)
        "LICENCIA_GO": "L/C",   # Licencia con goce
        "COMISION": "C/S",      # Comisión de servicio
        "PERMISO": "PER",
        "DESCANSO": "D"         # Descanso médico o semanal
    }

    @staticmethod
    def _obtener_codigo_corto(estado: str) -> str:
        """Devuelve el código corto para un estado dado."""
        if not estado:
            return "FAL"
        
        estado_upper = estado.upper()
        # Busqueda directa
        if estado_upper in ReporteService.CODIGOS_ASISTENCIA:
            return ReporteService.CODIGOS_ASISTENCIA[estado_upper]
        
        # Búsquedas parciales o mapeos extra
        if "LICENCIA" in estado_upper:
            return "L/S" # Default a Licencia
        if "COMIS" in estado_upper:
            return "C/S"
        if "PERMISO" in estado_upper:
            return "PER"
        if "VACACION" in estado_upper:
            return "VAC"
        
        return "FAL" # Default si no se reconoce

    @staticmethod
    def obtener_sabana_asistencia(
        db: Session, 
        anio: int, 
        mes: int, 
        user_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Genera la data para la Sábana de Asistencia (Matrix Report).
        """
        
        # 1. Definir rango del mes
        _, num_dias = monthrange(anio, mes)
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = date(anio, mes, num_dias)
        
        # 2. Obtener Empleados
        query_users = db.query(Usuario).order_by(Usuario.nombre)
        if user_ids:
            query_users = query_users.filter(Usuario.user_id.in_(user_ids))
        
        empleados = query_users.all()
        
        # 3. Obtener Registros de AsistenciaDiaria para el mes
        query_asis = db.query(AsistenciaDiaria).filter(
            extract('year', AsistenciaDiaria.fecha) == anio,
            extract('month', AsistenciaDiaria.fecha) == mes
        )
        if user_ids:
            # Filtrar por user_id (string) de los usuarios seleccionados
            # Ojo: Usuario.id es int, AsistenciaDiaria.user_id es str (from device)
            # Necesitamos los user_id strings de los empleados filtrados
            user_ids_str = [emp.user_id for emp in empleados]
            query_asis = query_asis.filter(AsistenciaDiaria.user_id.in_(user_ids_str))
            
        registros = query_asis.all()
        
        # 4. Indexar registros para acceso rápido: (user_id_str, dia_del_mes) -> AsistenciaDiaria
        map_registros = {}
        for reg in registros:
            dia = reg.fecha.day
            map_registros[(reg.user_id, dia)] = reg

        # 5. Construir Estructura de Respuesta
        
        # Metadatos del mes
        dias_semana_nombres = ["L", "M", "M", "J", "V", "S", "D"]
        columnas_dias = []
        for d in range(1, num_dias + 1):
            fecha_actual = date(anio, mes, d)
            nombre_dia = dias_semana_nombres[fecha_actual.weekday()]
            columnas_dias.append({
                "dia": d,
                "nombre_dia": nombre_dia,
                "es_fin_de_semana": fecha_actual.weekday() >= 4 # 5=Sabado, 6=Domingo
            })

        data_empleados = []
        
        for emp in empleados:
            asistencia_dias = []
            stats = {
                "dias_lab": 0, # Días laborados (Presente)
                "tardanzas": 0,
                "faltas": 0,
                "licencias": 0
            }
            
            for d in range(1, num_dias + 1):
                key = (emp.user_id, d)
                codigo = ""
                
                if key in map_registros:
                    reg = map_registros[key]
                    estado = reg.estado_asistencia
                    codigo = ReporteService._obtener_codigo_corto(estado)
                    
                    # Calcular estadisticas
                    if codigo == "A":
                        stats["dias_lab"] += 1
                    elif codigo == "T":
                        stats["tardanzas"] += 1
                        stats["dias_lab"] += 1 # Tarde cuenta como laborado generalmente? O separado. Lo contaremos como asistencia pero con tardanza.
                    elif codigo == "FAL":
                        stats["faltas"] += 1
                    elif codigo in ["L/S", "C/S", "VAC", "PER"]:
                        stats["licencias"] += 1
                else:
                    # No hay registro. Validar si es fin de semana o falta.
                    # Por defecto falta si no hay registro, o "-" si es domingo?
                    # Según requerimiento: "Si no hay registro en un día pasado, debe marcarse como "FAL" o "-""
                    fecha_iter = date(anio, mes, d)
                    if fecha_iter.weekday() == 6: # Domingo
                        codigo = "D" # Domingo/Descanso
                    else:
                         # Revisar si fecha_iter > hoy (futuro)
                        if fecha_iter > date.today():
                            codigo = "" # Futuro
                        else:
                            codigo = "FAL"
                            stats["faltas"] += 1
                
                asistencia_dias.append(codigo)
            
            data_empleados.append({
                "empleado_id": emp.id,
                "nombre": emp.nombre,
                "user_id": emp.user_id,
                "departamento": emp.departamento,
                "asistencia_dias": asistencia_dias,
                "resumen": stats
            })

        return {
            "meta": {
                "mes": mes,
                "anio": anio,
                "dias_total": num_dias
            },
            "columnas_dias": columnas_dias,
            "data": data_empleados
        }

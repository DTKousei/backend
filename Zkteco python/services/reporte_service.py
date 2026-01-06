from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from calendar import monthrange
from datetime import date
from typing import List, Dict, Any, Optional
from models.usuario import Usuario
from models.reportes import AsistenciaDiaria
from models.horario import Horario # Potentially needed for labels or checking non-working days
from models.turnos import AsignacionHorario, SegmentosHorario # Models for checking schedule
from sqlalchemy import or_
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
        user_ids: Optional[List[str]] = None,
        area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera la data para la Sábana de Asistencia (Matrix Report).
        """
        
        # 0. Registrar Generación de Reporte (Auditoria basica)
        # Nota: Idealmente esto va al final o en bloque try/finally, pero para simplicidad lo registramos aqui
        # Si no existe la tabla aun, saltar este paso. (Ya la creamos en models/reportes.py)
        try:
            from models.reportes import ReportesGenerados
            nuevo_reporte = ReportesGenerados(
                tipo_reporte="Sabana",
                anio=anio,
                mes=mes,
                area=area
            )
            db.add(nuevo_reporte)
            db.commit()
        except Exception as e:
            print(f"Advertencia: No se pudo registrar el historial de reporte: {e}")
            db.rollback()

        # 1. Definir rango del mes
        _, num_dias = monthrange(anio, mes)
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = date(anio, mes, num_dias)
        
        # 2. Obtener Empleados
        query_users = db.query(Usuario).order_by(Usuario.nombre)
        
        # 2.1 Filtrar por Departamento (Area)
        if area:
            from models.departamento import Departamento
            # Hacemos join y filtramos por nombre de departamento
            query_users = query_users.join(Usuario.departamento_rel).filter(Departamento.nombre == area)
        
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

        # 4.5 Obtener Horarios y Asignaciones
        # Necesitamos saber qué horario tenía asignado cada usuario en cada día del mes
        
        # A) Obtener Asignaciones que se solapen con el mes
        # Rango del mes: fecha_inicio a fecha_fin
        
        # IDs de usuarios (strings) que estamos procesando
        user_ids_filtro = [e.user_id for e in empleados]
        
        query_asig = db.query(AsignacionHorario).filter(
            AsignacionHorario.user_id.in_(user_ids_filtro),
            AsignacionHorario.fecha_inicio <= fecha_fin,
            or_(
                AsignacionHorario.fecha_fin == None,
                AsignacionHorario.fecha_fin >= fecha_inicio
            )
        )
        asignaciones = query_asig.all()
        
        # Mapa: user_id -> lista de asignaciones
        map_asignaciones = {}
        horario_ids_involucrados = set()
        
        for asig in asignaciones:
            if asig.user_id not in map_asignaciones:
                map_asignaciones[asig.user_id] = []
            map_asignaciones[asig.user_id].append(asig)
            horario_ids_involucrados.add(asig.horario_id)
            
        # B) Obtener Segmentos de los horarios involucrados
        segmentos = db.query(SegmentosHorario).filter(
            SegmentosHorario.horario_id.in_(list(horario_ids_involucrados))
        ).all()
        
        # Mapa: horario_id -> set de dias laborales (integers 0-6)
        map_dias_laborables = {}
        for seg in segmentos:
            if seg.horario_id not in map_dias_laborables:
                map_dias_laborables[seg.horario_id] = set()
            map_dias_laborables[seg.horario_id].add(seg.dia_semana)

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
                "es_fin_de_semana": fecha_actual.weekday() >= 5 # 5=Sabado, 6=Domingo
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
                    # No hay registro. Validar si es día laboral según horario.
                    fecha_iter = date(anio, mes, d)
                    
                    # 1. Buscar horario activo en fecha_iter
                    horario_activo_id = None
                    # Recorrer asignaciones del empleado
                    # Se asume que no hay solapamientos. Tomamos el primero que coincida.
                    if emp.user_id in map_asignaciones:
                        for asignacion in map_asignaciones[emp.user_id]:
                            fin_valido = asignacion.fecha_fin is None or asignacion.fecha_fin >= fecha_iter
                            inicio_valido = asignacion.fecha_inicio <= fecha_iter
                            
                            if inicio_valido and fin_valido:
                                horario_activo_id = asignacion.horario_id
                                break
                    
                    # 2. Verificar si es día laborable en ese horario
                    es_dia_laborable = False
                    if horario_activo_id and horario_activo_id in map_dias_laborables:
                        dias_lab_set = map_dias_laborables[horario_activo_id]
                        dia_semana_actual = fecha_iter.weekday() # 0=Lun, 6=Dom
                        if dia_semana_actual in dias_lab_set:
                            es_dia_laborable = True
                    
                    # 3. Determinar estado
                    # Si no tiene horario asignado, asumimos que no trabaja => Descanso (D)
                    # Si tiene horario y es día laborable => FALTA
                    # Si tiene horario y NO es día laborable => Descanso (D)
                    
                    if fecha_iter > date.today():
                        codigo = "" # Futuro
                    elif es_dia_laborable:
                        codigo = "FAL"
                        stats["faltas"] += 1
                    else:
                        # Usar inicial del día para Descanso/No Laborable
                        # 0=L, 1=M, 2=M, 3=J, 4=V, 5=S, 6=D
                        iniciales_dias = ["L", "M", "M", "J", "V", "S", "D"]
                        dia_semana_actual = fecha_iter.weekday()
                        codigo = iniciales_dias[dia_semana_actual]
                
                asistencia_dias.append(codigo)
            
            data_empleados.append({
                "empleado_id": emp.id,
                "nombre": emp.nombre,
                "user_id": emp.user_id,
                "departamento": emp.departamento_rel.nombre if emp.departamento_rel else "Sin Departamento",
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

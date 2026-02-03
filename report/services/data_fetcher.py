import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import calendar

load_dotenv()

# Basic Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
INCIDENCIAS_API_URL = os.getenv("INCIDENCIAS_API_URL", "http://localhost:3003/api/incidencias")

def fetch_incidencias():
    """
    Fetches incidences from the external API.
    Returns a list of approved incidences.
    """
    try:
        # Assuming we want all or filtering by date isn't strictly defined yet so we fetch generic list
        # If the API supports pagination, we might need ?limit=1000 or similar.
        response = requests.get(f"{INCIDENCIAS_API_URL}?limit=1000")
        response.raise_for_status()
        data = response.json()
        
        # The structure is {"data": [...], "pagination": {...}}
        incidencias = data.get("data", [])
        
        # Filter for Approved incidences only
        # User example: "estado": {"nombre": "Rechazado"}
        # We need "estado": {"nombre": "Aprobado"} (or check ID if known, but name is safer for now)
        approved = [
            inc 
            for inc in incidencias 
            if inc.get("estado", {}).get("nombre", "").upper() == "APROBADO"
        ]
        return approved
    except Exception as e:
        print(f"Error fetching incidences: {e}")
        return []

def is_date_in_range(target_date_str, start_str, end_str):
    """
    Checks if a date string YYYY-MM-DD is within the ISO start/end range.
    """
    try:
        # Target: YYYY-MM-DD
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        
        # Ranges: ISO 8601 (e.g., 2026-01-06T00:00:00.000Z)
        # We handle potential Z or offset by just slicing first 10 chars YYYY-MM-DD for simple comparison
        start = datetime.strptime(start_str[:10], "%Y-%m-%d")
        end = datetime.strptime(end_str[:10], "%Y-%m-%d")
        
        return start <= target <= end
    except Exception:
        return False

def fetch_sabana_data(mes: str, anio: str, user_ids: list[str] = None, area: str = None):
    """
    Obtains attendance data consuming the main API and enriches it with incidences.
    """
    url = f"{API_BASE_URL}/reportes/sabana"
    payload = {
        "mes": mes,
        "anio": anio
    }
    
    if user_ids:
        payload["user_ids"] = user_ids
        
    if area:
        payload["area"] = area

    try:
        # 1. Fetch Basic Attendance Data
        response = requests.post(url, json=payload)
        response.raise_for_status()
        report_data = response.json()
        
        # 2. Fetch Incidences
        try:
            incidencias = fetch_incidencias()
        except Exception as e:
            print(f"Warning: Could not fetch incidences: {e}")
            incidencias = []
            
        # 3. Merge Logic
        # Dictionary 'data' is the list of employees
        employees = report_data.get("data", [])
        
        # Calculate number of days in the month to iterate correctly
        try:
            num_days = calendar.monthrange(int(anio), int(mes))[1]
        except:
            num_days = 31

        for emp in employees:
            emp_dni = emp.get("user_id") # Assuming user_id is the DNI
            asistencia = emp.get("asistencia_dias", [])
            
            # Find incidences for this employee
            emp_incidencias = [inc for inc in incidencias if inc.get("empleado_id") == emp_dni]
            
            if not emp_incidencias:
                continue
                
            # Iterate through days in the report
            for day_idx in range(len(asistencia)):
                status = asistencia[day_idx]
                
                # Only justify 'FAL' (Absence)
                # Note: Adjust logic if other statuses should be justified too.
                if status == "FAL":
                    dia_num = day_idx + 1
                    date_str = f"{anio}-{str(mes).zfill(2)}-{str(dia_num).zfill(2)}"
                    
                    # Check overlap
                    for inc in emp_incidencias:
                        f_inicio = inc.get("fecha_inicio")
                        f_fin = inc.get("fecha_fin")
                        
                        if f_inicio and f_fin and is_date_in_range(date_str, f_inicio, f_fin):
                            # Replace with incidence code
                            # structure: "tipo_incidencia": {"codigo": "PM001", ...}
                            tipo = inc.get("tipo_incidencia", {})
                            code = tipo.get("codigo", "JUST") # Fallback code
                            
                            # Update the status in the list
                            asistencia[day_idx] = code
                            
                            # Actualizar contadores en el resumen
                            resumen = emp.get("resumen", {})
                            
                            # 1. Siempre restar de Faltas porque ya está justificado
                            # Aseguramos que no baje de 0
                            resumen["faltas"] = max(0, resumen.get("faltas", 0) - 1)

                            # 2. Sumar a Días Laborables SI NO ES 'LS/G'
                            # El usuario indica que LS/G no cuenta como laborable, el resto (VAC, L/S, etc) sÍ.
                            if code != "LS/G":
                                resumen["dias_lab"] = resumen.get("dias_lab", 0) + 1
                                
                            # Guardamos cambios en el dict resumen (aunque al ser mutable se actualiza en emp)
                            emp["resumen"] = resumen

                            break # Justified, move to next day
                            
        return report_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining data: {e}")
        raise

def fetch_saldos_incidencias(anio: int, empleado_id: str = None):
    """
    Fetches incidence balances (saldos) and enriches with employee names.
    Calls:
      1. Main API (Users) -> Map user_id to name
      2. Incidences API (Saldos) -> Get balances
    """
    try:
        # 1. Fetch Users
        # API_BASE_URL is http://localhost:8000/api
        resp_users = requests.get(f"{API_BASE_URL}/usuarios?limit=2000") # High limit to get all
        resp_users.raise_for_status()
        users_list = resp_users.json()
        
        # Map user_id -> User Info
        users_map = {}
        for u in users_list:
            # Check user_id field. The API returns user_id as string (DNI usually).
            uid = u.get("user_id")
            if uid:
                users_map[uid] = u

        # 2. Fetch Saldos
        # INCIDENCIAS_API_URL is http://localhost:3003/api/incidencias
        url = f"{INCIDENCIAS_API_URL}/saldos"
        params = {"anio": anio}
        if empleado_id:
            params["empleado_id"] = empleado_id
            
        resp_saldos = requests.get(url, params=params)
        resp_saldos.raise_for_status()
        
        # Structure: {"anio": 2026, "data": [...]}
        payload = resp_saldos.json()
        saldos_data = payload.get("data", [])
        
        # 3. Enrich & Format
        enriched_results = []
        for item in saldos_data:
            emp_id = item.get("empleado_id")
            if not emp_id:
                continue
                
            user_info = users_map.get(emp_id, {})
            nombre = user_info.get("nombre", "SIN NOMBRE")
            
            # Add fields for report
            item["nombre_empleado"] = nombre
            item["dni"] = emp_id
            enriched_results.append(item)
            
        return enriched_results

    except Exception as e:
        print(f"Error fetching saldos: {e}")
        # Return empty list or raise depending on preference. 
        # Raising allows controller to handle 500.
        raise

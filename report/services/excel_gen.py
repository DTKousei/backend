import pandas as pd
import os
import uuid
from datetime import datetime
import xlsxwriter

# Establecer la configuración regional a español para los nombres de meses, etc.
import locale
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass # Fallback si no está disponible

STORAGE_DIR = "storage"

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def generate_excel_report(data: dict) -> str:
    """
    Genera un reporte detallado en Excel usando XlsxWriter con formato personalizado.
    Replica el diseño de la imagen proporcionada.
    """
    # 1. Metadata
    meta = data.get("meta", {})
    mes = meta.get("mes")
    anio = meta.get("anio")
    dias_total = meta.get("dias_total", 31)
    
    # 2. Columnas Días
    columnas_dias = data.get("columnas_dias", [])
    
    # 3. Empleados
    employees = data.get("data", [])
    
    # Generar Path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"reporte_asistencia_{anio}_{mes}_{timestamp}_{unique_id}.xlsx"
    file_path = os.path.join(STORAGE_DIR, filename)
    absolute_path = os.path.abspath(file_path)
    
    # Iniciar Workbook XlsxWriter
    workbook = xlsxwriter.Workbook(absolute_path)
    worksheet = workbook.add_worksheet(f"Asistencia_{mes}_{anio}")
    
    # --- ESTILOS ---
    
    # Titulo Principal
    style_title = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14
    })
    
    # Cabecera Tabla (Negrita, Borde, Centrado)
    style_header = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True,
        'bg_color': '#FFFFFF' 
    })
    
    # Días (Pequeño, Centrado, Borde)
    style_day_num = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 9
    })
    style_day_name = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 9
    })
    
    # Datos (Borde, Centrado)
    style_cell = workbook.add_format({
        'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 10
    })
    
    # Datos Texto Izquierda (Nombre)
    style_cell_left = workbook.add_format({
        'align': 'left', 'valign': 'vcenter', 'border': 1, 'font_size': 10
    })

    # Fin de Semana (Gris Claro)
    style_weekend = workbook.add_format({
        'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 10,
        'bg_color': '#D3D3D3'
    })
    
    # --- ESTRUCTURA ---
    
    # Filas de inicio
    START_ROW = 4
    
    # Títulos Superiores
    # RESUMEN DE ASISTENCIA DEL PERSONAL...
    worksheet.merge_range('A2:AM2', "RESUMEN DE ASISTENCIA DEL PERSONAL DE LA SEDE UGEL SUCRE", style_title)
    
    # Cabecera Compleja
    # Fila 4 (Indices 3): Encabezados principales
    
    # Col A: N° (Merged row 4-5)
    worksheet.merge_range(START_ROW-1, 0, START_ROW, 0, "N°", style_header)
    
    # Col B: APELLIDOS Y NOMBRES (Merged row 4-5)
    worksheet.merge_range(START_ROW-1, 1, START_ROW, 1, "APELLIDOS Y NOMBRES", style_header)
    
    # Col C: DNI (Merged row 4-5)
    worksheet.merge_range(START_ROW-1, 2, START_ROW, 2, "DNI", style_header)
    
    # Col D hasta AE (aprox): Días
    # Título del mes sobre los días: "NOVIEMBRE 2025 - PERS. CAS INDETERMINADO UGEL"
    # Calculamos rango de dias: Col 3 (D) hasta 3 + dias_total - 1
    last_day_col_idx = 3 + dias_total - 1
    
    # Lista de meses
    MESES = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    
    nombre_mes = mes
    try:
        mes_int = int(mes)
        if 1 <= mes_int <= 12:
            nombre_mes = MESES[mes_int - 1]
    except ValueError:
        pass # Si no es numérico, usa el valor original

    worksheet.merge_range(START_ROW-2, 3, START_ROW-2, last_day_col_idx, f"{nombre_mes} {anio} - PERSONAL ", style_title)
    
    # Días Cabecera Doble
    # Fila 4: Número de día (1, 2, 3...)
    # Fila 5: Inicial del día (S, D, L...)
    
    weekend_cols = []
    
    for i, dia_info in enumerate(columnas_dias):
        col_idx = 3 + i
        day_num = dia_info['dia']
        day_name = dia_info['nombre_dia']
        is_weekend = dia_info['es_fin_de_semana']
        
        if is_weekend:
            weekend_cols.append(col_idx)
            
        worksheet.write(START_ROW-1, col_idx, day_num, style_day_num)
        worksheet.write(START_ROW, col_idx, day_name, style_day_name)
        worksheet.set_column(col_idx, col_idx, 3) # Ancho columna dia estrecho
        
    # Columnas Totales al final
    # Despues de los dias:
    next_col = last_day_col_idx + 1
    
    # DIA MES
    worksheet.merge_range(START_ROW-1, next_col, START_ROW, next_col, "DIA\nMES", style_header)
    next_col += 1
    
    # DIAS NO LAB
    worksheet.merge_range(START_ROW-1, next_col, START_ROW, next_col, "DIAS\nNO\nLAB.", style_header)
    next_col += 1

    # TOTAL DIAS LAB
    worksheet.merge_range(START_ROW-1, next_col, START_ROW, next_col, "TOTAL\nDIAS\nLAB.", style_header)
    next_col += 1
    
    # TARDANZA
    worksheet.merge_range(START_ROW-1, next_col, START_ROW, next_col, "TARDANZA", style_header)
    
    # Ajustar ancho de columnas fijas
    worksheet.set_column(0, 0, 4)  # N°
    worksheet.set_column(1, 1, 35) # Nombres
    worksheet.set_column(2, 2, 12) # DNI
    
    # --- DATOS ---
    current_row = START_ROW + 1
    
    for idx, emp in enumerate(employees, start=1):
        # 0: N°
        worksheet.write(current_row, 0, idx, style_cell)
        # 1: Nombre
        worksheet.write(current_row, 1, emp.get("nombre", ""), style_cell_left)
        # 2: DNI
        worksheet.write(current_row, 2, emp.get("user_id", ""), style_cell)
        
        # Dias
        asistencia = emp.get("asistencia_dias", [])
        for i in range(dias_total):
            col_idx = 3 + i
            # Buscar estilo
            cell_style = style_weekend if col_idx in weekend_cols else style_cell
            
            valor = ""
            if i < len(asistencia):
                valor = asistencia[i]
                
            worksheet.write(current_row, col_idx, valor, cell_style)
            
        # Resumen
        resumen = emp.get("resumen", {})
        dias_lab = resumen.get("dias_lab", 0)
        tardanzas = resumen.get("tardanzas", 0)
        faltas = resumen.get("faltas", 0)
        
        # Totales (Simulados según imagen, ajustar lógica si es necesario)
        col_resumen = last_day_col_idx + 1
        
        # DIA MES (30 o 31)
        worksheet.write(current_row, col_resumen, dias_total, style_cell)
        
        # DIAS NO LAB (Faltas)
        # Corregido: Mostrar conteo de faltas
        worksheet.write(current_row, col_resumen+1, faltas if faltas > 0 else "", style_cell) 
        
        # TOTAL DIAS LAB
        worksheet.write(current_row, col_resumen+2, dias_lab, style_cell)
        
        # TARDANZA
        worksheet.write(current_row, col_resumen+3, tardanzas if tardanzas > 0 else "", style_cell)
        
        current_row += 1
        
    # --- LEYENDA (Footer) ---
    current_row += 2
    worksheet.write(current_row, 0, "OBS.", workbook.add_format({'bold': True}))
    
    # Escribir leyenda en columnas o bloques
    # A: ASISTIDOS, C/S: COMISION, FAL: FALTA, etc.
    leyenda = [
        ("A", "ASISTIDOS"),
        ("C/S", "COMISION DE SERVICIO"),
        ("FAL", "FALTA"),
        ("FER", "FERIADO"),
        ("ONO", "ONOMASTICO"),
        ("A/B", "ABANDONO"),
        ("LS/G", "LICENCIA SIN GOCE"),
        ("P/E", "PERMISO POR ELECCIONES"),
        ("L/S", "LICENCIA POR SALUD"),
        ("VAC", "VACACIONES"),
        ("P/I", "PERMISO INTERNO"),
        ("P/C", "PERMISO COMPENSATORIO"),
        ("T/R", "TRABAJO REMOTO"),
        ("P/S", "PERMISO POR SALUD"),
        ("L/F", "LICENCIA POR FALLECIMIENTO"),
        ("C/J", "CITACION JUDICIAL"),
        ("OMI", "OMISIÓN")
    ]
    
    # Imprimir leyenda en 2 columnas grandes (repartidas)
    start_legend_row = current_row + 1
    
    col_a_idx = 4
    col_b_idx = 15
    
    for i, (code, desc) in enumerate(leyenda):
        # Repartir mitad y mitad
        if i < len(leyenda) / 2:
            r = start_legend_row + i
            c_code = col_a_idx
            c_desc = col_a_idx + 2
        else:
            r = start_legend_row + (i - int(len(leyenda)/2))
            c_code = col_b_idx
            c_desc = col_b_idx + 2
            
        worksheet.write(r, c_code, code, workbook.add_format({'bold': True}))
        worksheet.write(r, c_desc, desc)

    # Footer Ciudad/Fecha
    fecha_footer = datetime.now().strftime("%d/%m/%Y")
    footer_text = f"Querobamba, {fecha_footer}"
    row_footer = start_legend_row + len(leyenda)//2 + 2
    worksheet.merge_range(row_footer, 0, row_footer, last_day_col_idx, footer_text, workbook.add_format({'align': 'center'}))

    # --- PROTECCIÓN ---
    worksheet.protect()

    workbook.close()
    return absolute_path

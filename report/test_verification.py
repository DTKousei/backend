import os
import sys
from services.excel_gen import generate_excel_report
from services.pdf_gen import generate_pdf_report

# Mock Data (based on user request)
MOCK_DATA = {
    "meta": {
        "mes": 1,
        "anio": 2025,
        "dias_total": 31
    },
    "columnas_dias": [
        {"dia": 1, "nombre_dia": "M", "es_fin_de_semana": False},
        {"dia": 2, "nombre_dia": "J", "es_fin_de_semana": False},
        {"dia": 3, "nombre_dia": "V", "es_fin_de_semana": False},
        {"dia": 4, "nombre_dia": "S", "es_fin_de_semana": True},
        {"dia": 5, "nombre_dia": "D", "es_fin_de_semana": True}
    ],
    "data": [
        {
            "empleado_id": 1,
            "nombre": "Test User",
            "user_id": "12345",
            "departamento": "IT",
            "asistencia_dias": ["A", "A", "A", "S", "D"],
            "resumen": {"dias_lab": 3, "tardanzas": 0, "faltas": 0, "licencias": 0}
        }
    ]
}

def test_generation():
    print("Testing Excel Generation...")
    try:
        excel_path = generate_excel_report(MOCK_DATA)
        if os.path.exists(excel_path):
            print(f"SUCCESS: Excel generated at {excel_path}")
        else:
            print("FAILURE: Excel file not found.")
    except Exception as e:
        print(f"FAILURE: Excel generation error: {e}")

    print("\nTesting PDF Generation...")
    try:
        pdf_path = generate_pdf_report(MOCK_DATA)
        if os.path.exists(pdf_path):
            print(f"SUCCESS: PDF generated at {pdf_path}")
        else:
            print("FAILURE: PDF file not found.")
    except Exception as e:
        print(f"FAILURE: PDF generation error: {e}")

if __name__ == "__main__":
    test_generation()

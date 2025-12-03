import ExcelJS from 'exceljs';
import { formatDateDDMMYYYY, formatTime } from '../utils/dateUtils.js';
import { ATTENDANCE_STATUS, PUNCH_TYPES } from '../config/constants.js';

class ExcelGeneratorService {
  /**
   * Genera un reporte de asistencia en formato Excel
   */
  async generateAttendanceReport(data, options = {}) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Reporte de Asistencia');

    // Configurar propiedades del documento
    workbook.creator = 'Sistema de Control de Asistencia';
    workbook.created = new Date();
    workbook.modified = new Date();

    // Título del reporte
    worksheet.mergeCells('A1:H1');
    const titleCell = worksheet.getCell('A1');
    titleCell.value = options.title || 'REPORTE DE ASISTENCIA';
    titleCell.font = { size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
    titleCell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF2E5090' }
    };
    titleCell.alignment = { vertical: 'middle', horizontal: 'center' };
    worksheet.getRow(1).height = 30;

    // Información del reporte
    if (options.empleadoId || options.fechaInicio || options.fechaFin) {
      worksheet.mergeCells('A2:H2');
      const infoCell = worksheet.getCell('A2');
      let infoText = '';
      if (options.empleadoId) infoText += `Empleado: ${options.empleadoId} | `;
      if (options.fechaInicio && options.fechaFin) {
        infoText += `Período: ${formatDateDDMMYYYY(options.fechaInicio)} - ${formatDateDDMMYYYY(options.fechaFin)}`;
      }
      infoCell.value = infoText;
      infoCell.font = { size: 11, italic: true };
      infoCell.alignment = { vertical: 'middle', horizontal: 'center' };
      worksheet.getRow(2).height = 20;
    }

    // Encabezados de columna
    const headerRow = worksheet.addRow([
      'Fecha',
      'Usuario ID',
      'Hora',
      'Tipo',
      'Estado',
      'Dispositivo',
      'Sincronizado',
      'Fecha Sincronización'
    ]);

    // Estilo de encabezados
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4472C4' }
    };
    headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
    headerRow.height = 25;

    // Aplicar bordes a encabezados
    headerRow.eachCell((cell) => {
      cell.border = {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' }
      };
    });

    // Agregar datos
    if (data && data.length > 0) {
      data.forEach((record, index) => {
        const row = worksheet.addRow([
          formatDateDDMMYYYY(record.timestamp),
          record.user_id,
          formatTime(record.timestamp),
          PUNCH_TYPES[record.punch] || record.punch,
          ATTENDANCE_STATUS[record.status] || record.status,
          record.dispositivo_id,
          record.sincronizado ? 'Sí' : 'No',
          record.fecha_sincronizacion ? formatDateDDMMYYYY(record.fecha_sincronizacion) : 'N/A'
        ]);

        // Alternar color de filas
        if (index % 2 === 0) {
          row.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFF2F2F2' }
          };
        }

        // Aplicar bordes
        row.eachCell((cell) => {
          cell.border = {
            top: { style: 'thin', color: { argb: 'FFD3D3D3' } },
            left: { style: 'thin', color: { argb: 'FFD3D3D3' } },
            bottom: { style: 'thin', color: { argb: 'FFD3D3D3' } },
            right: { style: 'thin', color: { argb: 'FFD3D3D3' } }
          };
          cell.alignment = { vertical: 'middle', horizontal: 'center' };
        });
      });
    } else {
      // Sin datos
      const noDataRow = worksheet.addRow(['No hay datos disponibles']);
      worksheet.mergeCells(`A${noDataRow.number}:H${noDataRow.number}`);
      noDataRow.getCell(1).alignment = { vertical: 'middle', horizontal: 'center' };
      noDataRow.getCell(1).font = { italic: true, color: { argb: 'FF999999' } };
    }

    // Ajustar ancho de columnas
    worksheet.columns = [
      { key: 'fecha', width: 15 },
      { key: 'usuario', width: 12 },
      { key: 'hora', width: 12 },
      { key: 'tipo', width: 18 },
      { key: 'estado', width: 12 },
      { key: 'dispositivo', width: 12 },
      { key: 'sincronizado', width: 15 },
      { key: 'fecha_sync', width: 20 }
    ];

    // Pie de página con resumen
    const summaryRow = worksheet.addRow([]);
    summaryRow.height = 10;
    
    const footerRow = worksheet.addRow([
      `Total de registros: ${data.length}`,
      '',
      '',
      '',
      '',
      '',
      '',
      `Generado: ${formatDateDDMMYYYY(new Date())}`
    ]);
    worksheet.mergeCells(`A${footerRow.number}:D${footerRow.number}`);
    worksheet.mergeCells(`E${footerRow.number}:H${footerRow.number}`);
    footerRow.font = { size: 9, italic: true };
    footerRow.getCell(1).alignment = { horizontal: 'left' };
    footerRow.getCell(5).alignment = { horizontal: 'right' };

    // Generar buffer
    const buffer = await workbook.xlsx.writeBuffer();
    return buffer;
  }

  /**
   * Genera un reporte resumido por días
   */
  async generateDailySummaryReport(processedData, options = {}) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Resumen Diario');

    workbook.creator = 'Sistema de Control de Asistencia';
    workbook.created = new Date();

    // Título
    worksheet.mergeCells('A1:F1');
    const titleCell = worksheet.getCell('A1');
    titleCell.value = 'RESUMEN DIARIO DE ASISTENCIA';
    titleCell.font = { size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
    titleCell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF2E5090' }
    };
    titleCell.alignment = { vertical: 'middle', horizontal: 'center' };
    worksheet.getRow(1).height = 30;

    // Encabezados
    const headerRow = worksheet.addRow([
      'Fecha',
      'Hora Entrada',
      'Hora Salida',
      'Horas Trabajadas',
      'Registros',
      'Estado'
    ]);

    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4472C4' }
    };
    headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
    headerRow.height = 25;

    // Datos
    processedData.forEach((day, index) => {
      const row = worksheet.addRow([
        formatDateDDMMYYYY(day.fecha),
        day.entrada ? formatTime(day.entrada) : 'N/A',
        day.salida ? formatTime(day.salida) : 'N/A',
        day.horasTrabajadas || '0.00',
        day.registros.length,
        day.entrada && day.salida ? 'Completo' : 'Incompleto'
      ]);

      if (index % 2 === 0) {
        row.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFF2F2F2' }
        };
      }

      row.eachCell((cell) => {
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = {
          top: { style: 'thin' },
          left: { style: 'thin' },
          bottom: { style: 'thin' },
          right: { style: 'thin' }
        };
      });
    });

    // Ajustar columnas
    worksheet.columns = [
      { width: 15 },
      { width: 15 },
      { width: 15 },
      { width: 18 },
      { width: 12 },
      { width: 15 }
    ];

    const buffer = await workbook.xlsx.writeBuffer();
    return buffer;
  }
}

export default new ExcelGeneratorService();

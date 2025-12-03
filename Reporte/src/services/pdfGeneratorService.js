import PDFDocument from 'pdfkit';
import { formatDateDDMMYYYY, formatTime, formatDateTime } from '../utils/dateUtils.js';
import { ATTENDANCE_STATUS, PUNCH_TYPES } from '../config/constants.js';

class PdfGeneratorService {
  /**
   * Genera un reporte de asistencia en formato PDF
   */
  async generateAttendanceReport(data, options = {}) {
    return new Promise((resolve, reject) => {
      try {
        const doc = new PDFDocument({
          size: 'A4',
          layout: 'landscape',
          margins: { top: 50, bottom: 50, left: 50, right: 50 }
        });

        const chunks = [];
        doc.on('data', (chunk) => chunks.push(chunk));
        doc.on('end', () => resolve(Buffer.concat(chunks)));
        doc.on('error', reject);

        // Encabezado
        this.addHeader(doc, options);

        // Información del reporte
        this.addReportInfo(doc, options);

        // Tabla de datos
        this.addAttendanceTable(doc, data);

        // Pie de página
        this.addFooter(doc, data.length);

        doc.end();
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Genera un reporte resumido por días en PDF
   */
  async generateDailySummaryReport(processedData, options = {}) {
    return new Promise((resolve, reject) => {
      try {
        const doc = new PDFDocument({
          size: 'A4',
          margins: { top: 50, bottom: 50, left: 50, right: 50 }
        });

        const chunks = [];
        doc.on('data', (chunk) => chunks.push(chunk));
        doc.on('end', () => resolve(Buffer.concat(chunks)));
        doc.on('error', reject);

        // Encabezado
        doc.fontSize(18).fillColor('#2E5090').text('RESUMEN DIARIO DE ASISTENCIA', { align: 'center' });
        doc.moveDown();

        // Información
        if (options.empleadoId) {
          doc.fontSize(10).fillColor('#000000').text(`Empleado: ${options.empleadoId}`, { align: 'center' });
        }
        if (options.fechaInicio && options.fechaFin) {
          doc.fontSize(10).text(
            `Período: ${formatDateDDMMYYYY(options.fechaInicio)} - ${formatDateDDMMYYYY(options.fechaFin)}`,
            { align: 'center' }
          );
        }
        doc.moveDown(2);

        // Tabla resumida
        this.addDailySummaryTable(doc, processedData);

        // Pie de página
        doc.fontSize(8).fillColor('#666666').text(
          `Total de días: ${processedData.length} | Generado: ${formatDateTime(new Date())}`,
          50,
          doc.page.height - 50,
          { align: 'center' }
        );

        doc.end();
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Agrega el encabezado al documento
   */
  addHeader(doc, options) {
    doc.fontSize(20).fillColor('#2E5090').text(
      options.title || 'REPORTE DE ASISTENCIA',
      { align: 'center' }
    );
    doc.moveDown();
  }

  /**
   * Agrega información del reporte
   */
  addReportInfo(doc, options) {
    doc.fontSize(10).fillColor('#000000');
    
    if (options.empleadoId) {
      doc.text(`Empleado: ${options.empleadoId}`, { align: 'center' });
    }
    
    if (options.fechaInicio && options.fechaFin) {
      doc.text(
        `Período: ${formatDateDDMMYYYY(options.fechaInicio)} - ${formatDateDDMMYYYY(options.fechaFin)}`,
        { align: 'center' }
      );
    }
    
    doc.moveDown(2);
  }

  /**
   * Agrega la tabla de asistencia
   */
  addAttendanceTable(doc, data) {
    const tableTop = doc.y;
    const itemHeight = 20;
    const pageHeight = doc.page.height - 100;

    // Encabezados de tabla
    const headers = ['Fecha', 'Usuario', 'Hora', 'Tipo', 'Estado', 'Dispositivo', 'Sync'];
    const columnWidths = [70, 60, 60, 100, 70, 70, 50];
    const startX = 50;

    // Dibujar encabezados
    doc.fontSize(9).fillColor('#FFFFFF');
    doc.rect(startX, tableTop, 750, itemHeight).fill('#4472C4');
    
    let currentX = startX + 5;
    headers.forEach((header, i) => {
      doc.text(header, currentX, tableTop + 5, {
        width: columnWidths[i],
        align: 'center'
      });
      currentX += columnWidths[i];
    });

    // Dibujar filas de datos
    let currentY = tableTop + itemHeight;
    doc.fillColor('#000000');

    if (data && data.length > 0) {
      data.forEach((record, index) => {
        // Verificar si necesitamos una nueva página
        if (currentY > pageHeight) {
          doc.addPage();
          currentY = 50;
          
          // Redibujar encabezados en nueva página
          doc.fontSize(9).fillColor('#FFFFFF');
          doc.rect(startX, currentY, 750, itemHeight).fill('#4472C4');
          
          currentX = startX + 5;
          headers.forEach((header, i) => {
            doc.text(header, currentX, currentY + 5, {
              width: columnWidths[i],
              align: 'center'
            });
            currentX += columnWidths[i];
          });
          
          currentY += itemHeight;
          doc.fillColor('#000000');
        }

        // Fondo alternado
        if (index % 2 === 0) {
          doc.rect(startX, currentY, 750, itemHeight).fill('#F2F2F2');
        }

        // Datos de la fila
        const rowData = [
          formatDateDDMMYYYY(record.timestamp),
          record.user_id,
          formatTime(record.timestamp),
          PUNCH_TYPES[record.punch] || record.punch,
          ATTENDANCE_STATUS[record.status] || record.status,
          record.dispositivo_id.toString(),
          record.sincronizado ? 'Sí' : 'No'
        ];

        currentX = startX + 5;
        doc.fontSize(8).fillColor('#000000');
        
        rowData.forEach((data, i) => {
          doc.text(data, currentX, currentY + 5, {
            width: columnWidths[i],
            align: 'center'
          });
          currentX += columnWidths[i];
        });

        // Borde de fila
        doc.rect(startX, currentY, 750, itemHeight).stroke('#D3D3D3');
        
        currentY += itemHeight;
      });
    } else {
      doc.fontSize(10).fillColor('#999999').text(
        'No hay datos disponibles',
        startX,
        currentY + 10,
        { width: 750, align: 'center' }
      );
    }
  }

  /**
   * Agrega tabla de resumen diario
   */
  addDailySummaryTable(doc, processedData) {
    const tableTop = doc.y;
    const itemHeight = 20;
    const headers = ['Fecha', 'Entrada', 'Salida', 'Horas', 'Registros', 'Estado'];
    const columnWidths = [80, 70, 70, 70, 70, 80];
    const startX = 50;

    // Encabezados
    doc.fontSize(9).fillColor('#FFFFFF');
    doc.rect(startX, tableTop, 440, itemHeight).fill('#4472C4');
    
    let currentX = startX + 5;
    headers.forEach((header, i) => {
      doc.text(header, currentX, tableTop + 5, {
        width: columnWidths[i],
        align: 'center'
      });
      currentX += columnWidths[i];
    });

    // Datos
    let currentY = tableTop + itemHeight;
    doc.fillColor('#000000');

    processedData.forEach((day, index) => {
      if (index % 2 === 0) {
        doc.rect(startX, currentY, 440, itemHeight).fill('#F2F2F2');
      }

      const rowData = [
        formatDateDDMMYYYY(day.fecha),
        day.entrada ? formatTime(day.entrada) : 'N/A',
        day.salida ? formatTime(day.salida) : 'N/A',
        day.horasTrabajadas || '0.00',
        day.registros.length.toString(),
        day.entrada && day.salida ? 'Completo' : 'Incompleto'
      ];

      currentX = startX + 5;
      doc.fontSize(8).fillColor('#000000');
      
      rowData.forEach((data, i) => {
        doc.text(data, currentX, currentY + 5, {
          width: columnWidths[i],
          align: 'center'
        });
        currentX += columnWidths[i];
      });

      doc.rect(startX, currentY, 440, itemHeight).stroke('#D3D3D3');
      currentY += itemHeight;
    });
  }

  /**
   * Agrega el pie de página
   */
  addFooter(doc, totalRecords) {
    doc.fontSize(8).fillColor('#666666').text(
      `Total de registros: ${totalRecords} | Generado: ${formatDateTime(new Date())}`,
      50,
      doc.page.height - 50,
      { align: 'center' }
    );
  }
}

export default new PdfGeneratorService();

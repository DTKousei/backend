import PDFDocument from 'pdfkit';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { formatearFecha, generarNombreArchivo } from '../utils/helpers.js';
import { generarQRBuffer } from './qr.service.js';
import { METODO_FIRMA } from '../utils/constants.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Genera un PDF de la papeleta con todas las firmas
 */
export const generarPDFPapeleta = async (permiso, tipoPermiso, empleadoInfo = {}) => {
  return new Promise((resolve, reject) => {
    try {
      // Crear documento PDF
      const doc = new PDFDocument({
        size: 'A4',
        margins: { top: 50, bottom: 50, left: 50, right: 50 }
      });

      // Generar nombre de archivo
      const nombreArchivo = generarNombreArchivo('papeleta', 'pdf');
      const rutaArchivo = path.join(__dirname, '../../generated', nombreArchivo);

      // Crear stream de escritura
      const stream = fs.createWriteStream(rutaArchivo);
      doc.pipe(stream);

      // --- ENCABEZADO ---
      doc.fontSize(20)    
         .font('Helvetica-Bold')
         .text('PAPELETA DE PERMISO', { align: 'center' });
      
      doc.moveDown();
      doc.fontSize(10)
         .font('Helvetica')
         .text(`N° ${permiso.id.substring(0, 8).toUpperCase()}`, { align: 'center' });
      
      doc.moveDown(2);

      // --- INFORMACIÓN DEL EMPLEADO ---
      doc.fontSize(12)
         .font('Helvetica-Bold')
         .text('DATOS DEL SOLICITANTE', { underline: true });
      
      doc.moveDown(0.5);
      doc.fontSize(10)
         .font('Helvetica');
      
      doc.text(`Empleado ID: ${permiso.empleado_id}`);
      if (empleadoInfo.nombre) {
        doc.text(`Nombre: ${empleadoInfo.nombre}`);
      }
      if (empleadoInfo.cargo) {
        doc.text(`Cargo: ${empleadoInfo.cargo}`);
      }
      if (empleadoInfo.area) {
        doc.text(`Área: ${empleadoInfo.area}`);
      }

      doc.moveDown(1.5);

      // --- INFORMACIÓN DEL PERMISO ---
      doc.fontSize(12)
         .font('Helvetica-Bold')
         .text('INFORMACIÓN DEL PERMISO', { underline: true });
      
      doc.moveDown(0.5);
      doc.fontSize(10)
         .font('Helvetica');
      
      doc.text(`Tipo de Permiso: ${tipoPermiso.nombre}`);
      doc.text(`Fecha y Hora de Inicio: ${formatearFecha(permiso.fecha_hora_inicio)}`);
      
      if (permiso.fecha_hora_fin) {
        doc.text(`Fecha y Hora de Fin: ${formatearFecha(permiso.fecha_hora_fin)}`);
      }
      
      if (permiso.hora_salida_calculada) {
        doc.text(`Hora de Salida Calculada: ${formatearFecha(permiso.hora_salida_calculada)}`);
      }

      if (tipoPermiso.tiempo_maximo_horas) {
        doc.text(`Tiempo Máximo: ${tipoPermiso.tiempo_maximo_horas} horas`);
      } else {
        doc.text(`Tiempo: Sin límite (se define manualmente)`);
      }

      doc.moveDown(1);

      doc.font('Helvetica-Bold').text('Motivo:');
      doc.font('Helvetica').text(permiso.motivo, { width: 500 });
      
      doc.moveDown(0.5);
      
      doc.font('Helvetica-Bold').text('Justificación:');
      doc.font('Helvetica').text(permiso.justificacion, { width: 500 });

      if (permiso.institucion_visitada) {
        doc.moveDown(0.5);
        doc.font('Helvetica-Bold').text('Institución Visitada:');
        doc.font('Helvetica').text(permiso.institucion_visitada);
      }

      doc.moveDown(2);

      // --- FIRMAS ---
      doc.fontSize(12)
         .font('Helvetica-Bold')
         .text('FIRMAS', { underline: true });
      
      doc.moveDown(1);

      const firmas = [
        {
          titulo: 'Firma del Solicitante',
          tipo: 'solicitante',
          firma: permiso.firma_solicitante,
          firmaDigital: permiso.firma_solicitante_digital,
          certificado: permiso.certificado_solicitante,
          metodo: permiso.metodo_firma_solicitante,
          fecha: permiso.firma_solicitante_en
        },
        {
          titulo: 'Firma del Jefe de Área',
          tipo: 'jefe_area',
          firma: permiso.firma_jefe_area,
          firmaDigital: permiso.firma_jefe_area_digital,
          certificado: permiso.certificado_jefe_area,
          metodo: permiso.metodo_firma_jefe_area,
          fecha: permiso.firma_jefe_area_en
        },
        {
          titulo: 'Firma de RRHH',
          tipo: 'rrhh',
          firma: permiso.firma_rrhh,
          firmaDigital: permiso.firma_rrhh_digital,
          certificado: permiso.certificado_rrhh,
          metodo: permiso.metodo_firma_rrhh,
          fecha: permiso.firma_rrhh_en
        }
      ];

      // Agregar firma de institución si aplica
      if (tipoPermiso.requiere_firma_institucion) {
        firmas.push({
          titulo: 'Firma de Institución Visitada',
          tipo: 'institucion',
          firma: permiso.firma_institucion,
          firmaDigital: permiso.firma_institucion_digital,
          certificado: permiso.certificado_institucion,
          metodo: permiso.metodo_firma_institucion,
          fecha: permiso.firma_institucion_en
        });
      }

      // Dibujar firmas en dos columnas
      let yPosition = doc.y;
      const columnWidth = 250;
      const leftColumn = 50;
      const rightColumn = 320;

      // Procesar firmas de forma asíncrona
      for (let index = 0; index < firmas.length; index++) {
        const firmaInfo = firmas[index];
        const isLeftColumn = index % 2 === 0;
        const xPosition = isLeftColumn ? leftColumn : rightColumn;
        
        if (index > 0 && index % 2 === 0) {
          yPosition += 140; // Espacio entre filas (aumentado para QR)
        }

        doc.fontSize(10)
           .font('Helvetica-Bold')
           .text(firmaInfo.titulo, xPosition, yPosition, { width: columnWidth });

        // Verificar si es firma digital ONPE
        if (firmaInfo.metodo === METODO_FIRMA.ONPE && firmaInfo.certificado) {
          // Firma Digital ONPE
          doc.fontSize(8)
             .font('Helvetica')
             .text(`Firmado digitalmente por:`, xPosition, yPosition + 15);
          
          doc.fontSize(9)
             .font('Helvetica-Bold')
             .text(firmaInfo.certificado.nombre || 'N/A', xPosition, yPosition + 27);
          
          doc.fontSize(8)
             .font('Helvetica')
             .text(`DNI: ${firmaInfo.certificado.dni || 'N/A'}`, xPosition, yPosition + 40);
          
          doc.text(`Entidad: ${firmaInfo.certificado.entidad_emisora || 'N/A'}`, xPosition, yPosition + 52);
          
          // Generar y agregar QR code
          // Nota: No podemos usar await aquí porque no estamos en contexto async
          // El QR se generará pero no bloqueará el flujo
          generarQRBuffer(permiso.id, firmaInfo.tipo, firmaInfo.certificado)
            .then(qrBuffer => {
              doc.image(qrBuffer, xPosition + 150, yPosition + 15, {
                width: 60,
                height: 60
              });
              doc.fontSize(7)
                 .text('Verificar', xPosition + 160, yPosition + 78, { width: 40, align: 'center' });
            })
            .catch(error => {
              console.error('Error generando QR:', error);
            });


        } else if (firmaInfo.firma) {
          // Firma tradicional base64
          try {
            // Extraer datos base64
            const base64Data = firmaInfo.firma.replace(/^data:image\/\w+;base64,/, '');
            const imageBuffer = Buffer.from(base64Data, 'base64');
            
            doc.image(imageBuffer, xPosition, yPosition + 15, {
              width: 150,
              height: 50
            });
          } catch (error) {
            // Si falla la imagen, mostrar texto
            doc.fontSize(9)
               .font('Helvetica-Oblique')
               .text('[Firma electrónica]', xPosition, yPosition + 15);
          }
        } else {
          // Sin firma
          doc.fontSize(9)
             .font('Helvetica')
             .text('_____________________', xPosition, yPosition + 40);
          doc.text('(Pendiente)', xPosition, yPosition + 55);
        }

        // Fecha de firma
        if (firmaInfo.fecha) {
          doc.fontSize(8)
             .font('Helvetica')
             .text(`Fecha: ${formatearFecha(firmaInfo.fecha)}`, xPosition, yPosition + 90);
        }
      }

      // --- PIE DE PÁGINA ---
      doc.fontSize(8)
         .font('Helvetica-Oblique')
         .text(
           `Documento generado el ${formatearFecha(new Date())}`,
           50,
           doc.page.height - 70,
           { align: 'center' }
         );

      // Finalizar documento
      doc.end();

      // Esperar a que termine de escribir
      stream.on('finish', () => {
        resolve({
          ruta: rutaArchivo,
          nombreArchivo: nombreArchivo,
          rutaRelativa: `/generated/${nombreArchivo}`
        });
      });

      stream.on('error', (error) => {
        reject(error);
      });

    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Elimina un archivo PDF
 */
export const eliminarPDF = async (rutaArchivo) => {
  try {
    if (fs.existsSync(rutaArchivo)) {
      fs.unlinkSync(rutaArchivo);
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error al eliminar PDF:', error);
    return false;
  }
};

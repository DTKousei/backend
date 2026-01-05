import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { formatearFecha, generarNombreArchivo } from '../utils/helpers.js';
import { generarQRBuffer } from './qr.service.js';
import { METODO_FIRMA } from '../utils/constants.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Genera un PDF de la papeleta con todas las firmas usando Puppeteer
 */
export const generarPDFPapeleta = async (permiso, tipoPermiso, empleadoInfo = {}, nombreArchivoPersonalizado = null) => {
  let browser;
  try {
    // Lanzar navegador
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Preparar logo
    const logoPath = path.join(__dirname, '../../img/LOGO_UGEL.png');
    let logoSrc = '';
    if (fs.existsSync(logoPath)) {
      const logoBase64 = fs.readFileSync(logoPath).toString('base64');
      logoSrc = `data:image/png;base64,${logoBase64}`;
    }

    // Preparar firmas
    const firmasProcesadas = await procesarFirmas(permiso, tipoPermiso);

    // Determinar checkbox seleccionado para Motivo
    const motivoLower = (permiso.motivo || '').toLowerCase();
    const tipoLower = (tipoPermiso.nombre || '').toLowerCase();
    
    // Lógica para marcar casillas
    const checkSalud = motivoLower.includes('salud') || tipoLower.includes('salud') || tipoLower.includes('cita medica');
    const checkComision = motivoLower.includes('comisi') || tipoLower.includes('comisi') || tipoLower.includes('oficial');
    const checkParticulares = motivoLower.includes('particular') || tipoLower.includes('particular') || motivoLower.includes('personal') || tipoLower.includes('personal');
    
    // Si no es ninguno de los anteriores, es "Otros"
    const checkOtros = !checkSalud && !checkComision && !checkParticulares;
    
    // Si es "Otros", mostrar el motivo específico
    const textoOtros = checkOtros ? (tipoPermiso.nombre === 'Otros' ? permiso.motivo : tipoPermiso.nombre) : '';

    // Formatear fechas
    const fecha = new Date(permiso.fecha_hora_inicio);
    const fechaDia = fecha.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const horaSalida = fecha.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', hour12: false });
    
    let horaRetorno = '';
    if (permiso.fecha_hora_fin) {
      horaRetorno = new Date(permiso.fecha_hora_fin).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', hour12: false });
    } else if (permiso.hora_salida_calculada) {
       // Si es hora_salida_calculada, a veces se usa como retorno estimado
       // pero formateamos solo si es válido
       const fechaCalc = new Date(permiso.hora_salida_calculada);
       if (!isNaN(fechaCalc.getTime())) {
         horaRetorno = fechaCalc.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', hour12: false });
       }
    }

    // HTML Content
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body {
            font-family: Arial, sans-serif;
            font-size: 11px;
            margin: 0;
            padding: 20px;
          }
          .container {
            border: 1px solid black;
            padding: 5px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          .header-table td {
            border: 1px solid black;
            padding: 5px;
            text-align: center;
          }
          .header-logo {
            width: 15%;
          }
          .header-logo img {
            max-width: 60px;
          }
          .header-title {
            width: 65%;
            font-weight: bold;
            font-size: 14px;
          }
          .header-meta {
            width: 20%;
            padding: 0 !important;
          }
          .header-meta table td {
            border: none;
            border-bottom: 1px solid black;
            text-align: left;
            padding: 2px 5px;
            font-size: 10px;
          }
          .header-meta table tr:last-child td {
            border-bottom: none;
          }
          
          .section-row {
            border: 1px solid black;
            border-top: none;
            display: flex;
          }
          .field-label {
            background-color: #f0f0f0;
            padding: 5px;
            border-right: 1px solid black;
            font-weight: bold;
            display: flex;
            align-items: center;
            width: 150px;
          }
          .field-value {
            padding: 5px;
            flex: 1;
            display: flex;
            align-items: center;
            text-transform: uppercase;
          }
          
          .two-col-row {
            display: flex;
            border: 1px solid black;
            border-top: none;
          }
          .col-half {
            width: 50%;
            display: flex;
          }
          .col-half:first-child {
            border-right: 1px solid black;
          }
          .col-half .field-label {
            width: 100px;
          }
          
          .motivo-section {
            border: 1px solid black;
            border-top: none;
            padding: 5px 10px;
            display: flex;
            align-items: center;
          }
          .checkbox-container {
            display: flex;
            align-items: center;
            margin-left: 20px;
          }
          .checkbox-box {
            width: 12px;
            height: 12px;
            border: 1px solid black;
            margin-left: 5px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 10px;
            line-height: 10px;
          }
          
          .fundamentacion-section {
            border: 1px solid black;
            border-top: none;
            padding: 5px 10px;
            min-height: 100px;
          }
          .fundamentacion-text {
             margin-top: 5px;
             text-transform: uppercase;
             font-size: 11px;
             line-height: 1.5;
          }
          .lines-container {
            margin-top: 5px;
          }
          .line {
            border-bottom: 1px solid black;
            height: 20px;
            margin-bottom: 5px;
          }

          .signatures-container {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
            padding: 0 10px;
          }
          .signature-box {
            width: 22%;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
          }
          .signature-line {
            width: 100%;
            border-top: 1px solid black;
            margin-top: 5px;
            padding-top: 5px;
            font-weight: bold;
            font-size: 9px;
          }
          .signature-image {
            height: 50px;
            max-width: 100%;
            margin-bottom: 2px;
            object-fit: contain;
          }
          .digital-signature {
            border: 1px solid #ccc;
            padding: 2px;
            font-size: 7px;
            width: 100%;
            text-align: left;
            margin-bottom: 2px;
            word-break: break-all;
          }
          
          .footer-note {
            font-size: 8px;
            margin-top: 20px;
            font-style: italic;
          }

          /* Checkmark style */
          .checked::after {
            content: "X";
          }
        </style>
      </head>
      <body>
        <div class="container">
          <!-- Header -->
          <table class="header-table">
            <tr>
              <td class="header-logo">
                ${logoSrc ? `<img src="${logoSrc}" />` : 'LOGO'}
              </td>
              <td class="header-title">
                UGEL SUCRE<br>
                PAPELETA DE AUTORIZACIÓN DE SALIDA<br>
                ${fecha.getFullYear()}
              </td>
              <td class="header-meta">
                <table style="width:100%; margin:0; padding:0; border:none;">
                  <tr>
                    <td><strong>N° DE PAPELETA</strong></td>
                    <td>${permiso.id.substring(0, 8).toUpperCase()}</td>
                  </tr>
                  <tr>
                    <td><strong>Fecha:</strong></td>
                    <td>${fechaDia}</td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <!-- Datos Empleado -->
          <div class="section-row">
            <div class="field-label">APELLIDOS Y NOMBRES:</div>
            <div class="field-value">${empleadoInfo.nombre || ''}</div>
          </div>
          
          <div class="section-row">
            <div class="field-label">ÁREA O DEPENDENCIA ADMINISTRATIVA:</div>
            <div class="field-value">${empleadoInfo.area || empleadoInfo.cargo || ''}</div>
          </div>

          <!-- Horas -->
          <div class="two-col-row">
            <div class="col-half">
              <div class="field-label">HORA DE SALIDA :</div>
              <div class="field-value">${horaSalida}</div>
            </div>
            <div class="col-half">
              <div class="field-label">HORA DE RETORNO:</div>
              <div class="field-value">${horaRetorno}</div>
            </div>
          </div>

          <!-- Motivo -->
          <div class="motivo-section">
            <div style="font-weight:bold;">MOTIVO:</div>
            
            <div class="checkbox-container">
              PARTICULARES <div class="checkbox-box ${checkParticulares ? 'checked' : ''}"></div>
            </div>
            
            <div class="checkbox-container">
              SALUD <div class="checkbox-box ${checkSalud ? 'checked' : ''}"></div>
            </div>
            
            <div class="checkbox-container">
              COMISIÓN <div class="checkbox-box ${checkComision ? 'checked' : ''}"></div>
            </div>

             <div class="checkbox-container">
              OTROS <div class="checkbox-box ${checkOtros ? 'checked' : ''}"></div>
              ${checkOtros ? `<span style="margin-left:5px; border-bottom: 1px solid black; padding: 0 5px;">${textoOtros}</span>` : ''}
            </div>
          </div>

          <!-- Fundamentación -->
          <div class="fundamentacion-section">
            <div style="font-weight:bold;">FUNDAMENTACIÓN:</div>
            <div class="fundamentacion-text">
              ${permiso.motivo ? `<strong>${permiso.motivo}</strong>: ` : ''} ${permiso.justificacion || ''}
              ${permiso.institucion_visitada ? `<br>Institución Visitada: ${permiso.institucion_visitada}` : ''}
            </div>
            <!-- Líneas de relleno visual -->
            <div class="lines-container">
              <div class="line"></div>
              <div class="line"></div>
              <div class="line"></div>
            </div>
          </div>

          <!-- Firmas -->
          <div class="signatures-container">
             <!-- RRHH (Jefe de Personal) -->
            <div class="signature-box">
              <div style="height: 60px; display: flex; align-items: flex-end; justify-content: center; width: 100%;">
                 ${renderFirmaHtml(firmasProcesadas.rrhh)}
              </div>
              <div class="signature-line">JEFE DE PERSONAL</div>
            </div>

            <!-- Jefe Inmediato -->
             <div class="signature-box">
              <div style="height: 60px; display: flex; align-items: flex-end; justify-content: center; width: 100%;">
                 ${renderFirmaHtml(firmasProcesadas.jefe_area)}
              </div>
              <div class="signature-line">JEFE INMEDIATO</div>
            </div>

            <!-- Solicitante -->
             <div class="signature-box">
              <div style="height: 60px; display: flex; align-items: flex-end; justify-content: center; width: 100%;">
                 ${renderFirmaHtml(firmasProcesadas.solicitante)}
              </div>
              <div class="signature-line">SOLICITANTE</div>
            </div>
            
            <!-- Lugar Asistido (Opcional) -->
             <div class="signature-box">
              <div style="height: 60px; display: flex; align-items: flex-end; justify-content: center; width: 100%;">
                 ${renderFirmaHtml(firmasProcesadas.institucion)}
              </div>
              <div class="signature-line">V°B° DEL LUGAR ASISTIDO</div>
            </div>
          </div>
          
          <div class="footer-note">
            anexar soporte de justificación del permiso, cuando el caso es por salud o comision
          </div>

        </div>
      </body>
      </html>
    `;

    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });

    // Generar nombre de archivo (Usar correlativo corto)
    const nombreArchivo = `papeleta_${permiso.id.substring(0, 8)}.pdf`;
    
    // Ruta de salida normalizada
    const relativeDir = 'generated'; 
    const outputDir = path.join(__dirname, '../../', relativeDir);

    // Asegurar directorio
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const rutaArchivo = path.join(outputDir, nombreArchivo);

    // Eliminar si existe para evitar problemas de permisos o bloqueos
    if (fs.existsSync(rutaArchivo)) {
        try {
            fs.unlinkSync(rutaArchivo);
        } catch(e) { console.error('Error eliminando archivo previo:', e); }
    }

    await page.pdf({
      path: rutaArchivo,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20px',
        bottom: '20px',
        left: '20px',
        right: '20px'
      }
    });

    await browser.close();

    return {
      ruta: rutaArchivo,
      nombreArchivo: nombreArchivo,
      rutaRelativa: `/generated/${nombreArchivo}`
    };

  } catch (error) {
    if (browser) await browser.close();
    throw error;
  }
};

/**
 * Helper para renderizar el HTML de una firma
 */
const renderFirmaHtml = (firmaInfo) => {
  if (!firmaInfo) return ''; // Espacio en blanco

  if (firmaInfo.metodo === METODO_FIRMA.ONPE && firmaInfo.certificado) {
    return `
      <div class="digital-signature">
        <strong>Firma Digital</strong><br>
        ${firmaInfo.certificado.nombre}<br>
        DNI: ${firmaInfo.certificado.dni}<br>
        ${firmaInfo.fecha ? formatearFecha(firmaInfo.fecha) : ''}
        ${firmaInfo.qrBase64 ? `<br><img src="${firmaInfo.qrBase64}" style="width: 40px; margin-top: 2px;" />` : ''}
      </div>
    `;
  } else if (firmaInfo.firma) {
    // Es base64 image string (data:image/...)
    // Aseguramos que tenga el prefijo si no lo tiene (aunque normalmente lo tiene)
    let src = firmaInfo.firma;
    if (!src.startsWith('data:image')) {
        src = `data:image/png;base64,${src}`;
    }
    return `<img src="${src}" class="signature-image" />`;
  }
  
  return '';
};

/**
 * Procesa las firmas y genera sus QRs si es necesario
 */
const procesarFirmas = async (permiso, tipoPermiso) => {
  const result = {
    solicitante: null,
    jefe_area: null,
    rrhh: null,
    institucion: null
  };

  // Helper interno
  const procesarIndividual = async (tipo, firma, firmaDigital, certificado, metodo, fecha) => {
    const info = { tipo, firma, firmaDigital, certificado, metodo, fecha, qrBase64: null };
    
    if (metodo === METODO_FIRMA.ONPE && certificado) {
      try {
        const qrBuffer = await generarQRBuffer(permiso.id, tipo, certificado);
        info.qrBase64 = `data:image/png;base64,${qrBuffer.toString('base64')}`;
      } catch (e) {
        console.error('Error generando QR para PDF', e);
      }
    }
    return info;
  };

  if (permiso.firma_solicitante || permiso.firma_solicitante_digital) {
    result.solicitante = await procesarIndividual(
      'solicitante', 
      permiso.firma_solicitante, 
      permiso.firma_solicitante_digital, 
      permiso.certificado_solicitante, 
      permiso.metodo_firma_solicitante,
      permiso.firma_solicitante_en
    );
  }

  if (permiso.firma_jefe_area || permiso.firma_jefe_area_digital) {
    result.jefe_area = await procesarIndividual(
      'jefe_area', 
      permiso.firma_jefe_area, 
      permiso.firma_jefe_area_digital, 
      permiso.certificado_jefe_area, 
      permiso.metodo_firma_jefe_area,
      permiso.firma_jefe_area_en
    );
  }

  if (permiso.firma_rrhh || permiso.firma_rrhh_digital) {
    result.rrhh = await procesarIndividual(
      'rrhh', 
      permiso.firma_rrhh, 
      permiso.firma_rrhh_digital, 
      permiso.certificado_rrhh, 
      permiso.metodo_firma_rrhh,
      permiso.firma_rrhh_en
    );
  }

  if (permiso.firma_institucion || permiso.firma_institucion_digital) {
    result.institucion = await procesarIndividual(
      'institucion', 
      permiso.firma_institucion, 
      permiso.firma_institucion_digital, 
      permiso.certificado_institucion, 
      permiso.metodo_firma_institucion,
      permiso.firma_institucion_en
    );
  }

  return result;
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

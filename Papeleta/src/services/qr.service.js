import QRCode from 'qrcode';
import crypto from 'crypto';

/**
 * Genera código QR para verificación de firma
 */
export const generarQRVerificacion = async (permisoId, tipoFirma, certificadoInfo) => {
  try {
    const datosVerificacion = {
      permiso_id: permisoId,
      tipo_firma: tipoFirma,
      firmante_dni: certificadoInfo.dni,
      firmante_nombre: certificadoInfo.nombre,
      fecha_firma: new Date().toISOString(),
      numero_serie_certificado: certificadoInfo.numero_serie
    };

    // Generar hash de los datos para integridad
    const hash = crypto
      .createHash('sha256')
      .update(JSON.stringify(datosVerificacion))
      .digest('hex')
      .substring(0, 16);

    // URL de verificación (ajustar según tu dominio)
    const urlVerificacion = `${process.env.APP_URL || 'http://localhost:3000'}/api/permisos/${permisoId}/verificar-firma/${tipoFirma}?hash=${hash}`;

    // Generar QR como Data URL
    const qrDataURL = await QRCode.toDataURL(urlVerificacion, {
      errorCorrectionLevel: 'M',
      type: 'image/png',
      width: 200,
      margin: 1
    });

    return {
      qr_data_url: qrDataURL,
      url_verificacion: urlVerificacion,
      hash_verificacion: hash,
      datos: datosVerificacion
    };

  } catch (error) {
    throw new Error(`Error al generar QR: ${error.message}`);
  }
};

/**
 * Genera QR como buffer para embeber en PDF
 */
export const generarQRBuffer = async (permisoId, tipoFirma, certificadoInfo) => {
  try {
    const datosVerificacion = {
      permiso_id: permisoId,
      tipo_firma: tipoFirma,
      firmante_dni: certificadoInfo.dni,
      fecha_firma: new Date().toISOString()
    };

    const hash = crypto
      .createHash('sha256')
      .update(JSON.stringify(datosVerificacion))
      .digest('hex')
      .substring(0, 16);

    const urlVerificacion = `${process.env.APP_URL || 'http://localhost:3000'}/api/permisos/${permisoId}/verificar-firma/${tipoFirma}?hash=${hash}`;

    // Generar QR como buffer
    const qrBuffer = await QRCode.toBuffer(urlVerificacion, {
      errorCorrectionLevel: 'M',
      type: 'png',
      width: 150,
      margin: 1
    });

    return qrBuffer;

  } catch (error) {
    throw new Error(`Error al generar QR buffer: ${error.message}`);
  }
};

/**
 * Valida hash de verificación
 */
export const validarHashVerificacion = (permisoId, tipoFirma, certificadoInfo, hashRecibido) => {
  const datosVerificacion = {
    permiso_id: permisoId,
    tipo_firma: tipoFirma,
    firmante_dni: certificadoInfo.dni,
    firmante_nombre: certificadoInfo.nombre,
    fecha_firma: certificadoInfo.fecha_firma,
    numero_serie_certificado: certificadoInfo.numero_serie
  };

  const hashCalculado = crypto
    .createHash('sha256')
    .update(JSON.stringify(datosVerificacion))
    .digest('hex')
    .substring(0, 16);

  return hashCalculado === hashRecibido;
};

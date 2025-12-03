import { TIPO_FIRMA } from '../utils/constants.js';
import { AppError } from '../middleware/error.middleware.js';

/**
 * Valida que las firmas requeridas estén presentes según el tipo de permiso
 */
export const validarFirmasRequeridas = (permiso, tipoPermiso) => {
  const firmasRequeridas = [
    TIPO_FIRMA.SOLICITANTE,
    TIPO_FIRMA.JEFE_AREA,
    TIPO_FIRMA.RRHH
  ];

  // Si es comisión de servicio, agregar firma de institución
  if (tipoPermiso.requiere_firma_institucion) {
    firmasRequeridas.push(TIPO_FIRMA.INSTITUCION);
  }

  const firmasFaltantes = [];

  for (const tipoFirma of firmasRequeridas) {
    const campoFirma = `firma_${tipoFirma}`;
    if (!permiso[campoFirma]) {
      firmasFaltantes.push(tipoFirma);
    }
  }

  return {
    completo: firmasFaltantes.length === 0,
    faltantes: firmasFaltantes
  };
};

/**
 * Valida que se pueda agregar una firma (verificando el orden correcto)
 */
export const validarOrdenFirma = (permiso, tipoFirma, tipoPermiso) => {
  // Orden de firmas: solicitante -> jefe_area -> rrhh -> institución (si aplica)
  
  switch (tipoFirma) {
    case TIPO_FIRMA.SOLICITANTE:
      // La firma del solicitante siempre se puede agregar primero
      return { valido: true };
    
    case TIPO_FIRMA.JEFE_AREA:
      // Requiere firma del solicitante
      if (!permiso.firma_solicitante) {
        return {
          valido: false,
          mensaje: 'Se requiere primero la firma del solicitante'
        };
      }
      return { valido: true };
    
    case TIPO_FIRMA.RRHH:
      // Requiere firma del jefe de área
      if (!permiso.firma_jefe_area) {
        return {
          valido: false,
          mensaje: 'Se requiere primero la firma del jefe de área'
        };
      }
      return { valido: true };
    
    case TIPO_FIRMA.INSTITUCION:
      // Solo para comisión de servicio y requiere firma de RRHH
      if (!tipoPermiso.requiere_firma_institucion) {
        return {
          valido: false,
          mensaje: 'Este tipo de permiso no requiere firma de institución'
        };
      }
      if (!permiso.firma_rrhh) {
        return {
          valido: false,
          mensaje: 'Se requiere primero la firma de RRHH'
        };
      }
      return { valido: true };
    
    default:
      return {
        valido: false,
        mensaje: 'Tipo de firma inválido'
      };
  }
};

/**
 * Obtiene el siguiente tipo de firma requerido
 */
export const obtenerSiguienteFirma = (permiso, tipoPermiso) => {
  if (!permiso.firma_solicitante) {
    return TIPO_FIRMA.SOLICITANTE;
  }
  
  if (!permiso.firma_jefe_area) {
    return TIPO_FIRMA.JEFE_AREA;
  }
  
  if (!permiso.firma_rrhh) {
    return TIPO_FIRMA.RRHH;
  }
  
  if (tipoPermiso.requiere_firma_institucion && !permiso.firma_institucion) {
    return TIPO_FIRMA.INSTITUCION;
  }
  
  return null; // Todas las firmas están completas
};

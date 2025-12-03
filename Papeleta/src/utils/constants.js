// Tipos de permisos
export const TIPO_PERMISO = {
  COMISION_SERVICIO: 'COMISION_SERVICIO',
  PERMISO_PERSONAL: 'PERMISO_PERSONAL'
};

// Estados de permisos
export const ESTADO_PERMISO = {
  PENDIENTE: 'PENDIENTE',
  APROBADO_JEFE: 'APROBADO_JEFE',
  APROBADO_RRHH: 'APROBADO_RRHH',
  APROBADO: 'APROBADO',
  RECHAZADO: 'RECHAZADO',
  CANCELADO: 'CANCELADO'
};

// Tipos de firma
export const TIPO_FIRMA = {
  SOLICITANTE: 'solicitante',
  JEFE_AREA: 'jefe_area',
  RRHH: 'rrhh',
  INSTITUCION: 'institucion'
};

// Métodos de firma
export const METODO_FIRMA = {
  BASE64: 'base64',
  ONPE: 'onpe'
};

// Configuración de permisos
export const PERMISO_CONFIG = {
  [TIPO_PERMISO.COMISION_SERVICIO]: {
    requiere_firma_institucion: true,
    tiempo_maximo_horas: null, // Sin límite
    descripcion: 'Comisión de servicio a otra institución'
  },
  [TIPO_PERMISO.PERMISO_PERSONAL]: {
    requiere_firma_institucion: false,
    tiempo_maximo_horas: 2,
    descripcion: 'Permiso personal (máximo 2 horas)'
  }
};

// Mensajes de error
export const ERROR_MESSAGES = {
  PERMISO_NOT_FOUND: 'Permiso no encontrado',
  TIPO_PERMISO_NOT_FOUND: 'Tipo de permiso no encontrado',
  ESTADO_NOT_FOUND: 'Estado no encontrado',
  FIRMA_INVALIDA: 'Firma inválida o incompleta',
  FIRMA_YA_EXISTE: 'Esta firma ya fue registrada',
  FIRMA_PREVIA_REQUERIDA: 'Se requiere la firma previa antes de continuar',
  TIEMPO_EXCEDIDO: 'El tiempo del permiso excede el máximo permitido',
  FECHA_INVALIDA: 'Fecha u hora inválida',
  PDF_NOT_FOUND: 'PDF no encontrado',
  ARCHIVO_INVALIDO: 'Archivo inválido'
};

// Mensajes de éxito
export const SUCCESS_MESSAGES = {
  PERMISO_CREADO: 'Permiso creado exitosamente',
  PERMISO_ACTUALIZADO: 'Permiso actualizado exitosamente',
  PERMISO_ELIMINADO: 'Permiso eliminado exitosamente',
  FIRMA_REGISTRADA: 'Firma registrada exitosamente',
  PDF_GENERADO: 'PDF generado exitosamente',
  PDF_CARGADO: 'PDF cargado exitosamente'
};

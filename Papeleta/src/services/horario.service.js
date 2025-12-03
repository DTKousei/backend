import { calcularDiferenciaHoras } from '../utils/helpers.js';

/**
 * Calcula la hora de salida según el tipo de permiso
 * 
 * Para permiso personal (2 horas máximo): hora_inicio + 2 horas
 * Para comisión de servicio: null (sin límite, se define manualmente)
 */
export const calcularHoraSalida = (fechaInicio, fechaFin, tipoPermiso) => {
  // Si es comisión de servicio (sin límite de tiempo)
  if (!tipoPermiso.tiempo_maximo_horas) {
    return null; // Se define manualmente
  }

  // Si tiene límite de tiempo (permiso personal)
  const horaInicio = new Date(fechaInicio);
  const horaSalida = new Date(horaInicio);
  horaSalida.setHours(horaSalida.getHours() + tipoPermiso.tiempo_maximo_horas);

  return horaSalida;
};

/**
 * Valida que el tiempo del permiso no exceda el máximo permitido
 */
export const validarTiempoPermiso = (fechaInicio, fechaFin, tipoPermiso) => {
  // Si no hay límite de tiempo, es válido
  if (!tipoPermiso.tiempo_maximo_horas) {
    return { valido: true };
  }

  // Si no hay fecha fin, usar el tiempo máximo
  if (!fechaFin) {
    return { valido: true };
  }

  const horasDiferencia = calcularDiferenciaHoras(fechaInicio, fechaFin);

  if (horasDiferencia > tipoPermiso.tiempo_maximo_horas) {
    return {
      valido: false,
      mensaje: `El permiso excede el tiempo máximo permitido de ${tipoPermiso.tiempo_maximo_horas} horas`,
      horasExcedidas: horasDiferencia - tipoPermiso.tiempo_maximo_horas
    };
  }

  return { valido: true };
};

/**
 * Obtiene información sobre el horario del permiso
 */
export const obtenerInfoHorario = (permiso, tipoPermiso) => {
  const info = {
    fecha_inicio: permiso.fecha_hora_inicio,
    fecha_fin: permiso.fecha_hora_fin,
    hora_salida_calculada: permiso.hora_salida_calculada,
    tiene_limite_tiempo: !!tipoPermiso.tiempo_maximo_horas,
    tiempo_maximo_horas: tipoPermiso.tiempo_maximo_horas
  };

  if (permiso.fecha_hora_fin) {
    info.duracion_horas = calcularDiferenciaHoras(
      permiso.fecha_hora_inicio,
      permiso.fecha_hora_fin
    );
  }

  return info;
};

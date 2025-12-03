import axios from 'axios';
import { config } from '../config/constants.js';

class AttendanceApiService {
  constructor() {
    this.baseUrl = config.attendanceApiUrl;
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Obtiene todas las asistencias con filtros opcionales
   */
  async getAttendances(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.dispositivo_id) params.append('dispositivo_id', filters.dispositivo_id);
      if (filters.fecha_inicio) params.append('fecha_inicio', filters.fecha_inicio);
      if (filters.fecha_fin) params.append('fecha_fin', filters.fecha_fin);
      if (filters.sincronizado !== undefined) params.append('sincronizado', filters.sincronizado);

      const response = await this.client.get('/asistencias', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Obtiene asistencias de un usuario específico
   */
  async getAttendancesByUser(userId, filters = {}) {
    try {
      const params = new URLSearchParams({ user_id: userId });
      
      // Note: No enviamos fecha_inicio y fecha_fin a la API externa
      // porque causa errores de validación. Filtraremos los datos localmente.

      const response = await this.client.get('/asistencias', { params });
      
      // Filtrar por fechas localmente si se proporcionaron
      let data = response.data;
      if (filters.fecha_inicio || filters.fecha_fin) {
        data = this.filterByDateRange(data, filters.fecha_inicio, filters.fecha_fin);
      }
      
      return data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Filtra datos de asistencia por rango de fechas
   */
  filterByDateRange(attendances, startDate, endDate) {
    if (!Array.isArray(attendances)) return attendances;
    
    return attendances.filter(record => {
      const recordDate = new Date(record.timestamp);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;
      
      if (start && recordDate < start) return false;
      if (end && recordDate > end) return false;
      
      return true;
    });
  }

  /**
   * Obtiene el conteo de asistencias
   */
  async getAttendanceCount(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.dispositivo_id) params.append('dispositivo_id', filters.dispositivo_id);

      const response = await this.client.get('/asistencias/count', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Procesa los datos de asistencia para reportes
   * Agrupa por día y calcula horas trabajadas
   */
  processAttendanceData(attendances) {
    if (!Array.isArray(attendances) || attendances.length === 0) {
      return [];
    }

    // Agrupar por fecha
    const groupedByDate = {};
    
    attendances.forEach(record => {
      const date = new Date(record.timestamp).toISOString().split('T')[0];
      
      if (!groupedByDate[date]) {
        groupedByDate[date] = {
          fecha: date,
          registros: [],
          entrada: null,
          salida: null,
          horasTrabajadas: 0
        };
      }
      
      groupedByDate[date].registros.push(record);
      
      // Identificar entrada y salida (punch 0 = entrada, 1 = salida)
      if (record.punch === 0 && !groupedByDate[date].entrada) {
        groupedByDate[date].entrada = record.timestamp;
      }
      if (record.punch === 1) {
        groupedByDate[date].salida = record.timestamp;
      }
    });

    // Calcular horas trabajadas
    Object.keys(groupedByDate).forEach(date => {
      const day = groupedByDate[date];
      if (day.entrada && day.salida) {
        const entrada = new Date(day.entrada);
        const salida = new Date(day.salida);
        const diffMs = salida - entrada;
        day.horasTrabajadas = (diffMs / (1000 * 60 * 60)).toFixed(2);
      }
    });

    return Object.values(groupedByDate);
  }

  /**
   * Maneja errores de la API externa
   */
  handleError(error) {
    if (error.response) {
      // Error de respuesta del servidor
      return new Error(`API Error: ${error.response.status} - ${error.response.data?.message || error.message}`);
    } else if (error.request) {
      // No se recibió respuesta
      return new Error('No se pudo conectar con la API de asistencia');
    } else {
      // Error en la configuración de la petición
      return new Error(`Error: ${error.message}`);
    }
  }
}

export default new AttendanceApiService();

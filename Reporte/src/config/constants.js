import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: process.env.PORT || 3004,
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // Database
  databaseUrl: process.env.DATABASE_URL,
  
  // External API
  attendanceApiUrl: process.env.ATTENDANCE_API_URL || 'http://localhost:8000/api',
  
  // File Storage
  storagePath: process.env.STORAGE_PATH || './src/storage',
  maxFileSizeMB: parseInt(process.env.MAX_FILE_SIZE_MB) || 10,
  
  // Rate Limiting
  rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000, // 15 minutes
  rateLimitMaxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
};

export const REPORT_FORMATS = {
  XLSX: 'XLSX',
  PDF: 'PDF',
  CSV: 'CSV',
  JSON: 'JSON'
};

export const ATTENDANCE_STATUS = {
  1: 'Presente',
  0: 'Ausente',
  2: 'Tardanza',
  3: 'Permiso'
};

export const PUNCH_TYPES = {
  0: 'Entrada',
  1: 'Salida',
  2: 'Inicio Break',
  3: 'Fin Break',
  4: 'Inicio Almuerzo',
  5: 'Fin Almuerzo'
};

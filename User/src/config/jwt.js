require('dotenv').config();

/**
 * Configuración de JWT siguiendo mejores prácticas de seguridad OWASP
 */

// Validar que existe un secret en producción
if (process.env.NODE_ENV === 'production' && !process.env.JWT_SECRET) {
  throw new Error('JWT_SECRET es requerido en producción');
}

// Validar longitud mínima del secret
const secret = process.env.JWT_SECRET;
if (secret.length < 32) {
  console.warn('⚠️  ADVERTENCIA: JWT_SECRET debería tener al menos 32 caracteres para mayor seguridad');
}

module.exports = {
  /**
   * Clave secreta para firmar los tokens
   * CRÍTICO: Debe ser una clave larga y aleatoria en producción
   * Mínimo recomendado: 256 bits (32 caracteres)
   */
  secret: secret,
  
  /**
   * Tiempo de expiración del token de acceso
   * Formato: número + unidad (s=segundos, m=minutos, h=horas, d=días)
   * OWASP recomienda tokens de corta duración (15-60 minutos)
   * Ejemplo: '15m', '1h', '24h'
   */
  expiresIn: process.env.JWT_EXPIRE || '24h',
  
  /**
   * Tiempo de expiración del refresh token
   * Debe ser mayor que el token de acceso
   */
  refreshExpiresIn: process.env.JWT_REFRESH_EXPIRE || '7d',
  
  /**
   * Algoritmo de firma
   * HS256 es seguro para la mayoría de casos
   * Para mayor seguridad considerar RS256 (requiere par de claves pública/privada)
   */
  algorithm: 'HS256',
  
  /**
   * Emisor del token (opcional)
   * Útil para identificar la aplicación que emitió el token
   */
  issuer: process.env.JWT_ISSUER || 'api-rest-jwt',
  
  /**
   * Audiencia del token (opcional)
   * Identifica los destinatarios para los que el token está destinado
   */
  audience: process.env.JWT_AUDIENCE || 'api-users',
  
  /**
   * Configuración de cookies (si decides usar cookies en lugar de headers)
   */
  cookie: {
    httpOnly: true, // Previene acceso desde JavaScript (XSS)
    secure: process.env.NODE_ENV === 'production', // Solo HTTPS en producción
    sameSite: 'strict', // Protección contra CSRF
    maxAge: 24 * 60 * 60 * 1000, // 24 horas en milisegundos
    path: '/'
  }
};
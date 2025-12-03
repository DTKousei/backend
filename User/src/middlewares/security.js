const rateLimit = require('express-rate-limit');
const helmet = require('helmet');

/**
 * Configuración de Helmet para headers de seguridad HTTP
 * Implementa múltiples protecciones según OWASP Top 10
 */
const helmetConfig = helmet({
  // Content Security Policy - Previene XSS
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  
  // HTTP Strict Transport Security - Fuerza HTTPS
  hsts: {
    maxAge: 31536000, // 1 año
    includeSubDomains: true,
    preload: true
  },
  
  // X-Content-Type-Options - Previene MIME sniffing
  noSniff: true,
  
  // X-Frame-Options - Previene clickjacking
  frameguard: {
    action: 'deny'
  },
  
  // X-XSS-Protection - Protección XSS en navegadores antiguos
  xssFilter: true,
  
  // Ocultar el header X-Powered-By
  hidePoweredBy: true,
  
  // Referrer Policy - Controla información del referrer
  referrerPolicy: {
    policy: 'no-referrer'
  },
  
  // Permissions Policy (antes Feature Policy)
  permittedCrossDomainPolicies: {
    permittedPolicies: "none"
  }
});

/**
 * Rate limiting para proteger contra ataques de fuerza bruta en login
 * OWASP recomienda limitar intentos de autenticación
 */
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 5, // Máximo 5 intentos por ventana
  message: {
    success: false,
    message: 'Demasiados intentos de login desde esta IP. Por favor, intenta de nuevo en 15 minutos.',
    retryAfter: '15 minutos'
  },
  standardHeaders: true, // Retorna información en headers `RateLimit-*`
  legacyHeaders: false, // Deshabilita headers `X-RateLimit-*`
  skipSuccessfulRequests: true, // No contar requests exitosos
  skipFailedRequests: false, // Contar requests fallidos
  
  // Función personalizada para generar la clave del rate limit
  keyGenerator: (req) => {
    // Usar IP real incluso detrás de un proxy
    return req.ip || req.connection.remoteAddress;
  },
  
  // Handler cuando se excede el límite
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      message: 'Demasiados intentos de login. Tu cuenta ha sido temporalmente bloqueada por seguridad.',
      retryAfter: '15 minutos',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Rate limiting general para toda la API
 * Previene abuso y ataques DDoS básicos
 */
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // Máximo 100 requests por ventana por IP
  message: {
    success: false,
    message: 'Demasiadas peticiones desde esta IP. Por favor, intenta de nuevo más tarde.',
    retryAfter: '15 minutos'
  },
  standardHeaders: true,
  legacyHeaders: false,
  
  keyGenerator: (req) => {
    return req.ip || req.connection.remoteAddress;
  },
  
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      message: 'Límite de peticiones excedido. Por favor, espera antes de continuar.',
      retryAfter: '15 minutos',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Rate limiting estricto para operaciones sensibles
 * (cambio de contraseña, recuperación de cuenta, etc.)
 */
const strictLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hora
  max: 3, // Máximo 3 intentos por hora
  message: {
    success: false,
    message: 'Has excedido el límite de intentos para esta operación. Intenta de nuevo en 1 hora.',
    retryAfter: '1 hora'
  },
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: false,
  
  keyGenerator: (req) => {
    // Combinar IP y usuario (si está autenticado)
    const userId = req.user ? req.user.id : 'anonymous';
    return `${req.ip}-${userId}`;
  }
});

/**
 * Middleware para validar y sanitizar entrada de datos
 * Prevención básica de XSS y otros ataques de inyección
 */
const sanitizeInput = (req, res, next) => {
  // Función auxiliar para limpiar strings
  const clean = (str) => {
    if (typeof str !== 'string') return str;
    
    // Trim whitespace
    str = str.trim();
    
    // Limitar longitud para prevenir payloads enormes
    if (str.length > 10000) {
      str = str.substring(0, 10000);
    }
    
    return str;
  };
  
  // Limpiar body
  if (req.body && typeof req.body === 'object') {
    for (let key in req.body) {
      if (Object.prototype.hasOwnProperty.call(req.body, key)) {
        if (typeof req.body[key] === 'string') {
          req.body[key] = clean(req.body[key]);
        }
      }
    }
  }
  
  // Limpiar query params
  if (req.query && typeof req.query === 'object') {
    for (let key in req.query) {
      if (Object.prototype.hasOwnProperty.call(req.query, key)) {
        if (typeof req.query[key] === 'string') {
          req.query[key] = clean(req.query[key]);
        }
      }
    }
  }
  
  // Limpiar params
  if (req.params && typeof req.params === 'object') {
    for (let key in req.params) {
      if (Object.prototype.hasOwnProperty.call(req.params, key)) {
        if (typeof req.params[key] === 'string') {
          req.params[key] = clean(req.params[key]);
        }
      }
    }
  }
  
  next();
};

/**
 * Middleware para prevenir timing attacks en operaciones de autenticación
 * Añade un delay aleatorio mínimo para dificultar ataques de temporización
 */
const preventTimingAttack = (req, res, next) => {
  const startTime = Date.now();
  
  // Interceptar la respuesta
  const originalSend = res.send;
  res.send = function(data) {
    const duration = Date.now() - startTime;
    
    // Si la respuesta fue muy rápida (posible timing attack vector)
    if (duration < 100) {
      // Añadir delay aleatorio pequeño
      const delay = Math.random() * 50 + 50; // Entre 50-100ms
      setTimeout(() => {
        originalSend.call(this, data);
      }, delay);
    } else {
      originalSend.call(this, data);
    }
  };
  
  next();
};

/**
 * Middleware para validar Content-Type en requests POST/PUT/PATCH
 * Previene ciertos tipos de ataques
 */
const validateContentType = (req, res, next) => {
  if (['POST', 'PUT', 'PATCH'].includes(req.method)) {
    const contentType = req.headers['content-type'];
    
    if (!contentType) {
      return res.status(400).json({
        success: false,
        message: 'Content-Type header es requerido'
      });
    }
    
    // Permitir solo application/json
    if (!contentType.includes('application/json')) {
      return res.status(415).json({
        success: false,
        message: 'Content-Type no soportado. Use application/json'
      });
    }
  }
  
  next();
};

/**
 * Middleware para detectar y prevenir parameter pollution
 */
const preventParameterPollution = (req, res, next) => {
  // Verificar query params duplicados
  if (req.query) {
    for (let key in req.query) {
      if (Array.isArray(req.query[key])) {
        // Tomar solo el primer valor si hay duplicados
        req.query[key] = req.query[key][0];
      }
    }
  }
  
  next();
};

/**
 * Middleware para logging de seguridad
 * Registra eventos sospechosos
 */
const securityLogger = (req, res, next) => {
  const suspiciousPatterns = [
    /(\.|%2e){2,}/i, // Path traversal
    /<script/i, // XSS
    /union.*select/i, // SQL Injection
    /javascript:/i, // XSS
    /on\w+\s*=/i, // Event handlers (XSS)
  ];
  
  const checkSuspicious = (str) => {
    return suspiciousPatterns.some(pattern => pattern.test(str));
  };
  
  // Verificar en URL, query y body
  const url = req.originalUrl || req.url;
  const query = JSON.stringify(req.query);
  const body = JSON.stringify(req.body);
  
  if (checkSuspicious(url) || checkSuspicious(query) || checkSuspicious(body)) {
    console.warn('⚠️  ACTIVIDAD SOSPECHOSA DETECTADA:', {
      ip: req.ip,
      method: req.method,
      url: url,
      timestamp: new Date().toISOString(),
      userAgent: req.headers['user-agent']
    });
  }
  
  next();
};

module.exports = {
  helmetConfig,
  loginLimiter,
  apiLimiter,
  strictLimiter,
  sanitizeInput,
  preventTimingAttack,
  validateContentType,
  preventParameterPollution,
  securityLogger
};
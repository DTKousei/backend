const jwt = require('jsonwebtoken');
const jwtConfig = require('../config/jwt.js');

/**
 * Genera un token JWT
 * @param {Object} payload - Datos a incluir en el token
 * @param {String} expiresIn - Tiempo de expiración
 * @returns {String} Token JWT
 */
const generateToken = (payload, expiresIn = jwtConfig.expiresIn) => {
  return jwt.sign(payload, jwtConfig.secret, {
    expiresIn,
    algorithm: jwtConfig.algorithm
  });
};

/**
 * Verifica y decodifica un token JWT
 * @param {String} token - Token a verificar
 * @returns {Object} Payload decodificado
 */
const verifyToken = (token) => {
  try {
    return jwt.verify(token, jwtConfig.secret, {
      algorithms: [jwtConfig.algorithm]
    });
  } catch (error) {
    throw new Error('Token inválido o expirado');
  }
};

/**
 * Decodifica un token sin verificar (usar con precaución)
 * @param {String} token - Token a decodificar
 * @returns {Object} Payload decodificado
 */
const decodeToken = (token) => {
  return jwt.decode(token);
};

module.exports = {
  generateToken,
  verifyToken,
  decodeToken
};
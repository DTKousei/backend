const bcrypt = require('bcryptjs');

/**
 * Hashea una contraseña usando bcrypt
 * OWASP recomienda al menos 10 rounds, usamos 12 para mayor seguridad
 * @param {String} password - Contraseña en texto plano
 * @returns {Promise<String>} Contraseña hasheada
 */
const hashPassword = async (password) => {
  try {
    const saltRounds = 12; // OWASP recomienda entre 10-12
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    return hashedPassword;
  } catch (error) {
    throw new Error('Error al hashear la contraseña: ' + error.message);
  }
};

/**
 * Compara una contraseña con su hash de forma segura
 * Previene timing attacks usando bcrypt.compare
 * @param {String} password - Contraseña en texto plano
 * @param {String} hash - Hash almacenado en la base de datos
 * @returns {Promise<Boolean>} True si coinciden, False si no
 */
const comparePassword = async (password, hash) => {
  try {
    const isMatch = await bcrypt.compare(password, hash);
    return isMatch;
  } catch (error) {
    throw new Error('Error al comparar contraseñas: ' + error.message);
  }
};

/**
 * Valida la fortaleza de una contraseña según OWASP
 * @param {String} password - Contraseña a validar
 * @returns {Object} { isValid: boolean, errors: string[] }
 */
const validatePasswordStrength = (password) => {
  const errors = [];
  
  if (!password || password.length < 8) {
    errors.push('La contraseña debe tener al menos 8 caracteres');
  }
  
  if (password.length > 128) {
    errors.push('La contraseña no debe exceder 128 caracteres');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('La contraseña debe contener al menos una letra minúscula');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('La contraseña debe contener al menos una letra mayúscula');
  }
  
  if (!/\d/.test(password)) {
    errors.push('La contraseña debe contener al menos un número');
  }
  
  if (!/[@$!%*?&]/.test(password)) {
    errors.push('La contraseña debe contener al menos un carácter especial (@$!%*?&)');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Genera una contraseña aleatoria segura
 * @param {Number} length - Longitud de la contraseña (mínimo 12)
 * @returns {String} Contraseña generada
 */
const generateSecurePassword = (length = 16) => {
  const minLength = Math.max(length, 12);
  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const numbers = '0123456789';
  const symbols = '@$!%*?&';
  
  const allChars = lowercase + uppercase + numbers + symbols;
  
  // Asegurar que tenga al menos un carácter de cada tipo
  let password = '';
  password += lowercase[Math.floor(Math.random() * lowercase.length)];
  password += uppercase[Math.floor(Math.random() * uppercase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += symbols[Math.floor(Math.random() * symbols.length)];
  
  // Completar el resto de la contraseña
  for (let i = password.length; i < minLength; i++) {
    password += allChars[Math.floor(Math.random() * allChars.length)];
  }
  
  // Mezclar los caracteres
  return password.split('').sort(() => Math.random() - 0.5).join('');
};

module.exports = {
  hashPassword,
  comparePassword,
  validatePasswordStrength,
  generateSecurePassword
};
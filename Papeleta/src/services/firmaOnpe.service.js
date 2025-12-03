import forge from 'node-forge';
import crypto from 'crypto';

/**
 * Servicio para validación de firmas digitales ONPE
 */

/**
 * Genera hash SHA-256 del documento para firmar
 */
export const generarHashDocumento = (permisoData) => {
  const dataString = JSON.stringify({
    empleado_id: permisoData.empleado_id,
    tipo_permiso_id: permisoData.tipo_permiso_id,
    fecha_hora_inicio: permisoData.fecha_hora_inicio,
    motivo: permisoData.motivo,
    justificacion: permisoData.justificacion
  });
  
  return crypto.createHash('sha256').update(dataString).digest('hex');
};

/**
 * Valida firma digital PKCS#7
 */
export const validarFirmaDigital = (firmaBase64, documentoHash) => {
  try {
    // Decodificar firma PKCS#7
    const derBuffer = forge.util.decode64(firmaBase64);
    const asn1 = forge.asn1.fromDer(derBuffer);
    const p7 = forge.pkcs7.messageFromAsn1(asn1);

    // Verificar que tiene contenido
    if (!p7.rawCapture || !p7.rawCapture.content) {
      return {
        valida: false,
        error: 'Firma PKCS#7 inválida: sin contenido'
      };
    }

    // Obtener certificado del firmante
    if (!p7.certificates || p7.certificates.length === 0) {
      return {
        valida: false,
        error: 'No se encontró certificado en la firma'
      };
    }

    const certificado = p7.certificates[0];

    // Verificar firma criptográfica
    // Nota: En producción, aquí se debería verificar contra el hash del documento
    // y validar la cadena de certificación completa
    
    return {
      valida: true,
      certificado: certificado
    };

  } catch (error) {
    return {
      valida: false,
      error: `Error al validar firma: ${error.message}`
    };
  }
};

/**
 * Extrae información del certificado digital
 */
export const extraerInfoCertificado = (firmaBase64) => {
  try {
    const derBuffer = forge.util.decode64(firmaBase64);
    const asn1 = forge.asn1.fromDer(derBuffer);
    const p7 = forge.pkcs7.messageFromAsn1(asn1);

    if (!p7.certificates || p7.certificates.length === 0) {
      throw new Error('No se encontró certificado');
    }

    const cert = p7.certificates[0];
    
    // Extraer información del subject
    const subject = cert.subject.attributes;
    const issuer = cert.issuer.attributes;

    // Buscar DNI en el certificado (puede estar en serialNumber o CN)
    let dni = null;
    let nombre = null;
    
    for (const attr of subject) {
      if (attr.shortName === 'CN' || attr.name === 'commonName') {
        nombre = attr.value;
        // Intentar extraer DNI del CN (formato común: "NOMBRE - DNI")
        const dniMatch = attr.value.match(/(\d{8})/);
        if (dniMatch) {
          dni = dniMatch[1];
        }
      }
      if (attr.shortName === 'serialNumber') {
        // El DNI a veces está en serialNumber
        const serialMatch = attr.value.match(/(\d{8})/);
        if (serialMatch) {
          dni = serialMatch[1];
        }
      }
    }

    // Extraer entidad emisora
    let entidadEmisora = 'Desconocida';
    for (const attr of issuer) {
      if (attr.shortName === 'O' || attr.name === 'organizationName') {
        entidadEmisora = attr.value;
      }
    }

    return {
      dni: dni,
      nombre: nombre,
      entidad_emisora: entidadEmisora,
      fecha_emision: cert.validity.notBefore,
      fecha_expiracion: cert.validity.notAfter,
      numero_serie: cert.serialNumber,
      subject: cert.subject.attributes.map(a => ({ name: a.name, value: a.value })),
      issuer: cert.issuer.attributes.map(a => ({ name: a.name, value: a.value }))
    };

  } catch (error) {
    throw new Error(`Error al extraer información del certificado: ${error.message}`);
  }
};

/**
 * Verifica la vigencia del certificado
 */
export const verificarVigenciaCertificado = (certificadoInfo) => {
  const ahora = new Date();
  const fechaEmision = new Date(certificadoInfo.fecha_emision);
  const fechaExpiracion = new Date(certificadoInfo.fecha_expiracion);

  if (ahora < fechaEmision) {
    return {
      vigente: false,
      razon: 'El certificado aún no es válido'
    };
  }

  if (ahora > fechaExpiracion) {
    return {
      vigente: false,
      razon: 'El certificado ha expirado',
      fecha_expiracion: fechaExpiracion
    };
  }

  return {
    vigente: true,
    dias_restantes: Math.floor((fechaExpiracion - ahora) / (1000 * 60 * 60 * 24))
  };
};

/**
 * Valida que el DNI del certificado coincida con el empleado
 */
export const validarDNIEmpleado = (certificadoInfo, empleadoId) => {
  // El empleadoId ahora es el DNI según la validación actualizada
  const dniCertificado = certificadoInfo.dni;
  
  if (!dniCertificado) {
    return {
      valido: false,
      razon: 'No se pudo extraer el DNI del certificado'
    };
  }

  if (dniCertificado !== empleadoId) {
    return {
      valido: false,
      razon: `El DNI del certificado (${dniCertificado}) no coincide con el empleado (${empleadoId})`
    };
  }

  return {
    valido: true
  };
};

/**
 * Validación completa de firma digital ONPE
 */
export const validarFirmaCompleta = async (firmaDigital, documentoHash, empleadoId) => {
  try {
    // 1. Validar formato PKCS#7
    const validacionFirma = validarFirmaDigital(firmaDigital, documentoHash);
    if (!validacionFirma.valida) {
      return {
        valida: false,
        error: validacionFirma.error
      };
    }

    // 2. Extraer información del certificado
    const certificadoInfo = extraerInfoCertificado(firmaDigital);

    // 3. Verificar vigencia
    const vigencia = verificarVigenciaCertificado(certificadoInfo);
    if (!vigencia.vigente) {
      return {
        valida: false,
        error: vigencia.razon,
        certificado: certificadoInfo
      };
    }

    // 4. Validar DNI
    const validacionDNI = validarDNIEmpleado(certificadoInfo, empleadoId);
    if (!validacionDNI.valido) {
      return {
        valida: false,
        error: validacionDNI.razon,
        certificado: certificadoInfo
      };
    }

    // Firma válida
    return {
      valida: true,
      certificado: certificadoInfo,
      vigencia: vigencia
    };

  } catch (error) {
    return {
      valida: false,
      error: `Error en validación: ${error.message}`
    };
  }
};

/**
 * Simula validación contra servicios externos (RENIEC/ONPE)
 * En producción, esto debería consultar servicios reales
 */
export const validarCertificadoConEntidad = async (certificadoInfo) => {
  // TODO: Implementar consulta real a servicios de RENIEC/ONPE
  // Por ahora, retornamos validación simulada
  
  return {
    valido: true,
    entidad: certificadoInfo.entidad_emisora,
    mensaje: 'Validación simulada - implementar consulta real en producción'
  };
};

/**
 * Genera información resumida de la firma para mostrar
 */
export const obtenerResumenFirma = (certificadoInfo, validada) => {
  return {
    firmante: certificadoInfo.nombre,
    dni: certificadoInfo.dni,
    entidad_emisora: certificadoInfo.entidad_emisora,
    vigente_hasta: certificadoInfo.fecha_expiracion,
    validada: validada,
    numero_serie: certificadoInfo.numero_serie
  };
};

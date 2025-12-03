/**
 * Firmar permiso con firma digital ONPE
 */
export const firmarPermisoDigital = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { tipo_firma, firma_digital, certificado } = req.body;

    // Obtener permiso con tipo de permiso
    const permiso = await prisma.permiso.findUnique({
      where: { id },
      include: { tipo_permiso: true, estado: true }
    });

    if (!permiso) {
      throw new AppError(ERROR_MESSAGES.PERMISO_NOT_FOUND, 404);
    }

    // Validar orden de firma
    const validacionOrden = validarOrdenFirma(permiso, tipo_firma, permiso.tipo_permiso);
    if (!validacionOrden.valido) {
      throw new AppError(validacionOrden.mensaje, 400);
    }

    // Verificar que no exista ya esta firma
    const campoFirmaDigital = `firma_${tipo_firma}_digital`;
    if (permiso[campoFirmaDigital]) {
      throw new AppError('Esta firma digital ya fue registrada', 400);
    }

    // Generar hash del documento si no existe
    let documentoHash = permiso.documento_hash;
    if (!documentoHash) {
      documentoHash = generarHashDocumento(permiso);
    }

    // Validar firma digital completa
    const validacion = await validarFirmaCompleta(
      firma_digital,
      documentoHash,
      permiso.empleado_id
    );

    if (!validacion.valida) {
      throw new AppError(validacion.error || 'Firma digital inválida', 400);
    }

    // Generar QR de verificación
    const qrInfo = await generarQRVerificacion(
      id,
      tipo_firma,
      validacion.certificado
    );

    // Preparar datos de actualización
    const dataActualizacion = {
      [campoFirmaDigital]: firma_digital,
      [`firma_${tipo_firma}_en`]: new Date(),
      [`certificado_${tipo_firma}`]: validacion.certificado,
      [`firma_${tipo_firma}_validada`]: validacion.valida,
      [`metodo_firma_${tipo_firma}`]: METODO_FIRMA.ONPE,
      documento_hash: documentoHash
    };

    // Actualizar estado si todas las firmas están completas
    const permisoConNuevaFirma = { ...permiso, ...dataActualizacion };
    const validacionFirmas = validarFirmasRequeridas(
      permisoConNuevaFirma,
      permiso.tipo_permiso
    );

    if (validacionFirmas.completo) {
      const estadoAprobado = await prisma.estado.findFirst({
        where: { codigo: ESTADO_PERMISO.APROBADO }
      });

      if (estadoAprobado) {
        dataActualizacion.estado_id = estadoAprobado.id;
      }
    }

    // Actualizar permiso
    const permisoActualizado = await prisma.permiso.update({
      where: { id },
      data: dataActualizacion,
      include: {
        tipo_permiso: true,
        estado: true
      }
    });

    res.json({
      success: true,
      message: 'Firma digital registrada exitosamente',
      data: permisoActualizado,
      certificado: validacion.certificado,
      qr_verificacion: qrInfo.qr_data_url,
      url_verificacion: qrInfo.url_verificacion,
      firmas_completas: validacionFirmas.completo
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Verificar firma digital de un permiso
 */
export const verificarFirmaDigital = async (req, res, next) => {
  try {
    const { id, tipoFirma } = req.params;
    const { hash } = req.query;

    const permiso = await prisma.permiso.findUnique({
      where: { id },
      include: {
        tipo_permiso: true,
        estado: true
      }
    });

    if (!permiso) {
      throw new AppError(ERROR_MESSAGES.PERMISO_NOT_FOUND, 404);
    }

    // Obtener información de la firma
    const campoFirmaDigital = `firma_${tipoFirma}_digital`;
    const campoCertificado = `certificado_${tipoFirma}`;
    const campoValidada = `firma_${tipoFirma}_validada`;
    const campoFechaFirma = `firma_${tipoFirma}_en`;
    const campoMetodo = `metodo_firma_${tipoFirma}`;

    if (!permiso[campoFirmaDigital]) {
      throw new AppError('No existe firma digital para este tipo', 404);
    }

    const certificadoInfo = permiso[campoCertificado];
    const validada = permiso[campoValidada];
    const fechaFirma = permiso[campoFechaFirma];
    const metodo = permiso[campoMetodo];

    res.json({
      success: true,
      data: {
        permiso_id: id,
        tipo_firma: tipoFirma,
        metodo_firma: metodo,
        validada: validada,
        firmante: {
          nombre: certificadoInfo.nombre,
          dni: certificadoInfo.dni,
          cargo: tipoFirma.replace('_', ' ').toUpperCase()
        },
        certificado: {
          entidad_emisora: certificadoInfo.entidad_emisora,
          numero_serie: certificadoInfo.numero_serie,
          vigente_desde: certificadoInfo.fecha_emision,
          vigente_hasta: certificadoInfo.fecha_expiracion
        },
        fecha_firma: fechaFirma,
        documento_hash: permiso.documento_hash,
        permiso: {
          empleado_id: permiso.empleado_id,
          tipo_permiso: permiso.tipo_permiso.nombre,
          estado: permiso.estado.nombre,
          fecha_inicio: permiso.fecha_hora_inicio
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar firma tradicional para soportar método
 */
export const firmarPermisoTradicional = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { tipo_firma, firma } = req.body;

    // Obtener permiso con tipo de permiso
    const permiso = await prisma.permiso.findUnique({
      where: { id },
      include: { tipo_permiso: true, estado: true }
    });

    if (!permiso) {
      throw new AppError(ERROR_MESSAGES.PERMISO_NOT_FOUND, 404);
    }

    // Validar orden de firma
    const validacionOrden = validarOrdenFirma(permiso, tipo_firma, permiso.tipo_permiso);
    if (!validacionOrden.valido) {
      throw new AppError(validacionOrden.mensaje, 400);
    }

    // Verificar que no exista ya esta firma
    const campoFirma = `firma_${tipo_firma}`;
    if (permiso[campoFirma]) {
      throw new AppError(ERROR_MESSAGES.FIRMA_YA_EXISTE, 400);
    }

    // Preparar datos de actualización
    const dataActualizacion = {
      [campoFirma]: firma,
      [`${campoFirma}_en`]: new Date(),
      [`metodo_firma_${tipo_firma}`]: METODO_FIRMA.BASE64
    };

    // Actualizar estado si todas las firmas están completas
    const permisoConNuevaFirma = { ...permiso, ...dataActualizacion };
    const validacionFirmas = validarFirmasRequeridas(
      permisoConNuevaFirma,
      permiso.tipo_permiso
    );

    if (validacionFirmas.completo) {
      const estadoAprobado = await prisma.estado.findFirst({
        where: { codigo: ESTADO_PERMISO.APROBADO }
      });

      if (estadoAprobado) {
        dataActualizacion.estado_id = estadoAprobado.id;
      }
    }

    // Actualizar permiso
    const permisoActualizado = await prisma.permiso.update({
      where: { id },
      data: dataActualizacion,
      include: {
        tipo_permiso: true,
        estado: true
      }
    });

    res.json({
      success: true,
      message: SUCCESS_MESSAGES.FIRMA_REGISTRADA,
      data: permisoActualizado,
      firmas_completas: validacionFirmas.completo
    });
  } catch (error) {
    next(error);
  }
};

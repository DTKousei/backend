import prisma from '../config/database.js';
import { AppError } from '../middleware/error.middleware.js';
import { ERROR_MESSAGES, SUCCESS_MESSAGES, ESTADO_PERMISO, METODO_FIRMA } from '../utils/constants.js';
import { calcularHoraSalida, validarTiempoPermiso } from '../services/horario.service.js';
import { validarOrdenFirma, validarFirmasRequeridas } from '../services/firma.service.js';
import { generarPDFPapeleta } from '../services/pdf.service.js';
import { 
  validarFirmaCompleta, 
  extraerInfoCertificado,
  generarHashDocumento 
} from '../services/firmaOnpe.service.js';
import { generarQRVerificacion } from '../services/qr.service.js';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Obtener todos los permisos con filtros
 */
export const obtenerPermisos = async (req, res, next) => {
  try {
    const {
      empleado_id,
      tipo_permiso_id,
      estado_id,
      fecha_desde,
      fecha_hasta,
      page = 1,
      limit = 10
    } = req.query;

    const where = {};

    if (empleado_id) where.empleado_id = empleado_id;
    if (tipo_permiso_id) where.tipo_permiso_id = tipo_permiso_id;
    if (estado_id) where.estado_id = estado_id;

    if (fecha_desde || fecha_hasta) {
      where.fecha_hora_inicio = {};
      if (fecha_desde) where.fecha_hora_inicio.gte = new Date(fecha_desde);
      if (fecha_hasta) where.fecha_hora_inicio.lte = new Date(fecha_hasta);
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const take = parseInt(limit);

    const [permisos, total] = await Promise.all([
      prisma.permiso.findMany({
        where,
        include: {
          tipo_permiso: true,
          estado: true
        },
        orderBy: { creado_en: 'desc' },
        skip,
        take
      }),
      prisma.permiso.count({ where })
    ]);

    res.json({
      success: true,
      data: permisos,
      pagination: {
        total,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener un permiso por ID
 */
export const obtenerPermisoPorId = async (req, res, next) => {
  try {
    const { id } = req.params;

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

    res.json({
      success: true,
      data: permiso
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Crear un nuevo permiso
 */
export const crearPermiso = async (req, res, next) => {
  try {
    const {
      empleado_id,
      tipo_permiso_id,
      fecha_hora_inicio,
      fecha_hora_fin,
      motivo,
      justificacion,
      institucion_visitada
    } = req.body;

    // Obtener tipo de permiso
    const tipoPermiso = await prisma.permisoTipo.findUnique({
      where: { id: tipo_permiso_id }
    });

    if (!tipoPermiso) {
      throw new AppError(ERROR_MESSAGES.TIPO_PERMISO_NOT_FOUND, 404);
    }

    if (!tipoPermiso.esta_activo) {
      throw new AppError('Este tipo de permiso no está activo', 400);
    }

    // Validar tiempo del permiso
    if (fecha_hora_fin) {
      const validacion = validarTiempoPermiso(
        fecha_hora_inicio,
        fecha_hora_fin,
        tipoPermiso
      );

      if (!validacion.valido) {
        throw new AppError(validacion.mensaje, 400);
      }
    }

    // Calcular hora de salida
    const horaSalida = calcularHoraSalida(
      fecha_hora_inicio,
      fecha_hora_fin,
      tipoPermiso
    );

    // Obtener estado "PENDIENTE"
    let estadoPendiente = await prisma.estado.findFirst({
      where: { codigo: ESTADO_PERMISO.PENDIENTE }
    });

    // Si no existe, crear el estado pendiente
    if (!estadoPendiente) {
      estadoPendiente = await prisma.estado.create({
        data: {
          nombre: 'Pendiente',
          codigo: ESTADO_PERMISO.PENDIENTE,
          descripcion: 'Permiso pendiente de aprobación'
        }
      });
    }

    // Crear permiso
    const permiso = await prisma.permiso.create({
      data: {
        empleado_id,
        tipo_permiso_id,
        estado_id: estadoPendiente.id,
        fecha_hora_inicio: new Date(fecha_hora_inicio),
        fecha_hora_fin: fecha_hora_fin ? new Date(fecha_hora_fin) : null,
        hora_salida_calculada: horaSalida,
        motivo,
        justificacion,
        institucion_visitada: tipoPermiso.requiere_firma_institucion ? institucion_visitada : null
      },
      include: {
        tipo_permiso: true,
        estado: true
      }
    });

    res.status(201).json({
      success: true,
      message: SUCCESS_MESSAGES.PERMISO_CREADO,
      data: permiso
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar un permiso
 */
export const actualizarPermiso = async (req, res, next) => {
  try {
    const { id } = req.params;
    const {
      fecha_hora_inicio,
      fecha_hora_fin,
      motivo,
      justificacion,
      institucion_visitada
    } = req.body;

    // Obtener permiso actual
    const permisoActual = await prisma.permiso.findUnique({
      where: { id },
      include: { tipo_permiso: true }
    });

    if (!permisoActual) {
      throw new AppError(ERROR_MESSAGES.PERMISO_NOT_FOUND, 404);
    }

    // Preparar datos de actualización
    const dataActualizacion = {};

    if (fecha_hora_inicio) {
      dataActualizacion.fecha_hora_inicio = new Date(fecha_hora_inicio);
    }

    if (fecha_hora_fin !== undefined) {
      dataActualizacion.fecha_hora_fin = fecha_hora_fin ? new Date(fecha_hora_fin) : null;
    }

    // Recalcular hora de salida si cambian las fechas
    if (fecha_hora_inicio || fecha_hora_fin !== undefined) {
      const nuevaFechaInicio = fecha_hora_inicio || permisoActual.fecha_hora_inicio;
      const nuevaFechaFin = fecha_hora_fin !== undefined ? fecha_hora_fin : permisoActual.fecha_hora_fin;

      if (nuevaFechaFin) {
        const validacion = validarTiempoPermiso(
          nuevaFechaInicio,
          nuevaFechaFin,
          permisoActual.tipo_permiso
        );

        if (!validacion.valido) {
          throw new AppError(validacion.mensaje, 400);
        }
      }

      const horaSalida = calcularHoraSalida(
        nuevaFechaInicio,
        nuevaFechaFin,
        permisoActual.tipo_permiso
      );

      dataActualizacion.hora_salida_calculada = horaSalida;
    }

    if (motivo) dataActualizacion.motivo = motivo;
    if (justificacion) dataActualizacion.justificacion = justificacion;
    if (institucion_visitada !== undefined) {
      dataActualizacion.institucion_visitada = institucion_visitada;
    }

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
      message: SUCCESS_MESSAGES.PERMISO_ACTUALIZADO,
      data: permisoActualizado
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Eliminar un permiso
 */
export const eliminarPermiso = async (req, res, next) => {
  try {
    const { id } = req.params;

    const permiso = await prisma.permiso.findUnique({
      where: { id }
    });

    if (!permiso) {
      throw new AppError(ERROR_MESSAGES.PERMISO_NOT_FOUND, 404);
    }

    // Eliminar PDFs asociados si existen
    if (permiso.pdf_generado_path) {
      const rutaPDF = path.join(__dirname, '../..', permiso.pdf_generado_path);
      if (fs.existsSync(rutaPDF)) {
        fs.unlinkSync(rutaPDF);
      }
    }

    if (permiso.pdf_firmado_path) {
      const rutaPDF = path.join(__dirname, '../..', permiso.pdf_firmado_path);
      if (fs.existsSync(rutaPDF)) {
        fs.unlinkSync(rutaPDF);
      }
    }

    await prisma.permiso.delete({
      where: { id }
    });

    res.json({
      success: true,
      message: SUCCESS_MESSAGES.PERMISO_ELIMINADO
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Agregar firma a un permiso
 */
export const firmarPermiso = async (req, res, next) => {
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
      [`${campoFirma}_en`]: new Date()
    };

    // Actualizar estados intermedios
    if (tipo_firma === TIPO_FIRMA.JEFE_AREA) {
      const estadoJefe = await prisma.estado.findFirst({ 
        where: { codigo: ESTADO_PERMISO.APROBADO_JEFE } 
      });
      if (estadoJefe) {
        dataActualizacion.estado_id = estadoJefe.id;
      }
    } else if (tipo_firma === TIPO_FIRMA.RRHH) {
      const estadoRRHH = await prisma.estado.findFirst({ 
        where: { codigo: ESTADO_PERMISO.APROBADO_RRHH } 
      });
      if (estadoRRHH) {
        dataActualizacion.estado_id = estadoRRHH.id;
      }
    }

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

/**
 * Ver PDF de la papeleta en el navegador
 */
export const verPDF = async (req, res, next) => {
  try {
    const { id } = req.params;

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

    // Definir nombre de archivo personalizado usando el ID
    const numeroPapeleta = permiso.id.substring(0, 8).toUpperCase();
    const nombreArchivo = `papeleta_${numeroPapeleta}.pdf`;
    const rutaRelativa = `/generated/${nombreArchivo}`;
    const rutaAbsoluta = path.join(__dirname, '../../generated', nombreArchivo);

    // Verificar si ya existe el archivo físico
    if (fs.existsSync(rutaAbsoluta)) {
        // Verificar si la BD tiene la ruta correcta, si no, actualizarla
        if (permiso.pdf_generado_path !== rutaRelativa) {
             await prisma.permiso.update({
                where: { id },
                data: { pdf_generado_path: rutaRelativa }
             });
        }
        
        // Servir el archivo existente
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `inline; filename="${nombreArchivo}"`);
        return res.sendFile(rutaAbsoluta);
    }

    // Si no existe, generarlo
    // Obtener datos externos del empleado (misma lógica que generarPDF)
    const empleadoInfo = {};
    try {
      const [userRes, deptoRes] = await Promise.all([
        fetch(`http://localhost:8000/api/usuarios/user_id/${permiso.empleado_id}`).catch(err => ({ ok: false, err })),
        fetch(`http://localhost:8000/api/departamentos/usuario/${permiso.empleado_id}`).catch(err => ({ ok: false, err }))
      ]);

      if (userRes.ok) {
        const userData = await userRes.json();
        const user = userData.data || userData;
        empleadoInfo.nombre = user.nombre_completo || 
                            (user.nombres ? `${user.nombres} ${user.apellidos || ''}`.trim() : null) || 
                            user.nombre;
      }

      if (deptoRes.ok) {
        const deptoData = await deptoRes.json();
        const depto = deptoData.data || deptoData;
        empleadoInfo.area = depto.nombre || depto.nombre_departamento || depto.departamento;
      }
    } catch (error) {
      console.error('Error obteniendo datos externos para PDF:', error);
    }

    // Generar PDF con nombre personalizado
    const resultadoPDF = await generarPDFPapeleta(permiso, permiso.tipo_permiso, empleadoInfo, nombreArchivo);

    // Actualizar permiso con ruta del PDF
    await prisma.permiso.update({
      where: { id },
      data: {
        pdf_generado_path: resultadoPDF.rutaRelativa
      }
    });

    // Servir el archivo generado
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `inline; filename="${nombreArchivo}"`);
    res.sendFile(resultadoPDF.ruta);

  } catch (error) {
    next(error);
  }
};

/**
 * Generar PDF del permiso
 */
export const generarPDF = async (req, res, next) => {

  try {
    const { id } = req.params;

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

    // Obtener datos externos del empleado
    const empleadoInfo = {};
    try {
      // Usamos fetch nativo (Node 18+)
      const [userRes, deptoRes] = await Promise.all([
        fetch(`http://localhost:8000/api/usuarios/user_id/${permiso.empleado_id}`).catch(err => ({ ok: false, err })),
        fetch(`http://localhost:8000/api/departamentos/usuario/${permiso.empleado_id}`).catch(err => ({ ok: false, err }))
      ]);

      if (userRes.ok) {
        const userData = await userRes.json();
        // Soporte para diferentes estructuras de respuesta
        const user = userData.data || userData;
        empleadoInfo.nombre = user.nombre_completo || 
                            (user.nombres ? `${user.nombres} ${user.apellidos || ''}`.trim() : null) || 
                            user.nombre;
      }

      if (deptoRes.ok) {
        const deptoData = await deptoRes.json();
        const depto = deptoData.data || deptoData;
        empleadoInfo.area = depto.nombre || depto.nombre_departamento || depto.departamento;
      }
    } catch (error) {
      console.error('Error obteniendo datos externos para PDF:', error);
    }

    // Generar PDF
    const resultadoPDF = await generarPDFPapeleta(permiso, permiso.tipo_permiso, empleadoInfo);

    // Actualizar permiso con ruta del PDF
    await prisma.permiso.update({
      where: { id },
      data: {
        pdf_generado_path: resultadoPDF.rutaRelativa
      }
    });

    // Enviar archivo
    res.download(resultadoPDF.ruta, resultadoPDF.nombreArchivo, (err) => {
      if (err) {
        next(err);
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Cargar PDF firmado
 */
export const cargarPDFFirmado = async (req, res, next) => {
  try {
    const { id } = req.params;

    if (!req.file) {
      throw new AppError('No se ha cargado ningún archivo', 400);
    }

    const permiso = await prisma.permiso.findUnique({
      where: { id }
    });

    if (!permiso) {
      // Eliminar archivo cargado
      fs.unlinkSync(req.file.path);
      throw new AppError(ERROR_MESSAGES.PERMISO_NOT_FOUND, 404);
    }

    // Actualizar permiso con ruta del PDF firmado
    const rutaRelativa = `/uploads/${req.file.filename}`;

    const permisoActualizado = await prisma.permiso.update({
      where: { id },
      data: {
        pdf_firmado_path: rutaRelativa
      },
      include: {
        tipo_permiso: true,
        estado: true
      }
    });

    res.json({
      success: true,
      message: SUCCESS_MESSAGES.PDF_CARGADO,
      data: permisoActualizado,
      archivo: {
        nombre: req.file.filename,
        ruta: rutaRelativa,
        tamano: req.file.size
      }
    });
  } catch (error) {
    next(error);
  }
};

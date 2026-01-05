
import mime from 'mime-types'; // Needed for content-type setting

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

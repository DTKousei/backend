# API REST - Sistema de Papeletas (Permisos)

API REST completa para gestión de papeletas (permisos) con firmas electrónicas, generación de PDF y carga de documentos.

## 🚀 Características

- ✅ CRUD completo para tipos de permisos, estados y papeletas
- ✅ Gestión de firmas electrónicas con validación de orden
- ✅ Cálculo automático de horarios de salida según tipo de permiso
- ✅ Generación de PDF con firmas para impresión
- ✅ Carga de PDF firmado físicamente
- ✅ Validaciones completas de datos
- ✅ Manejo centralizado de errores

## 📋 Requisitos

- Node.js >= 16
- PostgreSQL >= 12
- npm o yarn

## 🔧 Instalación

1. **Clonar el repositorio o navegar al directorio del proyecto**

2. **Instalar dependencias**

```bash
npm install
```

3. **Configurar variables de entorno**

Copiar el archivo `.env.example` a `.env` y configurar:

```env
PORT=3000
NODE_ENV=development
DATABASE_URL="postgresql://usuario:password@localhost:5432/papeletas_db?schema=public"
```

4. **Generar cliente de Prisma**

```bash
npm run prisma:generate
```

5. **Ejecutar migraciones**

```bash
npm run prisma:migrate
```

6. **Poblar base de datos con datos iniciales**

```bash
node prisma/seed.js
```

## 🏃 Ejecución

### Modo desarrollo

```bash
npm run dev
```

### Modo producción

```bash
npm start
```

El servidor estará disponible en `http://localhost:3000`

---

## 🔐 Firmas Digitales ONPE

### Características

El sistema soporta **dos métodos de firma**:

1. **Firmas Tradicionales (Base64)**

   - Dibujar firma en canvas
   - Guardar como imagen base64
   - Ideal para usuarios sin certificado digital

2. **Firmas Digitales ONPE (PKCS#7)**
   - Certificados digitales de RENIEC/ONPE
   - Validación criptográfica
   - Códigos QR para verificación pública
   - Validez legal completa

### Endpoints de Firma Digital

```http
# Firmar con certificado digital
PATCH /api/permisos/:id/firmar-digital

# Verificar firma digital
GET /api/permisos/:id/verificar-firma/:tipoFirma
```

### Integración con Firma ONPE

Para usar firmas digitales, necesitas:

1. **Firma ONPE** instalado en el equipo del usuario
2. **Certificado digital** válido (RENIEC, ONPE, etc.)
3. Integración frontend (ver [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md))

**Ejemplo de uso:**

```javascript
// Desde el frontend
const { firma_digital, certificado } = await firmarConONPE(documentoHash);

await fetch("/api/permisos/123/firmar-digital", {
  method: "PATCH",
  body: JSON.stringify({
    tipo_firma: "solicitante",
    firma_digital,
    certificado,
  }),
});
```

Ver documentación completa en [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)

---

## 📚 Documentación de API

### Tipos de Permisos

#### Listar tipos de permisos

```http
GET /api/permiso-tipos
GET /api/permiso-tipos?activo=true
```

#### Obtener tipo de permiso por ID

```http
GET /api/permiso-tipos/:id
```

#### Crear tipo de permiso

```http
POST /api/permiso-tipos
Content-Type: application/json

{
  "nombre": "Permiso Médico",
  "codigo": "PERMISO_MEDICO",
  "descripcion": "Permiso por motivos médicos",
  "requiere_firma_institucion": false,
  "tiempo_maximo_horas": 4,
  "esta_activo": true
}
```

#### Actualizar tipo de permiso

```http
PUT /api/permiso-tipos/:id
Content-Type: application/json

{
  "nombre": "Permiso Médico Actualizado"
}
```

#### Eliminar tipo de permiso

```http
DELETE /api/permiso-tipos/:id
```

---

### Estados

#### Listar estados

```http
GET /api/estados
```

#### Obtener estado por ID

```http
GET /api/estados/:id
```

#### Crear estado

```http
POST /api/estados
Content-Type: application/json

{
  "nombre": "En Revisión",
  "codigo": "EN_REVISION",
  "descripcion": "Permiso en proceso de revisión"
}
```

---

### Permisos (Papeletas)

#### Listar permisos con filtros

```http
GET /api/permisos
GET /api/permisos?empleado_id=uuid&estado_id=uuid&page=1&limit=10
GET /api/permisos?fecha_desde=2024-01-01&fecha_hasta=2024-12-31
```

#### Obtener permiso por ID

```http
GET /api/permisos/:id
```

#### Crear permiso

```http
POST /api/permisos
Content-Type: application/json

{
  "empleado_id": "uuid-del-empleado",
  "tipo_permiso_id": "uuid-del-tipo-permiso",
  "fecha_hora_inicio": "2024-12-02T14:00:00",
  "fecha_hora_fin": "2024-12-02T16:00:00",
  "motivo": "Trámite personal",
  "justificacion": "Necesito realizar trámites bancarios urgentes",
  "institucion_visitada": "Banco de la Nación" // Solo para comisión de servicio
}
```

#### Actualizar permiso

```http
PUT /api/permisos/:id
Content-Type: application/json

{
  "motivo": "Motivo actualizado",
  "fecha_hora_fin": "2024-12-02T17:00:00"
}
```

#### Eliminar permiso

```http
DELETE /api/permisos/:id
```

#### Firmar permiso

```http
PATCH /api/permisos/:id/firmar
Content-Type: application/json

{
  "tipo_firma": "solicitante",
  "firma": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

**Tipos de firma válidos:**

- `solicitante` - Firma del empleado solicitante
- `jefe_area` - Firma del jefe de área
- `rrhh` - Firma de Recursos Humanos
- `institucion` - Firma de institución visitada (solo comisión de servicio)

**Orden de firmas:**

1. Solicitante
2. Jefe de Área
3. RRHH
4. Institución (si aplica)

#### Generar PDF

```http
GET /api/permisos/:id/pdf
```

Descarga un PDF con toda la información del permiso y las firmas.

#### Cargar PDF firmado

```http
POST /api/permisos/:id/upload-pdf
Content-Type: multipart/form-data

pdf: [archivo PDF]
```

---

## 🗂️ Estructura del Proyecto

```
Backend/Papeleta/
├── prisma/
│   ├── migrations/          # Migraciones de base de datos
│   ├── schema.prisma        # Esquema de Prisma
│   └── seed.js             # Datos iniciales
├── src/
│   ├── config/
│   │   ├── database.js     # Configuración de Prisma
│   │   └── upload.js       # Configuración de Multer
│   ├── controllers/
│   │   ├── estado.controller.js
│   │   ├── permiso.controller.js
│   │   └── permisoTipo.controller.js
│   ├── middleware/
│   │   ├── error.middleware.js
│   │   └── validation.middleware.js
│   ├── routes/
│   │   ├── estado.routes.js
│   │   ├── permiso.routes.js
│   │   └── permisoTipo.routes.js
│   ├── services/
│   │   ├── firma.service.js
│   │   ├── horario.service.js
│   │   └── pdf.service.js
│   ├── utils/
│   │   ├── constants.js
│   │   └── helpers.js
│   └── index.js            # Punto de entrada
├── uploads/                # PDFs cargados
├── generated/              # PDFs generados
├── .env                    # Variables de entorno
├── .env.example           # Ejemplo de variables
├── package.json
└── README.md
```

## 🔐 Reglas de Negocio

### Tipos de Permisos

1. **Comisión de Servicio**

   - Sin límite de tiempo (manual)
   - Requiere firma de institución visitada
   - Firmas: Solicitante → Jefe → RRHH → Institución

2. **Permiso Personal**
   - Máximo 2 horas
   - No requiere firma de institución
   - Firmas: Solicitante → Jefe → RRHH

### Flujo de Firmas

- Las firmas deben seguir un orden estricto
- No se puede firmar sin la firma previa correspondiente
- Cuando todas las firmas están completas, el estado cambia a "Aprobado"

### Horarios

- Para permisos con límite de tiempo: se calcula automáticamente la hora de salida
- Para comisión de servicio: la hora de retorno es manual

## 🛠️ Tecnologías

- **Node.js** - Runtime de JavaScript
- **Express.js** - Framework web
- **Prisma** - ORM para PostgreSQL
- **PostgreSQL** - Base de datos
- **PDFKit** - Generación de PDF
- **Multer** - Carga de archivos
- **express-validator** - Validación de datos

## 📝 Notas

- Las firmas se almacenan en formato base64
- Los PDFs generados se guardan en `/generated`
- Los PDFs cargados se guardan en `/uploads`
- Todos los endpoints retornan JSON
- Los errores se manejan de forma centralizada

## 🤝 Contribuir

1. Crear una rama para tu feature
2. Hacer commit de los cambios
3. Push a la rama
4. Crear un Pull Request

## 📄 Licencia

ISC

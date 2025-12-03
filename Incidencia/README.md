# API de Gestión de Incidencias - Guía Rápida

## 🚀 Inicio Rápido

### Iniciar el Servidor

```bash
npm run dev
```

El servidor estará disponible en: `http://localhost:3000`

---

## 📋 Endpoints Principales

### **Crear Incidencia con PDF**

```http
POST /api/incidencias
Content-Type: multipart/form-data

Form Data:
- empleado_id: "emp-123"
- tipo_incidencia_id: "<UUID>"
- fecha_inicio: "2025-12-03"
- fecha_fin: "2025-12-03"
- descripcion: "Cita médica"
- estado_id: "<UUID>"
- documento: <archivo.pdf>
```

### **Listar Incidencias**

```http
GET /api/incidencias?page=1&limit=10&empleado_id=emp-123
```

### **Aprobar Incidencia**

```http
PATCH /api/incidencias/:id/aprobar
Content-Type: application/json

{
  "aprobado_por": "supervisor-123"
}
```

### **Crear Tipo de Incidencia**

```http
POST /api/tipos-incidencia
Content-Type: application/json

{
  "nombre": "Permiso Médico",
  "codigo": "PM001",
  "requiere_aprobacion": true,
  "requiere_documento": true,
  "descuenta_salario": false,
  "esta_activo": true
}
```

### **Crear Estado**

```http
POST /api/estados
Content-Type: application/json

{
  "nombre": "Pendiente",
  "descripcion": "Incidencia pendiente de revisión"
}
```

---

## 📁 Almacenamiento de Archivos

Los archivos PDF se guardan en: **`C:\IncidenciasDocumentos`**

- ✅ Solo archivos PDF permitidos
- ✅ Tamaño máximo: 10 MB
- ✅ Nombres únicos automáticos
- ✅ Eliminación automática al borrar incidencias

---

## 🔧 Configuración

Edita el archivo `.env` con tu configuración:

```env
DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/nombre_bd"
PORT=3000
NODE_ENV=development
```

---

## ✅ Características

- 🔒 Seguridad con Helmet y CORS
- ⚡ Rate limiting (100 req/15min)
- ✅ Validación de datos robusta
- 📄 Paginación y filtros
- 🗑️ Limpieza automática de archivos
- 🛡️ Manejo de errores consistente

---

## 📚 Documentación Completa

Ver [walkthrough.md](file:///C:/Users/Asus/.gemini/antigravity/brain/df0c84ab-4889-41c3-8f55-5ed0501e1619/walkthrough.md) para documentación detallada.

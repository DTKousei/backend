# Integración Frontend con Firma ONPE

## 📱 Guía de Integración para el Frontend

Esta guía explica cómo integrar el frontend con la API de firmas digitales ONPE.

---

## 🔌 Comunicación con Firma ONPE Local

### Verificar Disponibilidad de Firma ONPE

```javascript
async function verificarFirmaONPE() {
  try {
    const response = await fetch("http://localhost:8080/status");
    return response.ok;
  } catch (error) {
    console.error("Firma ONPE no disponible:", error);
    return false;
  }
}
```

### Firmar Documento con ONPE

```javascript
async function firmarConONPE(documentoHash, razon = "Aprobación de papeleta") {
  try {
    const response = await fetch("http://localhost:8080/firmar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        documento: documentoHash,
        formato: "PKCS7",
        razon: razon,
      }),
    });

    if (!response.ok) {
      throw new Error("Error al firmar con ONPE");
    }

    const { firma, certificado } = await response.json();

    return {
      firma_digital: firma,
      certificado: certificado,
    };
  } catch (error) {
    console.error("Error en firma ONPE:", error);
    throw error;
  }
}
```

---

## 🎯 Flujo Completo de Firma Digital

### Ejemplo con Vue.js

```vue
<template>
  <div class="firma-digital-container">
    <h3>Firmar Papeleta</h3>

    <!-- Selector de método de firma -->
    <div class="metodo-firma">
      <label>
        <input type="radio" v-model="metodoFirma" value="base64" />
        Firma Tradicional (Dibujar)
      </label>
      <label>
        <input type="radio" v-model="metodoFirma" value="onpe" />
        Firma Digital ONPE
      </label>
    </div>

    <!-- Firma tradicional -->
    <div v-if="metodoFirma === 'base64'" class="firma-canvas">
      <canvas ref="canvasFirma" @mousedown="iniciarDib ujo"></canvas>
      <button @click="limpiarFirma">Limpiar</button>
      <button @click="firmarTradicional">Firmar</button>
    </div>

    <!-- Firma digital ONPE -->
    <div v-else class="firma-digital">
      <div v-if="!onpeDisponible" class="alert alert-warning">
        ⚠️ Firma ONPE no está disponible. Asegúrate de que la aplicación esté
        corriendo.
      </div>
      <button @click="firmarDigital" :disabled="!onpeDisponible || firmando">
        {{ firmando ? "Firmando..." : "Firmar con ONPE" }}
      </button>
    </div>

    <!-- Resultado -->
    <div v-if="firmaExitosa" class="alert alert-success">
      ✅ Firma registrada exitosamente
      <div v-if="qrVerificacion">
        <img :src="qrVerificacion" alt="QR Verificación" />
        <p>Escanea para verificar la firma</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      metodoFirma: "onpe", // 'base64' o 'onpe'
      onpeDisponible: false,
      firmando: false,
      firmaExitosa: false,
      qrVerificacion: null,
      permisoId: this.$route.params.id,
      tipoFirma: "solicitante", // o 'jefe_area', 'rrhh', 'institucion'
    };
  },

  async mounted() {
    // Verificar si Firma ONPE está disponible
    this.onpeDisponible = await this.verificarFirmaONPE();
  },

  methods: {
    async verificarFirmaONPE() {
      try {
        const response = await fetch("http://localhost:8080/status");
        return response.ok;
      } catch (error) {
        return false;
      }
    },

    async firmarDigital() {
      this.firmando = true;

      try {
        // 1. Obtener datos del permiso para generar hash
        const permiso = await this.obtenerPermiso(this.permisoId);

        // 2. Generar hash del documento (debe coincidir con el backend)
        const documentoHash = await this.generarHashDocumento(permiso);

        // 3. Firmar con ONPE
        const { firma_digital, certificado } = await this.firmarConONPE(
          documentoHash
        );

        // 4. Enviar firma digital a la API
        const response = await fetch(
          `http://localhost:3000/api/permisos/${this.permisoId}/firmar-digital`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              tipo_firma: this.tipoFirma,
              firma_digital: firma_digital,
              certificado: certificado,
            }),
          }
        );

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error || "Error al registrar firma");
        }

        const resultado = await response.json();

        this.firmaExitosa = true;
        this.qrVerificacion = resultado.qr_verificacion;

        this.$emit("firma-registrada", resultado);
      } catch (error) {
        console.error("Error al firmar:", error);
        alert(`Error: ${error.message}`);
      } finally {
        this.firmando = false;
      }
    },

    async firmarTradicional() {
      // Obtener firma del canvas como base64
      const canvas = this.$refs.canvasFirma;
      const firmaBase64 = canvas.toDataURL("image/png");

      try {
        const response = await fetch(
          `http://localhost:3000/api/permisos/${this.permisoId}/firmar`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              tipo_firma: this.tipoFirma,
              firma: firmaBase64,
            }),
          }
        );

        if (!response.ok) {
          throw new Error("Error al registrar firma");
        }

        this.firmaExitosa = true;
        this.$emit("firma-registrada");
      } catch (error) {
        console.error("Error:", error);
        alert("Error al registrar firma");
      }
    },

    async firmarConONPE(documentoHash) {
      const response = await fetch("http://localhost:8080/firmar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          documento: documentoHash,
          formato: "PKCS7",
          razon: `Firma de ${this.tipoFirma} para papeleta`,
        }),
      });

      if (!response.ok) {
        throw new Error("Error al firmar con ONPE");
      }

      return await response.json();
    },

    async obtenerPermiso(id) {
      const response = await fetch(`http://localhost:3000/api/permisos/${id}`);
      const data = await response.json();
      return data.data;
    },

    async generarHashDocumento(permiso) {
      // Debe coincidir con la lógica del backend
      const dataString = JSON.stringify({
        empleado_id: permiso.empleado_id,
        tipo_permiso_id: permiso.tipo_permiso_id,
        fecha_hora_inicio: permiso.fecha_hora_inicio,
        motivo: permiso.motivo,
        justificacion: permiso.justificacion,
      });

      // Usar Web Crypto API para generar SHA-256
      const encoder = new TextEncoder();
      const data = encoder.encode(dataString);
      const hashBuffer = await crypto.subtle.digest("SHA-256", data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");

      return hashHex;
    },

    limpiarFirma() {
      const canvas = this.$refs.canvasFirma;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    },

    iniciarDibujo(e) {
      // Implementar lógica de dibujo en canvas
      // ... código de dibujo ...
    },
  },
};
</script>

<style scoped>
.firma-digital-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.metodo-firma {
  margin: 20px 0;
}

.metodo-firma label {
  display: block;
  margin: 10px 0;
}

.firma-canvas canvas {
  border: 2px solid #ccc;
  cursor: crosshair;
}

.alert {
  padding: 15px;
  margin: 15px 0;
  border-radius: 4px;
}

.alert-warning {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
}

.alert-success {
  background-color: #d4edda;
  border: 1px solid #28a745;
}

button {
  padding: 10px 20px;
  margin: 5px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}
</style>
```

---

## 🔍 Verificar Firma Digital

### Componente de Verificación

```vue
<template>
  <div class="verificacion-firma">
    <h3>Verificar Firma Digital</h3>

    <div v-if="loading">Verificando...</div>

    <div v-else-if="firmaInfo" class="firma-info">
      <div class="status" :class="{ valida: firmaInfo.validada }">
        {{ firmaInfo.validada ? "✅ Firma Válida" : "❌ Firma Inválida" }}
      </div>

      <div class="detalles">
        <h4>Firmante</h4>
        <p><strong>Nombre:</strong> {{ firmaInfo.firmante.nombre }}</p>
        <p><strong>DNI:</strong> {{ firmaInfo.firmante.dni }}</p>
        <p><strong>Cargo:</strong> {{ firmaInfo.firmante.cargo }}</p>

        <h4>Certificado Digital</h4>
        <p>
          <strong>Entidad Emisora:</strong>
          {{ firmaInfo.certificado.entidad_emisora }}
        </p>
        <p>
          <strong>Vigente hasta:</strong>
          {{ formatearFecha(firmaInfo.certificado.vigente_hasta) }}
        </p>
        <p>
          <strong>Número de Serie:</strong>
          {{ firmaInfo.certificado.numero_serie }}
        </p>

        <h4>Información del Permiso</h4>
        <p><strong>Empleado:</strong> {{ firmaInfo.permiso.empleado_id }}</p>
        <p><strong>Tipo:</strong> {{ firmaInfo.permiso.tipo_permiso }}</p>
        <p><strong>Estado:</strong> {{ firmaInfo.permiso.estado }}</p>
        <p>
          <strong>Fecha de Firma:</strong>
          {{ formatearFecha(firmaInfo.fecha_firma) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    permisoId: String,
    tipoFirma: String,
  },

  data() {
    return {
      loading: true,
      firmaInfo: null,
    };
  },

  async mounted() {
    await this.verificarFirma();
  },

  methods: {
    async verificarFirma() {
      try {
        const response = await fetch(
          `http://localhost:3002/api/permisos/${this.permisoId}/verificar-firma/${this.tipoFirma}`
        );

        if (!response.ok) {
          throw new Error("Error al verificar firma");
        }

        const data = await response.json();
        this.firmaInfo = data.data;
      } catch (error) {
        console.error("Error:", error);
        alert("Error al verificar firma");
      } finally {
        this.loading = false;
      }
    },

    formatearFecha(fecha) {
      return new Date(fecha).toLocaleString("es-PE");
    },
  },
};
</script>

<style scoped>
.verificacion-firma {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.status {
  padding: 15px;
  margin: 20px 0;
  border-radius: 4px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
}

.status.valida {
  background-color: #d4edda;
  color: #155724;
  border: 2px solid #28a745;
}

.detalles {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
}

.detalles h4 {
  margin-top: 20px;
  color: #333;
}

.detalles p {
  margin: 5px 0;
}
</style>
```

---

## 📱 Escaneo de Código QR

### Componente para Escanear QR

```javascript
// Usando una librería como html5-qrcode

import { Html5Qrcode } from "html5-qrcode";

export default {
  data() {
    return {
      scanner: null,
      scanning: false,
    };
  },

  methods: {
    async iniciarEscaneo() {
      this.scanning = true;

      const scanner = new Html5Qrcode("qr-reader");

      try {
        await scanner.start(
          { facingMode: "environment" },
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
          },
          (decodedText) => {
            // decodedText es la URL de verificación
            this.verificarDesdeQR(decodedText);
            scanner.stop();
            this.scanning = false;
          }
        );
      } catch (error) {
        console.error("Error al iniciar scanner:", error);
        this.scanning = false;
      }
    },

    async verificarDesdeQR(url) {
      // Extraer permisoId y tipoFirma de la URL
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split("/");
      const permisoId = pathParts[pathParts.length - 3];
      const tipoFirma = pathParts[pathParts.length - 1];

      // Redirigir a página de verificación
      this.$router.push({
        name: "verificar-firma",
        params: { permisoId, tipoFirma },
      });
    },
  },
};
```

---

## 🔐 Consideraciones de Seguridad

### CORS

Asegúrate de configurar CORS correctamente en el backend para permitir peticiones desde tu frontend:

```javascript
// En el backend (ya configurado)
app.use(
  cors({
    origin: ["http://localhost:8080", "http://localhost:5173"], // Tus dominios
    credentials: true,
  })
);
```

### HTTPS

Para producción, **siempre usa HTTPS** tanto en el backend como en Firma ONPE.

### Validación

- Siempre valida las firmas en el backend
- No confíes solo en la validación del frontend
- Verifica que el DNI del certificado coincida con el empleado

---

## 📚 Recursos Adicionales

- [Documentación de Firma ONPE](https://www.onpe.gob.pe)
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
- [html5-qrcode](https://github.com/mebjas/html5-qrcode)

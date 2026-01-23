const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
const { getSaldosIncidencias } = require('./src/controllers/incidencias.controller');

// Mockear Express Request/Response
const mockRequest = (query = {}) => ({ query });
const mockResponse = () => {
  const res = {};
  res.status = (code) => {
    res.statusCode = code;
    return res;
  };
  res.json = (data) => {
    const fs = require('fs');
    fs.writeFileSync('verify_output.json', JSON.stringify(data, null, 2));
    console.log(JSON.stringify(data, null, 2));
    return res;
  };
  return res;
};
const mockNext = (err) => {
  if (err) console.error('Error:', err);
};

async function main() {
  console.log('--- Verificando Endpoint de Saldos (Specific) ---');
  try {
     const empId = '40126700'; // El del problema
     console.log('Consultando saldos para empleado:', empId);

     const req = mockRequest({ empleado_id: empId, anio: 2026 });
     const res = mockResponse();

     // Ejecutar controlador directamente
     await getSaldosIncidencias(req, res, mockNext);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

main();

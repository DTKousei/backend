const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
const { getSaldosIncidencias } = require('./src/controllers/incidencias.controller');

const mockRequest = (query = {}) => ({ query });
const mockResponse = () => {
  const res = {};
  res.status = (code) => {
    res.statusCode = code;
    return res;
  };
  res.json = (data) => {
    console.log(JSON.stringify(data, null, 2));
    return res;
  };
  return res;
};
const mockNext = (err) => {
  if (err) console.error('Error:', err);
};

async function main() {
  console.log('--- Verificando tipo_codigo ---');
  try {
     const req = mockRequest({ anio: 2026 });
     const res = mockResponse();
     await getSaldosIncidencias(req, res, mockNext);
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

main();

# Ejemplos de APIs de Horarios y Segmentos

Aquí tienes los ejemplos de uso (curl) para gestionar horarios, segmentos y feriados.

## 1. Gestión de Horarios

### Crear Horario

```bash
curl -X POST "http://localhost:8000/api/horarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Horario Oficina",
    "descripcion": "Lunes a Viernes 8am a 5pm",
    "activo": true
  }'
```

### Listar Horarios

```bash
curl -X GET "http://localhost:8000/api/horarios/?skip=0&limit=100"
```

### Obtener Horario por ID

```bash
curl -X GET "http://localhost:8000/api/horarios/1"
```

### Actualizar Horario

```bash
curl -X PUT "http://localhost:8000/api/horarios/1" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Horario Oficina Modificado",
    "activo": true
  }'
```

### Eliminar Horario

```bash
curl -X DELETE "http://localhost:8000/api/horarios/1"
```

---

## 2. Gestión de Segmentos (Turnos)

### Crear Segmento (Un solo turno)

Para agregar un turno a un horario existente (ej: ID 1).
`dia_semana`: 0=Lunes, 1=Martes, ..., 6=Domingo.

```bash
curl -X POST "http://localhost:8000/api/horarios/segmentos/" \
  -H "Content-Type: application/json" \
  -d '{
    "horario_id": 1,
    "dia_semana": 0,
    "hora_inicio": "08:00:00",
    "hora_fin": "13:00:00",
    "tolerancia_minutos": 15,
    "orden_turno": 1
  }'
```

### Crear Segmentos Masivos (Varios días a la vez)

Ejemplo: Crear turno de mañana (8:00-13:00) para Lunes a Viernes (0,1,2,3,4).

```bash
curl -X POST "http://localhost:8000/api/horarios/segmentos/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "horario_id": 1,
    "dias_semana": [0, 1, 2, 3, 4],
    "hora_inicio": "08:00:00",
    "hora_fin": "13:00:00",
    "tolerancia_minutos": 10,
    "orden_turno": 1
  }'
```

### Listar Segmentos de un Horario

```bash
curl -X GET "http://localhost:8000/api/horarios/1/segmentos"
```

### Actualizar Segmento (NUEVO)

Modificar un turno específico (ej: cambiar tolerancia o hora).
`segmento_id` es el ID único del segmento, no del horario.

```bash
curl -X PUT "http://localhost:8000/api/horarios/segmentos/5" \
  -H "Content-Type: application/json" \
  -d '{
    "hora_inicio": "08:30:00",
    "tolerancia_minutos": 5
  }'
```

### Eliminar Segmento

Borrar un turno específico.

```bash
curl -X DELETE "http://localhost:8000/api/horarios/segmentos/5"
```

---

## 3. Asignación de Horarios a Usuarios

### Asignar Horario

Asocia un horario a un usuario desde una fecha específica.

```bash
curl -X POST "http://localhost:8000/api/horarios/asignar" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345678",
    "horario_id": 1,
    "fecha_inicio": "2024-01-01T00:00:00",
    "fecha_fin": null
  }'
```

---

## 4. Feriados

### Crear Feriado

```bash
curl -X POST "http://localhost:8000/api/horarios/feriados/" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2024-12-25",
    "nombre": "Navidad"
  }'
```

### Listar Feriados

```bash
curl -X GET "http://localhost:8000/api/horarios/feriados/"
```

### Eliminar Feriado

```bash
curl -X DELETE "http://localhost:8000/api/horarios/feriados/1"
```

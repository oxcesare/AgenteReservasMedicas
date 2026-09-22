# Ejemplos de uso del endpoint de creación de disponibilidad

## Endpoint
POST /api/doctors/{id_doctor}/availability
PUT /api/doctors/{id_doctor}/availability/{id_slot}
DELETE /api/doctors/{id_doctor}/availability/{id_slot}

---

## Ejemplo 1: Lunes con 3 franjas horarias

```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "slots": [
    {
      "fecha": "2026-09-21",
      "franjas": [
        {
          "hora_inicio": "07:00",
          "hora_fin": "09:00"
        },
        {
          "hora_inicio": "09:30",
          "hora_fin": "11:30"
        },
        {
          "hora_inicio": "17:30",
          "hora_fin": "19:30"
        }
      ]
    }
  ]
}
```

---

## Ejemplo 2: Lunes y Martes con 3 franjas cada uno (Como en tu caso)

```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "slots": [
    {
      "fecha": "2026-09-21",
      "franjas": [
        {
          "hora_inicio": "07:00",
          "hora_fin": "09:00"
        },
        {
          "hora_inicio": "09:30",
          "hora_fin": "11:30"
        },
        {
          "hora_inicio": "17:30",
          "hora_fin": "19:30"
        }
      ]
    },
    {
      "fecha": "2026-09-22",
      "franjas": [
        {
          "hora_inicio": "07:00",
          "hora_fin": "09:00"
        },
        {
          "hora_inicio": "09:30",
          "hora_fin": "11:30"
        },
        {
          "hora_inicio": "17:30",
          "hora_fin": "19:30"
        }
      ]
    }
  ]
}
```

---

## Ejemplo 3: Una semana completa (Lunes a Viernes)

```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "slots": [
    {
      "fecha": "2026-09-21",
      "franjas": [
        {"hora_inicio": "08:00", "hora_fin": "12:00"},
        {"hora_inicio": "14:00", "hora_fin": "18:00"}
      ]
    },
    {
      "fecha": "2026-09-22",
      "franjas": [
        {"hora_inicio": "08:00", "hora_fin": "12:00"},
        {"hora_inicio": "14:00", "hora_fin": "18:00"}
      ]
    },
    {
      "fecha": "2026-09-23",
      "franjas": [
        {"hora_inicio": "08:00", "hora_fin": "12:00"},
        {"hora_inicio": "14:00", "hora_fin": "18:00"}
      ]
    },
    {
      "fecha": "2026-09-24",
      "franjas": [
        {"hora_inicio": "08:00", "hora_fin": "12:00"},
        {"hora_inicio": "14:00", "hora_fin": "18:00"}
      ]
    },
    {
      "fecha": "2026-09-25",
      "franjas": [
        {"hora_inicio": "08:00", "hora_fin": "12:00"},
        {"hora_inicio": "14:00", "hora_fin": "18:00"}
      ]
    }
  ]
}
```

---

## Ejemplo 4: Días con diferentes horarios

```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "slots": [
    {
      "fecha": "2026-09-21",
      "franjas": [
        {"hora_inicio": "07:00", "hora_fin": "09:00"},
        {"hora_inicio": "09:30", "hora_fin": "11:30"},
        {"hora_inicio": "17:30", "hora_fin": "19:30"}
      ]
    },
    {
      "fecha": "2026-09-22",
      "franjas": [
        {"hora_inicio": "06:00", "hora_fin": "10:00"},
        {"hora_inicio": "16:00", "hora_fin": "20:00"}
      ]
    },
    {
      "fecha": "2026-09-23",
      "franjas": [
        {"hora_inicio": "08:00", "hora_fin": "12:00"}
      ]
    }
  ]
}
```

---

## Respuesta exitosa (201 Created)

```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "total_slots_creados": 3,
  "detalles": [
    {
      "fecha": "2026-09-21",
      "hora_inicio": "07:00",
      "hora_fin": "09:00",
      "clinica_id": 1
    },
    {
      "fecha": "2026-09-21",
      "hora_inicio": "09:30",
      "hora_fin": "11:30",
      "clinica_id": 1
    },
    {
      "fecha": "2026-09-21",
      "hora_inicio": "17:30",
      "hora_fin": "19:30",
      "clinica_id": 1
    }
  ]
}
```

---

## Prueba con cURL

```bash
curl -X POST "http://localhost:8000/api/doctors/1/availability" \
  -H "Content-Type: application/json" \
  -d '{
    "id_doctor": 1,
    "id_clinica": 1,
    "slots": [
      {
        "fecha": "2026-09-21",
        "franjas": [
          {"hora_inicio": "07:00", "hora_fin": "09:00"},
          {"hora_inicio": "09:30", "hora_fin": "11:30"},
          {"hora_inicio": "17:30", "hora_fin": "19:30"}
        ]
      }
    ]
  }'
```

---

## Prueba con JavaScript/Fetch

```javascript
const createAvailability = async (id_doctor) => {
  const payload = {
    id_doctor: 1,
    id_clinica: 1,
    slots: [
      {
        fecha: "2026-09-21",
        franjas: [
          { hora_inicio: "07:00", hora_fin: "09:00" },
          { hora_inicio: "09:30", hora_fin: "11:30" },
          { hora_inicio: "17:30", hora_fin: "19:30" }
        ]
      },
      {
        fecha: "2026-09-22",
        franjas: [
          { hora_inicio: "07:00", hora_fin: "09:00" },
          { hora_inicio: "09:30", hora_fin": "11:30" },
          { hora_inicio: "17:30", hora_fin": "19:30" }
        ]
      }
    ]
  };

  try {
    const response = await fetch(
      `http://localhost:8000/api/doctors/${id_doctor}/availability`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }
    );

    const data = await response.json();
    console.log("Slots creados:", data);
    return data;
  } catch (error) {
    console.error("Error al crear slots:", error);
  }
};

// Llamar función
createAvailability(1);
```

---

## Notas importantes

1. **Fecha**: Formato `YYYY-MM-DD` (ISO 8601)
2. **Hora**: Formato `HH:MM` (24 horas)
3. **id_doctor**: Debe existir en la tabla `doctores` y estar activo
4. **id_clinica**: Clínica donde el doctor dará consulta ese día
5. **Múltiples slots**: Un mismo doctor puede tener múltiples franjas en el mismo día
6. **Validaciones**:
   - La hora de fin debe ser mayor que la de inicio
   - El doctor debe estar activo
   - El id_doctor en URL debe coincidir con el del JSON

---

## Posibles errores

### 404 - Doctor no encontrado
```json
{"detail": "Doctor con ID 999 no encontrado"}
```

### 400 - Doctor inactivo
```json
{"detail": "El doctor Juan García no está activo"}
```

### 400 - Horario inválido
```json
{"detail": "Hora fin debe ser mayor que hora inicio en 2026-09-21: 09:00 - 07:00"}
```

### 400 - ID mismatch
```json
{"detail": "El id_doctor en la URL debe coincidir con el del cuerpo de la solicitud"}
```

---

## Modificar un slot existente (si está DISPONIBLE)

```http
PUT /api/doctors/1/availability/7
Content-Type: application/json
```

```json
{
  "fecha": "2026-09-21",
  "hora_inicio": "14:30",
  "hora_fin": "15:30",
  "id_clinica": 1
}
```

Respuesta:

```json
{
  "id_slot": 7,
  "id_doctor": 1,
  "id_clinica": 1,
  "fecha_hora_inicio": "2026-09-21T14:30:00",
  "fecha_hora_fin": "2026-09-21T15:30:00",
  "estado": "DISPONIBLE"
}
```

---

## Eliminar (cancelar) un slot disponible

```http
DELETE /api/doctors/1/availability/7
```

Respuesta:

```http
204 No Content
```

# Medical Appointments API

API para crear, reservar, cambiar y consultar citas médicas. Desarrollado con FastAPI para ser consultado desde Dialogflow.

## 🚀 Características

- ✅ Crear citas médicas
- ✅ Reservar citas
- ✅ Cambiar/Actualizar citas
- ✅ Consultar citas por paciente
- ✅ Cancelar citas
- ✅ Confirmar citas
- ✅ CORS habilitado para Dialogflow

## 📁 Estructura del Proyecto

```
app/
├── api/              # Endpoints REST
├── models/           # Modelos SQLAlchemy
├── schemas/          # Esquemas Pydantic
├── services/         # Lógica de negocio
├── database/         # Configuración de BD
├── config/           # Configuración general
└── utils/            # Funciones auxiliares
```

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
cd FastAPIProjectCitasMedicas
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```

## 🚀 Ejecutar la API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

## 📚 Endpoints

### Crear Cita
```http
POST /api/appointments/
Content-Type: application/json

{
  "patient_name": "Juan Pérez",
  "patient_phone": "3101234567",
  "patient_email": "juan@example.com",
  "doctor_name": "Dr. Carlos López",
  "specialty": "Cardiología",
  "appointment_date": "2024-01-15T14:30:00",
  "notes": "Revisión de presión arterial"
}
```

### Consultar Cita
```http
GET /api/appointments/{id}
```

### Consultar Citas del Paciente
```http
GET /api/appointments/patient/{patient_name}
```

### Actualizar Cita
```http
PUT /api/appointments/{id}
Content-Type: application/json

{
  "appointment_date": "2024-01-16T14:30:00",
  "notes": "Cambio de horario"
}
```

### Confirmar Cita
```http
PATCH /api/appointments/{id}/confirm
```

### Cancelar Cita
```http
PATCH /api/appointments/{id}/cancel
```

### Eliminar Cita
```http
DELETE /api/appointments/{id}
```

## 🔗 Integración con Dialogflow

La API está habilitada con CORS para aceptar solicitudes desde Dialogflow. Para hacer llamadas desde Dialogflow:

1. Usar la URL: `http://tu-servidor:8000/api/appointments/`
2. Configurar los parámetros según los esquemas
3. Mapear las respuestas JSON en el webhook

## 📝 Ejemplo de Integración Dialogflow

```javascript
// En un webhook de Dialogflow
const response = await fetch('http://tu-servidor:8000/api/appointments/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    patient_name: agent.parameters.patientName,
    patient_phone: agent.parameters.patientPhone,
    doctor_name: agent.parameters.doctorName,
    specialty: agent.parameters.specialty,
    appointment_date: agent.parameters.appointmentDate,
    notes: agent.parameters.notes
  })
});
```

## 🗄️ Base de Datos

Por defecto usa SQLite (`medical_appointments.db`). Para cambiar a PostgreSQL o MySQL, editar `app/config/settings.py` y `DATABASE_URL`.

## 📄 Licencia

MIT

## 👨‍💻 Autor

César Ruiz

---

**¡La API está lista para usar!** 

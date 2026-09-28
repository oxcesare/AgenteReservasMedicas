# Medical Appointments API

API REST para gestionar la disponibilidad de doctores y el ciclo de vida completo de citas médicas (crear, reservar, modificar, cancelar y consultar). Construida con **FastAPI + SQLAlchemy** sobre **MySQL**, pensada para ser consumida por un bot conversacional (Dialogflow / WhatsApp) o cualquier frontend (HTML/CSS/JS).

## 🚀 Características

- ✅ El doctor da de alta su disponibilidad (múltiples días y franjas horarias en una sola petición)
- ✅ El doctor puede modificar o eliminar un slot de disponibilidad (si aún no está reservado)
- ✅ Consulta de disponibilidad por doctor, con rango de fechas y paginación
- ✅ Los slots `RESERVADO` devuelven el detalle completo de la cita y del paciente
- ✅ El paciente agenda una cita seleccionando un `id_slot` disponible
- ✅ Modificación de una cita: cambio de horario (`id_slot`), notas y/o estado (`estado_actual`)
- ✅ Cancelación de una cita (libera el slot automáticamente)
- ✅ Historial de cambios de estado de cada cita (`historial_citas`)
- ✅ CORS habilitado para integraciones externas (Dialogflow, frontend, etc.)
- ✅ Configuración de base de datos vía variables de entorno (`.env`, no se sube al repositorio)

## 📁 Estructura del Proyecto

```
app/
├── api/                    # Endpoints REST (routers de FastAPI)
│   ├── appointments.py     # Endpoints demo iniciales (tabla appointments, SQLite)
│   ├── availability.py     # Disponibilidad de doctores (slots)
│   └── citas.py            # Agendar / modificar / cancelar citas
├── models/                 # Modelos SQLAlchemy (mapeo 1:1 con las tablas de MySQL)
│   ├── doctor.py, clinica.py, paciente.py
│   ├── doctor_clinica.py, regla_disponibilidad.py, excepcion_disponibilidad.py
│   ├── slot_disponibilidad.py, cita.py, historial_cita.py
├── schemas/                # Esquemas Pydantic (validación y forma de request/response)
├── services/                # Lógica de negocio (reglas, validaciones, transacciones)
├── database/                # Configuración de conexión SQLAlchemy
├── config/                  # Configuración general (settings, variables de entorno)
└── utils/                   # Funciones auxiliares
```

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repo>
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
Edita `.env` con tus credenciales reales de MySQL:
```env
DEBUG=True

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=reserva_citas_db
DB_USER=root
DB_PASS=tu_password
```
> ⚠️ `.env` está en `.gitignore` y **nunca** debe subirse al repositorio. Las credenciales se cargan con `python-dotenv` + `pydantic-settings` (ver `app/config/settings.py`).

5. **Crear la base de datos**
Ejecuta el script SQL de creación de tablas (`clinicas`, `doctores`, `pacientes`, `slots_disponibilidad`, `citas`, `historial_citas`, etc.) contra tu instancia MySQL (`reserva_citas_db`).

## 🚀 Ejecutar la API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Ejecuta el comando desde la **raíz del proyecto** (donde está `main.py`). Si tu terminal quedó ubicada en otra subcarpeta, `uvicorn` no podrá importar el módulo `main`.

La API estará disponible en: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

---

## 📚 Servicios expuestos por el API

### 1. Disponibilidad de doctores — `app/api/availability.py`

Base: `/api/doctors/{id_doctor}/availability`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/doctors/{id_doctor}/availability` | Consulta **todos los slots** del doctor en un rango de fechas (con su estado y, si aplica, la cita asociada) |
| `POST` | `/api/doctors/{id_doctor}/availability` | El doctor **crea** disponibilidad: uno o varios días, cada uno con una o varias franjas horarias |
| `PUT`  | `/api/doctors/{id_doctor}/availability/{id_slot}` | El doctor **modifica** un slot puntual (fecha/hora), solo si está `DISPONIBLE` |
| `DELETE` | `/api/doctors/{id_doctor}/availability/{id_slot}` | El doctor **elimina** un slot, solo si está `DISPONIBLE` |

#### `GET` — Consultar disponibilidad

Query params opcionales: `desde`, `hasta` (datetime ISO), `pagina` (default `1`), `tamano_pagina` (default `50`, máx `200`).

```http
GET /api/doctors/1/availability?desde=2026-09-22T00:00:00&hasta=2026-09-22T23:59:59&pagina=1&tamano_pagina=50
```

Respuesta:
```json
{
  "id_doctor": 1,
  "desde": "2026-09-22T00:00:00",
  "hasta": "2026-09-22T23:59:59",
  "pagina": 1,
  "tamano_pagina": 50,
  "total_slots": 3,
  "slots": [
    {
      "id_slot": 121,
      "id_clinica": 1,
      "fecha_hora_inicio": "2026-09-22T07:00:00",
      "fecha_hora_fin": "2026-09-22T09:00:00",
      "estado": "RESERVADO",
      "cita": {
        "id_cita": 5,
        "estado_actual": "PROGRAMADA",
        "notas_paciente": "Primera consulta",
        "paciente": {
          "id_paciente": 10,
          "nombre": "César",
          "apellido": "Ricardo",
          "telefono_whatsapp": "3101234567",
          "email": "juan.perez@mail.com"
        }
      }
    },
    {
      "id_slot": 122,
      "id_clinica": 1,
      "fecha_hora_inicio": "2026-09-22T09:30:00",
      "fecha_hora_fin": "2026-09-22T11:30:00",
      "estado": "DISPONIBLE",
      "cita": null
    }
  ]
}
```
> Regla: si el slot está `DISPONIBLE` o `BLOQUEADO`, `cita` es `null`. Si está `RESERVADO`, `cita` viene completa.

#### `POST` — Crear disponibilidad (uno o varios días)

```http
POST /api/doctors/1/availability
Content-Type: application/json
```
```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "slots": [
    {
      "fecha": "2026-09-21",
      "franjas": [
        { "hora_inicio": "07:00", "hora_fin": "09:00" },
        { "hora_inicio": "09:30", "hora_fin": "11:30" },
        { "hora_inicio": "17:30", "hora_fin": "19:30" }
      ]
    },
    {
      "fecha": "2026-09-22",
      "franjas": [
        { "hora_inicio": "07:00", "hora_fin": "09:00" }
      ]
    }
  ]
}
```
Respuesta (`201 Created`):
```json
{
  "id_doctor": 1,
  "id_clinica": 1,
  "total_slots_creados": 4,
  "detalles": [
    { "fecha": "2026-09-21", "hora_inicio": "07:00", "hora_fin": "09:00", "clinica_id": 1 }
  ]
}
```
Validaciones: el doctor debe existir y estar activo; `hora_fin` > `hora_inicio`.
Ver más ejemplos en [`EJEMPLOS_DISPONIBILIDAD.md`](./EJEMPLOS_DISPONIBILIDAD.md).

#### `PUT` — Modificar un slot existente

Solo permitido si el slot está `DISPONIBLE` (no se puede mover uno ya reservado).

```http
PUT /api/doctors/1/availability/121
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
  "id_slot": 121,
  "id_doctor": 1,
  "id_clinica": 1,
  "fecha_hora_inicio": "2026-09-21T14:30:00",
  "fecha_hora_fin": "2026-09-21T15:30:00",
  "estado": "DISPONIBLE"
}
```
Validaciones: `hora_fin` > `hora_inicio`; no debe cruzarse con otro slot del mismo doctor.

#### `DELETE` — Eliminar un slot disponible

```http
DELETE /api/doctors/1/availability/121
```
Respuesta: `204 No Content`. Solo permitido si el slot está `DISPONIBLE`.

---

### 2. Citas — `app/api/citas.py`

Base: `/api/citas`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST`   | `/api/citas` | El paciente **agenda** una cita sobre un slot `DISPONIBLE` |
| `PUT`    | `/api/citas/{id_cita}` | **Modifica** la cita: cambia de slot/horario, notas y/o estado |
| `DELETE` | `/api/citas/{id_cita}` | **Cancela** la cita y libera el slot |

#### `POST` — Agendar una cita

El `id_slot` debe existir y estar en estado `DISPONIBLE` (se obtiene previamente vía `GET /api/doctors/{id_doctor}/availability`). Si el paciente no existe (por `telefono_whatsapp`) se crea automáticamente; si ya existe, se actualizan sus datos.

```http
POST /api/citas
Content-Type: application/json
```
```json
{
  "id_slot": 121,
  "paciente": {
    "nombre": "César",
    "apellido": "Ricardo",
    "telefono_whatsapp": "3101234567",
    "email": "juan.perez@mail.com"
  },
  "notas_paciente": "Primera consulta"
}
```
Respuesta (`201 Created`):
```json
{
  "id_cita": 5,
  "estado_actual": "PROGRAMADA",
  "notas_paciente": "Primera consulta",
  "creado_en": "2026-09-21T02:47:28",
  "paciente": {
    "id_paciente": 10,
    "nombre": "César",
    "apellido": "Ricardo",
    "telefono_whatsapp": "3101234567",
    "email": "juan.perez@mail.com"
  },
  "slot": {
    "id_slot": 121,
    "id_doctor": 1,
    "id_clinica": 1,
    "fecha_hora_inicio": "2026-09-21T07:00:00",
    "fecha_hora_fin": "2026-09-21T09:00:00"
  }
}
```
Efecto en BD: se crea el registro en `citas`, el slot pasa a `RESERVADO` y se agrega una entrada en `historial_citas`.

#### `PUT` — Modificar una cita (horario, notas y/o estado)

```http
PUT /api/citas/5
Content-Type: application/json
```
```json
{
  "id_slot": 122,
  "notas_paciente": "Cambio de horario solicitado por el paciente",
  "estado_actual": "CONFIRMADA"
}
```
Todos los campos son opcionales (se envían solo los que se quieren cambiar):
- `id_slot`: mueve la cita a otro slot, siempre que el nuevo esté `DISPONIBLE`. El slot anterior vuelve a `DISPONIBLE`.
- `notas_paciente`: actualiza el comentario del paciente.
- `estado_actual`: uno de `PROGRAMADA`, `CONFIRMADA`, `COMPLETADA`, `CANCELADA`, `NO_ASISTIO`. Si se pasa a `CANCELADA` o `NO_ASISTIO`, el slot se libera automáticamente.

No se puede modificar una cita que ya esté `CANCELADA`. Cada cambio queda registrado en `historial_citas`.

#### `DELETE` — Cancelar una cita

```http
DELETE /api/citas/5
```
Respuesta: `204 No Content`. Marca la cita como `CANCELADA`, libera el slot (vuelve a `DISPONIBLE`) y registra el cambio en el historial.

---

### 3. Endpoints demo iniciales — `app/api/appointments.py`

Conjunto de endpoints CRUD sobre una tabla simple `appointments` (usada en las primeras pruebas del proyecto, independiente del esquema `citas`/`slots_disponibilidad`). Se mantiene como referencia/demo:

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/appointments/` | Crear cita (modelo simplificado) |
| `GET` | `/api/appointments/{id}` | Consultar por ID |
| `GET` | `/api/appointments/` | Listar con paginación (`skip`, `limit`) |
| `GET` | `/api/appointments/patient/{patient_name}` | Buscar por nombre de paciente |
| `PUT` | `/api/appointments/{id}` | Actualizar |
| `PATCH` | `/api/appointments/{id}/confirm` | Confirmar |
| `PATCH` | `/api/appointments/{id}/cancel` | Cancelar |
| `DELETE` | `/api/appointments/{id}` | Eliminar |

---

## 🔗 Integración con Dialogflow / WhatsApp

La API tiene CORS habilitado para aceptar solicitudes desde cualquier origen. Flujo típico de un bot conversacional:

1. El bot pregunta la fecha deseada.
2. Llama a `GET /api/doctors/{id_doctor}/availability?desde=...&hasta=...` y muestra los slots `DISPONIBLE` (p. ej. de 3 en 3 usando `pagina`/`tamano_pagina`).
3. Cuando el usuario elige un horario, llama a `POST /api/citas` con el `id_slot` seleccionado y los datos del paciente.
4. Si el usuario quiere reagendar o cancelar, usa `PUT`/`DELETE /api/citas/{id_cita}`.

```javascript
// Ejemplo desde un webhook
const response = await fetch('http://tu-servidor:8000/api/citas', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id_slot: idSlotSeleccionado,
    paciente: {
      nombre: agent.parameters.nombre,
      apellido: agent.parameters.apellido,
      telefono_whatsapp: agent.parameters.telefono,
      email: agent.parameters.email
    },
    notas_paciente: agent.parameters.notas
  })
});
```

## 🗄️ Base de Datos

MySQL (`reserva_citas_db`). La conexión se arma en `app/config/settings.py` a partir de `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` (o `DATABASE_URL` completo si se prefiere), definidos en `.env`. El driver usado es `PyMySQL`.

Tablas principales: `clinicas`, `doctores`, `pacientes`, `doctor_clinica`, `reglas_disponibilidad`, `excepciones_disponibilidad`, `slots_disponibilidad`, `citas`, `historial_citas`.

## 🚧 En desarrollo

- `app/agent/` y `app/api/agent/`: base para un agente conversacional (LangGraph) y webhook de WhatsApp. Aún no está integrado en `main.py`.

## 📄 Licencia

MIT

## 👨‍💻 Autor

César Ruiz

---

**¡La API está lista para usar!**

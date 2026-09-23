"""
Nodos del agente
"""
import requests
import dateparser
from datetime import datetime, time
from langgraph.types import interrupt

from .state import CitaState

BASE_URL = "http://localhost:8000"
DOCTOR_ID = 1


def parsear_fecha(texto: str) -> datetime | None:
    return dateparser.parse(
        texto,
        languages=["es"],
        settings={"PREFER_DATES_FROM": "future"}
    )


def detectar_periodo(texto: str) -> str | None:
    texto = texto.lower()
    if "mañana" in texto:
        return "manana"
    if "tarde" in texto:
        return "tarde"
    if "noche" in texto:
        return "noche"
    return None


def _en_periodo(fecha_hora_iso: str, periodo: str) -> bool:
    hora = datetime.fromisoformat(fecha_hora_iso).hour
    if periodo == "manana":
        return hora < 12
    if periodo == "tarde":
        return 12 <= hora < 19
    if periodo == "noche":
        return hora >= 19
    return True


def saludar(state: CitaState) -> dict:
    respuesta = interrupt("Buena tarde ¿Quieres reservar una cita?")
    return {"intencion_confirmada": respuesta.strip().lower() in ["si", "sí"]}


def pedir_fecha(state: CitaState) -> dict:
    fecha = interrupt("Me podrías dar la fecha para la cual deseas tu cita")
    return {"fecha_solicitada": fecha}


def consultar_disponibilidad(state: CitaState) -> dict:
    fecha = parsear_fecha(state["fecha_solicitada"])

    if fecha is None:
        return {"horarios_disponibles": [], "slots_disponibles": []}

    desde = datetime.combine(fecha.date(), time.min).isoformat()
    hasta = datetime.combine(fecha.date(), time.max.replace(microsecond=0)).isoformat()

    resp = requests.get(
        f"{BASE_URL}/api/doctors/{DOCTOR_ID}/availability",
        params={"desde": desde, "hasta": hasta}
    )
    resp.raise_for_status()
    data = resp.json()

    disponibles = [s for s in data["slots"] if s["estado"] == "DISPONIBLE"]

    periodo = detectar_periodo(state["fecha_solicitada"])
    if periodo:
        disponibles = [s for s in disponibles if _en_periodo(s["fecha_hora_inicio"], periodo)]

    slots_formateados = []
    horarios_legibles = []
    for s in disponibles:
        inicio = datetime.fromisoformat(s["fecha_hora_inicio"])
        fin = datetime.fromisoformat(s["fecha_hora_fin"])
        texto = f"{inicio.strftime('%I:%M %p')} a {fin.strftime('%I:%M %p')}"
        horarios_legibles.append(texto)
        slots_formateados.append({"id_slot": s["id_slot"], "texto": texto})

    return {
        "horarios_disponibles": horarios_legibles,
        "slots_disponibles": slots_formateados
    }


def pedir_horario(state: CitaState) -> dict:
    slots = state["slots_disponibles"]
    intentos = state.get("intentos_horario", 0)

    if not slots:
        return {"slot_elegido_id": None, "horario_elegido": None, "intentos_horario": intentos}

    lista = "\n".join(f"{i + 1}. {s['texto']}" for i, s in enumerate(slots))

    if intentos == 0:
        pregunta = f"Tengo estos horarios\n\n{lista}\n\nResponde con el número del horario que deseas reservar"
    else:
        pregunta = f"No entendí tu respuesta. Elige un número válido:\n\n{lista}"

    respuesta = interrupt(pregunta)
    respuesta_limpia = respuesta.strip()

    slot_match = None
    if respuesta_limpia.isdigit():
        indice = int(respuesta_limpia) - 1
        if 0 <= indice < len(slots):
            slot_match = slots[indice]

    if slot_match:
        return {
            "horario_elegido": slot_match["texto"],
            "slot_elegido_id": slot_match["id_slot"],
            "intentos_horario": intentos + 1
        }
    else:
        return {
            "horario_elegido": None,
            "slot_elegido_id": None,
            "intentos_horario": intentos + 1
        }


def confirmar_cita(state: CitaState) -> dict:
    print(f"Agente: Cita confirmada ({state['horario_elegido']}). Hasta pronto")
    return {}

PACIENTE_DUMMY = {
    "nombre": "César",
    "apellido": "Ricardo",
    "telefono_whatsapp": "3101234567",
    "email": "juan.perez@mail.com"
}


def reservar_cita(state: CitaState) -> dict:
    payload = {
        "id_slot": state["slot_elegido_id"],
        "paciente": PACIENTE_DUMMY,
        "notas_paciente": "Primera consulta"
    }

    try:
        resp = requests.post(f"{BASE_URL}/api/citas", json=payload)
        resp.raise_for_status()
        return {"reserva_exitosa": True, "error_reserva": None}
    except requests.exceptions.RequestException as e:
        return {"reserva_exitosa": False, "error_reserva": str(e)}


def confirmar_cita(state: CitaState) -> dict:
    if state.get("reserva_exitosa"):
        print(f"Agente: Cita confirmada ({state['horario_elegido']}). Hasta pronto")
    else:
        print(f"Agente: No pude confirmar tu cita. Motivo: {state.get('error_reserva')}")
    return {}
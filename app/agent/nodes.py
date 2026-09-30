"""
Nodos del agente
"""
import requests
import dateparser
from datetime import datetime, time
from langgraph.types import interrupt

from .state import CitaState
from ..config import settings

BASE_URL = settings.BASE_URL

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
    if state.get("fecha_entendida") is False:
        pregunta = (
            "No pude entender la fecha que me indicaste. ¿Podrías escribirla de otra forma? "
            "Por ejemplo: 'miércoles 23 de septiembre' o '23/09/2026'. "
            "O responde 'no' si prefieres terminar"
        )
    elif state.get("slots_disponibles") == []:
        pregunta = (
            "Lo siento, no encontré horarios disponibles para esa fecha. "
            "¿Te gustaría consultar otra? Escríbeme la nueva fecha, "
            "o responde 'no' si prefieres terminar"
        )
    else:
        pregunta = "Me podrías dar la fecha para la cual deseas tu cita"

    fecha = interrupt(pregunta)

    if fecha.strip().lower() in ("no", "cancelar", "salir"):
        print("Agente: Entendido, hasta pronto")
        return {"fecha_solicitada": None}
    return {"fecha_solicitada": fecha}


def consultar_disponibilidad(state: CitaState) -> dict:
    fecha = parsear_fecha(state["fecha_solicitada"])

    if fecha is None:
        return {"horarios_disponibles": [], "slots_disponibles": [], "fecha_entendida": False}

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
        "slots_disponibles": slots_formateados,
        "fecha_entendida": True
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


# ---------------------------------------------------------------------------
# Menú, consulta de citas y reagendado
# ---------------------------------------------------------------------------
OPCIONES_MENU = {"1": "reservar", "2": "consultar", "3": "reagendar", "4": "cancelar"}


def menu_principal(state: CitaState) -> dict:
    respuesta = interrupt(
        "Buena tarde ¿Qué deseas hacer?\n\n"
        "1. Reservar una cita\n"
        "2. Consultar mis citas\n"
        "3. Reagendar una cita\n"
        "4. Cancelar una cita\n\n"
        "Responde con el número de la opción"
    )
    opcion = OPCIONES_MENU.get(respuesta.strip())
    if opcion is None:
        print("Agente: No entendí tu opción. Hasta pronto")
    return {"opcion": opcion}


def consultar_mis_citas(state: CitaState) -> dict:
    telefono = PACIENTE_DUMMY["telefono_whatsapp"]

    resp = requests.get(f"{BASE_URL}/api/citas/paciente/{telefono}")
    resp.raise_for_status()

    citas = []
    for c in resp.json():
        inicio = datetime.fromisoformat(c["slot"]["fecha_hora_inicio"])
        fin = datetime.fromisoformat(c["slot"]["fecha_hora_fin"])
        texto = f"{inicio.strftime('%d/%m/%Y')} de {inicio.strftime('%I:%M %p')} a {fin.strftime('%I:%M %p')}"
        citas.append({"id_cita": c["id_cita"], "texto": texto})

    return {"citas_paciente": citas}


def mostrar_citas(state: CitaState) -> dict:
    citas = state.get("citas_paciente")
    if not citas:
        print("Agente: No tienes citas programadas")
    else:
        lista = "\n".join(f"- {c['texto']}" for c in citas)
        print(f"Agente: Estas son tus citas programadas\n\n{lista}")
    return {}


def pedir_cita(state: CitaState) -> dict:
    citas = state["citas_paciente"]
    intentos = state.get("intentos_cita", 0)
    accion = "cancelar" if state.get("opcion") == "cancelar" else "reagendar"

    lista = "\n".join(f"{i + 1}. {c['texto']}" for i, c in enumerate(citas))

    if intentos == 0:
        pregunta = f"Estas son tus citas programadas\n\n{lista}\n\nResponde con el número de la cita que deseas {accion}"
    else:
        pregunta = f"No entendí tu respuesta. Elige un número válido:\n\n{lista}"

    respuesta = interrupt(pregunta)
    respuesta_limpia = respuesta.strip()

    cita_match = None
    if respuesta_limpia.isdigit():
        indice = int(respuesta_limpia) - 1
        if 0 <= indice < len(citas):
            cita_match = citas[indice]

    return {
        "cita_elegida_id": cita_match["id_cita"] if cita_match else None,
        "intentos_cita": intentos + 1
    }


def reagendar_cita(state: CitaState) -> dict:
    payload = {"id_slot": state["slot_elegido_id"]}

    try:
        resp = requests.put(f"{BASE_URL}/api/citas/{state['cita_elegida_id']}", json=payload)
        resp.raise_for_status()
        print(f"Agente: Cita reagendada ({state['horario_elegido']}). Hasta pronto")
    except requests.exceptions.RequestException as e:
        print(f"Agente: No pude reagendar tu cita. Motivo: {e}")
    return {}


def confirmar_cancelacion(state: CitaState) -> dict:
    cita = next(
        c for c in state["citas_paciente"] if c["id_cita"] == state["cita_elegida_id"]
    )
    respuesta = interrupt(
        f"¿Seguro que deseas cancelar la cita del {cita['texto']}? (sí/no)"
    )
    confirmado = respuesta.strip().lower() in ("si", "sí")

    if not confirmado:
        print("Agente: De acuerdo, tu cita no fue cancelada. Hasta pronto")

    return {"confirmacion_cancelar": confirmado}


def cancelar_cita(state: CitaState) -> dict:
    try:
        resp = requests.delete(f"{BASE_URL}/api/citas/{state['cita_elegida_id']}")
        resp.raise_for_status()
        print("Agente: Tu cita ha sido cancelada. Hasta pronto")
    except requests.exceptions.RequestException as e:
        print(f"Agente: No pude cancelar tu cita. Motivo: {e}")
    return {}
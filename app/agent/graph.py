""""
Para incorporar los nodos del agente
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import CitaState
from .nodes import (
    menu_principal, consultar_mis_citas, mostrar_citas, pedir_cita,
    pedir_fecha, consultar_disponibilidad, pedir_horario,
    reservar_cita, reagendar_cita, confirmar_cita
)

MAX_INTENTOS = 3


def route_despues_horario(state: CitaState) -> str:
    if state.get("slot_elegido_id") is not None:
        return "reagendar_cita" if state.get("opcion") == "reagendar" else "reservar_cita"
    if not state.get("slots_disponibles"):
        return "pedir_fecha"  # no había disponibilidad: ofrece consultar otra fecha
    if state.get("intentos_horario", 0) >= MAX_INTENTOS:
        return END  # se acabaron los intentos
    return "pedir_horario"  # ciclo: vuelve a preguntar


def route_despues_menu(state: CitaState) -> str:
    opcion = state.get("opcion")
    if opcion == "reservar":
        return "pedir_fecha"
    if opcion in ("consultar", "reagendar"):
        return "consultar_mis_citas"
    return END  # opción inválida


def route_despues_consulta(state: CitaState) -> str:
    if state.get("opcion") == "reagendar" and state.get("citas_paciente"):
        return "pedir_cita"
    return "mostrar_citas"  # consultar, o reagendar sin citas


def route_despues_cita(state: CitaState) -> str:
    if state.get("cita_elegida_id") is not None:
        return "pedir_fecha"
    if state.get("intentos_cita", 0) >= MAX_INTENTOS:
        return END  # se acabaron los intentos
    return "pedir_cita"  # ciclo: vuelve a preguntar


def route_despues_fecha(state: CitaState) -> str:
    if state.get("fecha_solicitada") is None:
        return END  # el usuario decidió no consultar otra fecha
    return "consultar_disponibilidad"


def construir_grafo():
    flujo = StateGraph(CitaState)
    flujo.add_node("menu_principal", menu_principal)
    flujo.add_node("consultar_mis_citas", consultar_mis_citas)
    flujo.add_node("mostrar_citas", mostrar_citas)
    flujo.add_node("pedir_cita", pedir_cita)
    flujo.add_node("pedir_fecha", pedir_fecha)
    flujo.add_node("consultar_disponibilidad", consultar_disponibilidad)
    flujo.add_node("pedir_horario", pedir_horario)
    flujo.add_node("reservar_cita", reservar_cita)
    flujo.add_node("reagendar_cita", reagendar_cita)
    flujo.add_node("confirmar_cita", confirmar_cita)

    flujo.set_entry_point("menu_principal")
    flujo.add_conditional_edges("menu_principal", route_despues_menu)
    flujo.add_conditional_edges("consultar_mis_citas", route_despues_consulta)
    flujo.add_conditional_edges("pedir_cita", route_despues_cita)
    flujo.add_conditional_edges("pedir_fecha", route_despues_fecha)
    flujo.add_edge("consultar_disponibilidad", "pedir_horario")
    flujo.add_conditional_edges("pedir_horario", route_despues_horario)
    flujo.add_edge("reservar_cita", "confirmar_cita")
    flujo.add_edge("confirmar_cita", END)
    flujo.add_edge("mostrar_citas", END)
    flujo.add_edge("reagendar_cita", END)

    return flujo.compile(checkpointer=InMemorySaver())
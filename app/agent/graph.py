""""
Para incorporar los nodos del agente
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import CitaState
from .nodes import (
    saludar, pedir_fecha, consultar_disponibilidad,
    pedir_horario, reservar_cita, confirmar_cita
)

MAX_INTENTOS = 3


def route_despues_horario(state: CitaState) -> str:
    if state.get("slot_elegido_id") is not None:
        return "reservar_cita"
    if not state.get("slots_disponibles"):
        return END  # no había disponibilidad, no tiene caso reintentar
    if state.get("intentos_horario", 0) >= MAX_INTENTOS:
        return END  # se acabaron los intentos
    return "pedir_horario"  # ciclo: vuelve a preguntar


def construir_grafo():
    flujo = StateGraph(CitaState)
    flujo.add_node("saludar", saludar)
    flujo.add_node("pedir_fecha", pedir_fecha)
    flujo.add_node("consultar_disponibilidad", consultar_disponibilidad)
    flujo.add_node("pedir_horario", pedir_horario)
    flujo.add_node("reservar_cita", reservar_cita)
    flujo.add_node("confirmar_cita", confirmar_cita)

    flujo.set_entry_point("saludar")
    flujo.add_conditional_edges(
        "saludar",
        lambda s: "pedir_fecha" if s["intencion_confirmada"] else END
    )
    flujo.add_edge("pedir_fecha", "consultar_disponibilidad")
    flujo.add_edge("consultar_disponibilidad", "pedir_horario")
    flujo.add_conditional_edges("pedir_horario", route_despues_horario)
    flujo.add_edge("reservar_cita", "confirmar_cita")
    flujo.add_edge("confirmar_cita", END)

    return flujo.compile(checkpointer=InMemorySaver())
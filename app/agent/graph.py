from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import CitaState
from .nodes import saludar, pedir_fecha, consultar_disponibilidad, pedir_horario, confirmar_cita

def construir_grafo():
    flujo = StateGraph(CitaState)
    flujo.add_node("saludar", saludar)
    flujo.add_node("pedir_fecha", pedir_fecha)
    flujo.add_node("consultar_disponibilidad", consultar_disponibilidad)
    flujo.add_node("pedir_horario", pedir_horario)
    flujo.add_node("confirmar_cita", confirmar_cita)

    flujo.set_entry_point("saludar")
    flujo.add_conditional_edges(
        "saludar",
        lambda s: "pedir_fecha" if s["intencion_confirmada"] else END
    )
    flujo.add_edge("pedir_fecha", "consultar_disponibilidad")
    flujo.add_edge("consultar_disponibilidad", "pedir_horario")
    flujo.add_edge("pedir_horario", "confirmar_cita")
    flujo.add_edge("confirmar_cita", END)

    return flujo.compile(checkpointer=InMemorySaver())
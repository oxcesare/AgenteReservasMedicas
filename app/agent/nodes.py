"""
Nodos del agente
"""
from langgraph.types import interrupt
from .state import CitaState

def saludar(state: CitaState) -> dict:
    respuesta = interrupt("Buena tarde ¿Quieres reservar una cita?")
    return {"intencion_confirmada": respuesta.strip().lower() in ["si", "sí"]}

def pedir_fecha(state: CitaState) -> dict:
    fecha = interrupt("Me podrías dar la fecha para la cual deseas tu cita")
    return {"fecha_solicitada": fecha}

def consultar_disponibilidad(state: CitaState) -> dict:
    # Aquí luego conectas tu repository.py real; por ahora mock
    return {"horarios_disponibles": ["9am a 10am", "10am a 11am", "11am a 12pm"]}

def pedir_horario(state: CitaState) -> dict:
    lista = "\n".join(state["horarios_disponibles"])
    horario = interrupt(f"Tengo estos horarios\n\n{lista}\n\n¿Qué horario deseas reservar?")
    return {"horario_elegido": horario}

def confirmar_cita(state: CitaState) -> dict:
    print(f"Agente: Cita confirmada ({state['horario_elegido']}). Hasta pronto")
    return {}

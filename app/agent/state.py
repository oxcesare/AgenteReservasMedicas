"""
Estado compartido del grafo del agente de citas
"""
from typing import TypedDict, Optional


class CitaState(TypedDict, total=False):
    # Menú principal
    opcion: Optional[str]  # "reservar" | "consultar" | "reagendar"

    # Saludo / intención (si lo llegas a usar)
    intencion_confirmada: bool

    # Fecha y disponibilidad
    fecha_solicitada: Optional[str]
    fecha_entendida: bool
    horarios_disponibles: list[str]
    slots_disponibles: list[dict]

    # Selección de horario
    horario_elegido: Optional[str]
    slot_elegido_id: Optional[int]
    intentos_horario: int

    # Reserva
    reserva_exitosa: bool
    error_reserva: Optional[str]

    # Consulta / reagendado de citas existentes
    citas_paciente: list[dict]
    cita_elegida_id: Optional[int]
    intentos_cita: int

    # Cancelación de citas
    confirmacion_cancelar: bool

    # Mensaje final a mandar por WhatsApp cuando el grafo llega a END
    # (lo agregamos para no depender de print() en los nodos finales)
    respuesta_final: Optional[str]
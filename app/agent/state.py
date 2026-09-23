from typing import TypedDict, Optional

class CitaState(TypedDict):
    intencion_confirmada: Optional[bool]
    fecha_solicitada: Optional[str]
    horarios_disponibles: Optional[list[str]]
    slots_disponibles: Optional[list[dict]]
    horario_elegido: Optional[str]
    slot_elegido_id: Optional[int]
    intentos_horario: int
    reserva_exitosa: Optional[bool]
    error_reserva: Optional[str]
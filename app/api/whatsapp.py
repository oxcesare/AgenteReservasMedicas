"""WhatsApp Webhook Router"""
from fastapi import APIRouter, Request, Response
from starlette.concurrency import run_in_threadpool
from langgraph.types import Command

from app.config import settings
from app.agent.graph import construir_grafo
from app.services.agent.whatsapp_service import enviar_mensaje

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

# El grafo se crea UNA sola vez cuando arranca el servidor, no en cada
# request. InMemorySaver guarda el estado de cada conversación en RAM,
# así que si se crea un grafo nuevo por request, se pierde el historial.
grafo = construir_grafo()


@router.get("")
def verify_webhook(request: Request):
    """Meta llama este endpoint UNA vez al configurar el webhook, para validar
    que la URL es tuya. Debe regresar el 'challenge' tal cual si el token coincide."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=403)


def _extraer_mensaje(body: dict) -> tuple[str, str] | None:
    """Extrae (numero_remitente, texto) del payload de Meta.
    Regresa None si el evento no es un mensaje de texto entrante
    (ej. es un evento de status: entregado/leído)."""
    try:
        value = body["entry"][0]["changes"][0]["value"]
        mensajes = value.get("messages")
        if not mensajes:
            return None

        mensaje = mensajes[0]
        if mensaje.get("type") != "text":
            return None  # por ahora solo manejamos texto

        numero = mensaje["from"]
        texto = mensaje["text"]["body"]
        return numero, texto
    except (KeyError, IndexError):
        return None


def _procesar_turno(numero: str, texto: str) -> str:
    """Avanza el grafo un turno para este usuario y regresa el texto
    que se le debe responder."""
    config = {"configurable": {"thread_id": numero}}

    estado_actual = grafo.get_state(config)

    # OJO: no usamos 'estado_actual.values' para detectar si es conversación
    # nueva, porque cuando el grafo está pausado en el PRIMER interrupt()
    # (ej. el menú), el nodo aún no ha retornado nada y 'values' sigue
    # vacío ({}) igual que en un thread que nunca arrancó. Lo correcto es
    # revisar '.next': si hay un nodo pendiente de resumir, la conversación
    # ya está en curso.
    if not estado_actual.next:
        # Conversación nueva: arrancamos el grafo desde cero.
        # El texto que mandó el usuario para "iniciar" (ej. "Hola") se
        # descarta, ya que solo dispara el arranque de la conversación.
        resultado = grafo.invoke({}, config=config)
    else:
        # Conversación en curso: el texto es la respuesta a la última pregunta.
        resultado = grafo.invoke(Command(resume=texto), config=config)

    if "__interrupt__" in resultado:
        return resultado["__interrupt__"][0].value

    # El grafo llegó a END: usamos el mensaje final que dejó el último nodo
    # en el estado (ver campo 'respuesta_final' en state.py / nodes.py),
    # y le agregamos un cierre estándar invitando a continuar.
    texto_final = resultado.get("respuesta_final") or "Listo."
    return f"{texto_final}\n\nEscribe *Hola* si deseas realizar otra acción."


@router.post("")
async def receive_message(request: Request):
    """Recibe mensajes entrantes de WhatsApp, los pasa al grafo de LangGraph,
    y manda la respuesta de vuelta al usuario."""
    body = await request.json()

    extraido = _extraer_mensaje(body)
    if extraido is None:
        return Response(status_code=200)  # evento irrelevante (status, etc.)

    numero, texto = extraido
    print(f"Mensaje de {numero}: {texto}")

    try:
        # IMPORTANTE: _procesar_turno hace llamadas HTTP bloqueantes (requests)
        # de vuelta a este mismo servidor (BASE_URL apunta a localhost:8000).
        # Si se ejecuta directo en el event loop (async def), el servidor se
        # auto-bloquea: se queda esperando una respuesta de sí mismo sin poder
        # atenderla, porque el único hilo del event loop está ocupado esperando.
        # run_in_threadpool mueve esto a un hilo aparte, dejando el event loop
        # libre para seguir atendiendo peticiones (incluida la que nos
        # mandamos a nosotros mismos).
        respuesta = await run_in_threadpool(_procesar_turno, numero, texto)
    except Exception as e:
        print(f"[whatsapp webhook] Error procesando turno de {numero}: {e}")
        respuesta = "Tuvimos un problema procesando tu mensaje, intenta de nuevo."

    await run_in_threadpool(enviar_mensaje, numero, respuesta)

    return Response(status_code=200)
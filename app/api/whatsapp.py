from fastapi import APIRouter, Request, Response
from app.config import settings

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

VERIFY_TOKEN = settings.WHATSAPP_VERIFY_TOKEN  # o pon el string directo por ahora

@router.get("")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=403)

@router.post("")
async def receive_message(request: Request):
    body = await request.json()
    print(body)  # para ver la estructura real del primer mensaje que llegue
    # Aquí después conectamos con tu grafo de LangGraph (carpeta app/agent)
    return Response(status_code=200)
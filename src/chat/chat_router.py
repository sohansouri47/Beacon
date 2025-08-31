from fastapi import APIRouter, Depends, FastAPI, WebSocket, Request
from src.common.config.constants import Routes
from src.chat.chat_service import ChatService
from src.chat.model.chat_model import ConversationRequestModel


class ChatRouter:
    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.router = APIRouter()
        self.register_routes()
        self.include_router()

    def register_routes(self) -> None:
        # HTTP POST /chat
        self.router.post(Routes.SEND_TEXT)(self.chat)

        # WebSocket /voice
        self.router.websocket(Routes.SEND_VOICE)(self.voice)

    def include_router(self) -> None:
        self.app.include_router(self.router)

    async def chat(
        self,
        conversation_request: ConversationRequestModel,
        request: Request,
        chat_service: ChatService = Depends(ChatService),
    ):
        return await chat_service.chat(
            conversation_rquest=conversation_request, headers=request.headers
        )

    async def voice(self, websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"Echo from server: {data}")
        except Exception:
            await websocket.close()

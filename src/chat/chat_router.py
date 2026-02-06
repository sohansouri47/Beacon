from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    WebSocket,
    Request,
    WebSocketDisconnect,
)
from src.common.config.constants import Routes
from src.chat.chat_service import ChatService
from src.chat.model.chat_model import ConversationRequestModel
from src.common.logger.logger import get_logger

logger = get_logger(__name__)


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
        self.router.websocket(Routes.SEND_VOICE)(self.voice_chat)

    def include_router(self) -> None:
        self.app.include_router(self.router)

    async def chat(
        self,
        conversation_request: ConversationRequestModel,
        request: Request,
        chat_service: ChatService = Depends(ChatService),
    ):
        logger.info("Received chat request")
        try:
            response = await chat_service.chat(
                conversation_request=conversation_request, headers=request.headers
            )
            logger.info("Chat request processed successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing chat request: {e}", exc_info=True)
            raise

    async def voice_chat(
        self, websocket: WebSocket, chat_service: ChatService = Depends(ChatService)
    ):
        await websocket.accept()
        logger.info("🎙️ Client connected to /voice WebSocket")

        buffer = bytearray()
        speech_buffer = bytearray()
        silence_counter = 0

        try:
            while True:
                data = await websocket.receive_bytes()
                buffer, speech_buffer, silence_counter = (
                    await chat_service.process_audio(
                        websocket, data, buffer, speech_buffer, silence_counter
                    )
                )
        except WebSocketDisconnect:
            logger.warning("❌ Client disconnected from /voice WebSocket")
            chat_service.is_bot_speaking = False
        except Exception as e:
            logger.error(f"⚠️ Error in /voice WebSocket: {e}", exc_info=True)
            chat_service.is_bot_speaking = False

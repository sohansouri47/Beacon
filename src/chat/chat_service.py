import uuid
import httpx
import asyncio
from a2a.client import A2AClient
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard,
    Message,
    Part,
    Role,
    SendMessageRequest,
    SendMessageResponse,
    MessageSendParams,
    TextPart,
    SendMessageSuccessResponse,
)
import re
import uuid
from src.chat.model.chat_model import ConversationRequestModel
from a2a.types import SendMessageResponse, SendMessageSuccessResponse
from typing import Dict
import json
from fastrtc import get_stt_model, get_tts_model
import webrtcvad
import numpy as np
import librosa
from src.common.config.constants import Constants
from src.common.logger.logger import get_logger
from src.common.config.constants import Constants
from src.common.config.config import AgenticSystemConfig, ConversationConfig
from src.common.auth.auth import OAuth

logger = get_logger(__name__)
STT_MODEL = get_stt_model()
TTS_MODEL = get_tts_model("kokoro")


class ChatService:
    def __init__(self):
        self.stt_model = STT_MODEL
        self.tts_model = TTS_MODEL
        self.vad = webrtcvad.Vad(2)
        self.SAMPLE_RATE = 16000
        self.FRAME_DURATION = 30
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION / 1000)
        self.BYTES_PER_FRAME = self.FRAME_SIZE * 2
        self.is_bot_speaking = False
        self._auth = OAuth()

    async def get_response_from_agent(
        self,
        context_id: str,
        user_prompt: str,
        user_id: str,
    ) -> SendMessageResponse:
        """Send user message to agent and return raw response"""
        token = await self._auth.get_m2m_token(agent_name="orch_agent")
        async with httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"}, timeout=300.0
        ) as httpx_client:
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=AgenticSystemConfig.ORCH_AGENT_URL,
                agent_card_path=AgenticSystemConfig.PUBLIC_AGENT_CARD_PATH,
            )
            agent_card: AgentCard = await resolver.get_agent_card()
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

            message_payload = Message(
                role=Role.user,
                messageId=str(uuid.uuid4()),
                parts=[Part(root=TextPart(text=user_prompt))],
                contextId=context_id,
                metadata={"user_id": user_id},
            )
            request = SendMessageRequest(
                id=str(uuid.uuid4()),
                params=MessageSendParams(message=message_payload),
            )

            logger.info("Sending message to agent")
            response = await client.send_message(request)
            print("chat orch response", response)
            logger.info("Received response from agent")
            return response

    def extract_response_and_context(
        self, response: SendMessageResponse
    ) -> Dict[str, str]:
        """Normalize agent response and extract text + context"""
        if isinstance(response.root, SendMessageSuccessResponse):
            result = response.root.result

            # Handle both response types
            if hasattr(result, "status") and hasattr(result.status, "message"):
                raw_text = result.status.message.parts[0].root.text
                context_id = result.context_id
            else:
                raw_text = result.parts[0].root.text
                context_id = result.context_id

            parsed_text = None

            # Try extracting JSON block if text contains both narration + JSON
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                try:
                    parsed_text = json.loads(match.group())
                except json.JSONDecodeError:
                    pass  # fallback below

            if not parsed_text:
                # fallback: treat raw_text as plain response
                parsed_text = {
                    "response": raw_text.strip(),
                    "next_agent": None,
                }

            return {
                "contextId": context_id,
                "response": parsed_text.get("response"),
                "next_agent": parsed_text.get("next_agent"),
            }

        else:
            return {"error": response.root.error}

    async def chat(
        self, conversation_request: ConversationRequestModel, headers: dict[str, str]
    ):
        """Main chat entry point"""
        print(conversation_request)
        response = await self.get_response_from_agent(
            context_id=conversation_request.context_id,
            user_prompt=conversation_request.user_prompt,
            user_id=conversation_request.user_id,
        )
        return self.extract_response_and_context(response)

    def resample_to_16k(self, audio: np.ndarray, orig_sr: int) -> np.ndarray:
        """Resample float32 audio to 16kHz int16 PCM"""
        resampled = librosa.resample(audio, orig_sr=orig_sr, target_sr=16000)
        return (resampled * 32767).astype(np.int16)

    async def process_audio(
        self,
        websocket,
        data: bytes,
        buffer: bytearray,
        speech_buffer: bytearray,
        silence_counter: int,
    ):
        buffer.extend(data)

        while len(buffer) >= self.BYTES_PER_FRAME:
            frame = buffer[: self.BYTES_PER_FRAME]
            buffer = buffer[self.BYTES_PER_FRAME :]

            if self.is_bot_speaking:
                continue  # ignore mic while bot speaks

            is_speech = self.vad.is_speech(frame, self.SAMPLE_RATE)

            if is_speech:
                speech_buffer.extend(frame)
                silence_counter = 0
            else:
                silence_counter += 1
                if silence_counter > 10 and len(speech_buffer) > 0:
                    # ~300ms silence detected → process utterance
                    audio_array = np.frombuffer(speech_buffer, dtype=np.int16).copy()
                    speech_buffer.clear()

                    # --- Speech-to-Text ---
                    text = self.stt_model.stt((16000, audio_array))
                    if not text.strip():
                        return buffer, speech_buffer, silence_counter

                    # call agent

                    # --- Bot response ---
                    response_text = f"You asked: {text}. Here’s my answer."
                    print("🤖 Bot response:", response_text)
                    response = await self.get_response_from_agent(
                        context_id=ConversationConfig.CONTEXT_ID,
                        user_prompt=text,
                        user_id=ConversationConfig.USER_ID,
                    )
                    response_text = self.extract_response_and_context(response)
                    print(response_text)
                    # --- Text-to-Speech ---
                    sr, audio_out = self.tts_model.tts(response_text["response"])
                    if audio_out.ndim > 1:
                        audio_out = audio_out[:, 0]

                    audio_out_16k = self.resample_to_16k(audio_out, sr)

                    # 🔒 Lock speaking
                    self.is_bot_speaking = True
                    await websocket.send_bytes(audio_out_16k.tobytes())
                    self.is_bot_speaking = False  # 🔓 Unlock

        return buffer, speech_buffer, silence_counter

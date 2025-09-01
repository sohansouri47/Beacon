import uuid
import httpx
import asyncio
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
import uuid
from src.chat.model.chat_model import ConversationRequestModel
from a2a.types import SendMessageResponse, SendMessageSuccessResponse
from typing import Dict
import json
from fastrtc import get_stt_model, get_tts_model
import webrtcvad
import numpy as np
import librosa

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
BASE_URL = "http://localhost:8000"


class ChatService:
    def __init__(self):
        self.stt_model = get_stt_model()
        self.tts_model = get_tts_model("kokoro")
        self.vad = webrtcvad.Vad(2)
        self.SAMPLE_RATE = 16000
        self.FRAME_DURATION = 30
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION / 1000)
        self.BYTES_PER_FRAME = self.FRAME_SIZE * 2
        self.is_bot_speaking = False

    async def chat(
        self, conversation_rquest: ConversationRequestModel, headers: dict[str, str]
    ):
        context_id = conversation_rquest.context_id

        async with httpx.AsyncClient(timeout=300) as httpx_client:
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=BASE_URL,
                agent_card_path=PUBLIC_AGENT_CARD_PATH,
            )
            agent_card: AgentCard = await resolver.get_agent_card()
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
            for text in [conversation_rquest.user_prompt]:
                message_payload = Message(
                    role=Role.user,
                    messageId=str(uuid.uuid4()),
                    parts=[Part(root=TextPart(text=text))],
                    contextId=context_id,
                )
                request = SendMessageRequest(
                    id=str(uuid.uuid4()),
                    params=MessageSendParams(message=message_payload),
                )

                response = await client.send_message(request)

            def extract_response_and_context(
                response: SendMessageResponse,
            ) -> Dict[str, str]:
                if isinstance(response.root, SendMessageSuccessResponse):
                    result = response.root.result

                    # Get the latest agent message
                    if hasattr(result, "status") and hasattr(result.status, "message"):
                        raw_text = result.status.message.parts[0].root.text
                        context_id = result.context_id
                    else:
                        raw_text = result.parts[0].root.text
                        context_id = result.context_id

                    # Parse the JSON string in text
                    try:
                        parsed_text = json.loads(raw_text)
                    except json.JSONDecodeError:
                        parsed_text = {"response": raw_text, "next_agent": None}

                    return {
                        "contextId": context_id,
                        "response": parsed_text.get("response"),
                        "next_agent": parsed_text.get("next_agent"),
                    }
                else:
                    return {"error": response.root.error}

            resp_data = extract_response_and_context(response=response)
            return resp_data

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

                    # --- Text-to-Speech ---
                    sr, audio_out = self.tts_model.tts(response_text)
                    if audio_out.ndim > 1:
                        audio_out = audio_out[:, 0]

                    audio_out_16k = self.resample_to_16k(audio_out, sr)

                    # 🔒 Lock speaking
                    self.is_bot_speaking = True
                    await websocket.send_bytes(audio_out_16k.tobytes())
                    self.is_bot_speaking = False  # 🔓 Unlock

        return buffer, speech_buffer, silence_counter

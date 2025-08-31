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


class ChatService:
    def __init__(self):
        pass

    async def chat(
        self, conversation_rquest: ConversationRequestModel, headers: dict[str, str]
    ):
        context_id = conversation_rquest.context_id
        PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
        BASE_URL = "http://localhost:8000"
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
                    # handle error response
                    return {"error": response.root.error}

            resp_data = extract_response_and_context(response=response)
            return resp_data

from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from src.common.config.prompts import AgentPrompts
from src.common.config.constants import LlmConfig
from google.adk.models.lite_llm import LiteLlm
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from collections.abc import AsyncIterable
import uuid
from src.common.agent_registry.agent_registry import AgentRegistry
from src.common.auth.auth import OAuth
from src.common.agent_registry.agent_connector import AgentConnector
import uuid
from src.common.db.Postgre import ConversationHistoryManager
import json


class OrchestratorAgent:
    def __init__(self):
        self._user_id = "uuid.uuid4()"
        self._agent_registry = AgentRegistry()
        self._agent_auth = OAuth()
        self._agent_connector = AgentConnector()
        self._conversation_history_manger = ConversationHistoryManager()
        self._agent = None
        self._runner = None
        self._initialized = False
        self._context_id = None

    async def _initialize(self):
        """Initialize async components"""
        if not self._initialized:
            self._agent = await self._build_agent()
            self._runner = Runner(
                app_name=AgentPrompts.OrchestratorAgent.NAME,
                agent=self._agent,
                session_service=InMemorySessionService(),
            )
            self._initialized = True

    async def _build_agent(self) -> LlmAgent:
        agentlist = await self._agent_registry.get_agents_list()
        agentcards = await self._agent_registry.get_context_cards()
        conversation_history = self._conversation_history_manger.fetch_last_n(
            self._context_id, 2
        )
        agentlist_str = json.dumps(agentlist, indent=2)
        agentcards_str = json.dumps(agentcards, indent=2)
        print(
            AgentPrompts.OrchestratorAgent.INSTRUCTION.format(
                conversation_history=conversation_history,
                agentlist=agentlist_str,
                agentcards=agentcards_str,
            )
        )
        return LlmAgent(
            name=AgentPrompts.OrchestratorAgent.NAME,
            instruction=AgentPrompts.OrchestratorAgent.INSTRUCTION.format(
                conversation_history=conversation_history,
                agentlist=agentlist_str,
                agentcards=agentcards_str,
            ),
            description=AgentPrompts.OrchestratorAgent.DESCRIPTION,
            model=LiteLlm(
                model=LlmConfig.Anthropic.OPUS_4_MODEL,
            ),
            tools=[
                FunctionTool(self.redirect_agent),
                FunctionTool(self.operator_handoff),
            ],
        )

    async def operator_handoff(self):
        return "Handded off to operator"

    async def redirect_agent(self, agent_name: str, message: str) -> str:
        try:
            cards = await self._agent_registry.load_cards()
            token = await self._agent_auth.get_m2m_token(agent_name=agent_name)
            matched_card = None

            for card in cards:
                if card.name.lower() == agent_name.lower():
                    matched_card = card
                elif getattr(card, "id", "").lower() == agent_name.lower():
                    matched_card = card

            if matched_card is None:
                return "Agent not found"

            result = await self._agent_connector.send_task(
                matched_card=matched_card, message=message, token=token
            )
            return str(result)

        except Exception as e:
            print(f"Error in redirect_agent: {e}")
            return f"Error redirecting to agent: {str(e)}"

    async def invoke(self, query: str, session_id: str) -> AsyncIterable[dict]:
        self._context_id = session_id
        if not self._initialized:
            await self._initialize()
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            session_id=session_id,
            user_id=self._user_id,
        )

        if not session:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                session_id=session_id,
                user_id=self._user_id,
            )

        user_content = types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        )

        async for event in self._runner.run_async(
            user_id=self._user_id, new_message=user_content, session_id=session_id
        ):
            if event.is_final_response():
                final_response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[-1].text
                ):
                    final_response = event.content.parts[-1].text
                    final_response_json = json.loads(final_response)
                self._conversation_history_manger.store(
                    username="random",
                    conversation_id=self._context_id,
                    conversation=final_response_json,
                )
                yield {"is_task_complete": True, "content": final_response}

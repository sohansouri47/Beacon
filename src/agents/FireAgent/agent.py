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


class FireAgent:
    def __init__(self):
        self._agent = self._build_agent()
        self._runner = Runner(
            app_name=AgentPrompts.FireAgent.NAME,
            agent=self._agent,
            session_service=InMemorySessionService(),
        )
        self._user_id = "random_user"

    def _build_agent(self) -> LlmAgent:
        return LlmAgent(
            name=AgentPrompts.FireAgent.NAME,
            instruction=AgentPrompts.FireAgent.INSTRUCTION,
            description=AgentPrompts.FireAgent.DESCRIPTION,
            model=LiteLlm(model=LlmConfig.Anthropic.SONET_4_MODEL),
        )

    async def invoke(self, query: str, session_id: str) -> AsyncIterable[dict]:
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

                yield {"is_task_complete": True, "content": final_response}
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "Fire Agent is assessing the emergency...",
                }

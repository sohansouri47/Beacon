from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from src.agents.MinorCallsAgent.agent import MinorCallsAgent
from a2a.utils import new_task, new_agent_text_message

from a2a.utils.errors import ServerError

from a2a.types import Task, TaskState, UnsupportedOperationError

import asyncio
from src.common.db.Postgre import ConversationHistoryManager


class MinorCallsAgentExecutor(AgentExecutor):
    """
    Implements the AgentExecutor interface to integrate the
    minor calls agent with the A2A framework.
    """

    def __init__(self):
        self.agent = MinorCallsAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Executes the agent with the provided context and event queue.
        """
        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for item in self.agent.invoke(query, task.context_id):
                is_task_complete = item.get("is_task_complete", False)

                if not is_task_complete:
                    message = item.get(
                        "updates", "Minor Calls Agent is providing care guidance..."
                    )
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(message, task.context_id, task.id),
                    )
                else:
                    final_result = item.get("content", "no result received")
                    await updater.update_status(
                        TaskState.completed,
                        new_agent_text_message(final_result, task.context_id, task.id),
                    )

                    manager = ConversationHistoryManager()
                    # manager.store(
                    #     "john", task.context_id, query, "MinorCallsAgent", final_result
                    # )
                    await asyncio.sleep(0.1)

                    break

        except Exception as e:
            error_message = f"Minor emergency handling error: {str(e)}"
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(error_message, task.context_id, task.id),
            )
            raise

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

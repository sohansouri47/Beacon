import uvicorn
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.request_handlers import DefaultRequestHandler
from src.agents.MinorCallsAgent.agent_Executor import MinorCallsAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication


def main():
    """Main function to create and run the minor calls agent."""

    skills = [
        AgentSkill(
            id="minor_injuries",
            name="Minor Injury Treatment",
            description="Handle cuts, scrapes, bruises, and minor injuries",
            tags=["injury", "first-aid", "treatment", "care"],
            examples=[
                "Clean and bandage minor cuts",
                "Treat small bruises and sprains",
                "Handle minor bleeding",
            ],
        ),
        AgentSkill(
            id="minor_medical",
            name="Minor Medical Issues",
            description="Address minor allergic reactions, headaches, and non-critical symptoms",
            tags=["medical", "allergies", "pain", "symptoms"],
            examples=[
                "Minor allergic reaction guidance",
                "Headache and pain management",
                "Minor eye irritation treatment",
            ],
        ),
        AgentSkill(
            id="first_aid_assessment",
            name="First Aid Assessment",
            description="Assess injury severity and provide appropriate care guidance",
            tags=["assessment", "triage", "evaluation", "safety"],
            examples=[
                "Evaluate if injury needs professional care",
                "Assess burn severity",
                "Determine escalation needs",
            ],
        ),
    ]

    agent_card = AgentCard(
        name="minor_calls_agent",
        description="Specialized agent for minor emergencies, injuries, and non-critical medical situations with first aid guidance.",
        url="http://localhost:8003/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=skills,
        capabilities=AgentCapabilities(streaming=True),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=MinorCallsAgentExecutor(), task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    uvicorn.run(server.build(), host="localhost", port=8003)


if __name__ == "__main__":
    main()

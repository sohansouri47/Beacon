import uvicorn
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.request_handlers import DefaultRequestHandler
from src.agents.FireAgent.agent_executor import FireAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication


def main():
    """Main function to create and run the fire agent."""

    skills = [
        AgentSkill(
            id="fire_emergency_response",
            name="Fire Emergency Response",
            description="Handle active fires, smoke incidents, and immediate fire emergencies",
            tags=["fire", "emergency", "rescue", "evacuation"],
            examples=[
                "Building on fire emergency response",
                "Smoke inhalation guidance",
                "Fire evacuation procedures",
            ],
        ),
        AgentSkill(
            id="burn_treatment",
            name="Burn Injury Treatment",
            description="Provide immediate burn care and treatment guidance",
            tags=["burns", "treatment", "first-aid", "medical"],
            examples=[
                "Cool thermal burns with water",
                "Chemical burn neutralization",
                "Electrical burn assessment",
            ],
        ),
        AgentSkill(
            id="fire_prevention",
            name="Fire Safety & Prevention",
            description="Fire prevention measures and safety protocols",
            tags=["prevention", "safety", "protocols", "education"],
            examples=[
                "Fire safety equipment checks",
                "Prevention strategies",
                "Safety protocol education",
            ],
        ),
    ]

    agent_card = AgentCard(
        name="fire_agent",
        description="Specialized fire emergency agent handling fires, burns, smoke incidents, and evacuation protocols using R.A.C.E. methodology.",
        url="http://localhost:8002/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=skills,
        capabilities=AgentCapabilities(streaming=True),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=FireAgentExecutor(), task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    uvicorn.run(server.build(), host="localhost", port=8002)


if __name__ == "__main__":
    main()

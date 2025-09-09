# Beacon 🚨  
AI-powered triage system for secure, multi-agent communication in emergency response.  



## Team  
**Solo Project** – Built by **Sohan Souri**  


## Hackathon Challenge  
- **Theme 3:** Secure agent-to-agent communication with Descope  
- **Theme:** *Design How Agents Talk, Trust, and Team Up*  
- **Level:** Advanced  


## Key Technical Achievements  
-  ✅ **Cross-Server Conversation History** powered by Neon Postgres for scalable, persistent storage.  
-  ✅ **End-to-End AI Stack** integrating Agent2Agent (A2A), ADK, and MCP for orchestration and extensibility.  
-  ✅ **Redis-Backed Auth Caching** with TTL for fast, secure token validation.  
-  ✅ **Pluggable Sub-Agents** for specialized tasks, enabling modular expansion.  
-  ✅ **Secure Agent-to-Agent Authentication Descope** with Descope Inbound Apps enforcing scoped trust.  
-  ✅ **OIDC Authentication via Descope**, including per-session logout handling.  
-  ✅ **Voice Chat Capabilities** for real-time multimodal (text + voice) interaction.  
-  ✅ **Containerized Sub-Agents** packaged with Docker for portability and scalability. 



## Problem Statement  
911 emergency call centers are overwhelmed. Over **240M+ calls/year** are made in the U.S., with up to **80% being non-emergencies**. With a **25% staffing shortage**, operators are tied up handling trivial cases while real emergencies face dangerous delays.  



## Objective  
**Beacon** introduces an **AI-powered triage layer** that filters out non-emergency traffic while instantly escalating true emergencies.  
This reduces operator overload, cuts delays, and saves lives.  



## What We Built  
Beacon is a **modular, secure, multi-agent system** powered by Descope IAM:  

- **Frontend (React + Tailwind)**  
  User interface for text and voice inputs (HTTP + WebSockets), secured with Descope login.  

- **Backend (FastAPI)**  
  Core API layer that routes requests to the orchestrator and maintains conversation context.  

- **Orchestrator Agent**  
  Central router that validates scoped tokens with Descope and dispatches tasks to the right sub-agent.  

- **Sub-Agents**  
  - **FireAgent** → Handles fire emergencies  
  - **CrimeAgent** → Handles crime-related reports  
  - **SpamAgent** → Filters out non-emergency traffic  
  Each sub-agent validates scoped tokens independently and processes requests.  

- **Authorization & Trust**  
  All agent-to-agent calls secured with **Descope Inbound Apps + scoped M2M tokens**. Tokens cached in Redis for efficiency.  

- **Media Layer**  
  Real-time **STT/TTS** powered by **FastRTC** for natural voice interaction.  

- **Deployment**  
  Dockerized microservices → scalable, modular, extensible.  



## Tech Stack  
- **Frontend**: React, Tailwind CSS  
- **Backend**: FastAPI (HTTP + WebSockets)  
- **Agents**: Google Agent2Agent protocol, Google ADK, FastMCP  
- **Infrastructure**: Docker, Redis, Postgres  
- **Auth & IAM**: Descope Inbound Apps (scoped M2M tokens)  
- **Media Layer**: FastRTC (STT + TTS)  
- **Architecture**: Orchestrator + Sub-Agents microservices

## Demo  
🎥 [Deck](https://vimeo.com/1117083737?share=copy)  
🎥 [Demo](https://vimeo.com/1117085766?share=copy)  


---




# 🔔 Beacon – Full Application Setup

Beacon is an AI-powered emergency triage system. To run the full application, the following microservices must be running:



## 🏗️ Required Microservices

### 1. Frontend Service (Local)

* Repository: [Beacon Frontend](https://github.com/sohansouri47/beacon-signal-hub)
* Run locally with `npm run dev`.
* Ensure `.env` is configured with your Descope project and backend URL.

### 2. Backend Microservice (Local)

* Repository: [Beacon Backend](https://github.com/sohansouri47/Beacon.git)
* Checkout branch `development-backend-only`
* Install dependencies and run locally:

```bash
# Git clone
git clone https://github.com/sohansouri47/Beacon.git
cd Beacon
git checkout development-backend-only

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
poetry install

# Copy .env.example to .env and fill in your values
cp .env.example .env

# Run backend
uvicorn main:app --host 0.0.0.0 --port 5001 --reload
```

### 3. Orchestrator Agent (Local)

* Repository: [Beacon Orchestrator](https://github.com/sohansouri47/orchestrator-agent)
* Run locally:

```bash
source venv/bin/activate
poetry install
cp .env.example .env
python3 -m src.agents.OrchestratorAgent
```

### 4. Crime Agent (Docker Image)

* Repository: [Crime Agent](https://github.com/sohansouri47/crime-agent)
* Pull and run the image:

```bash
docker pull ghcr.io/sohansouri47/crime_agent:1.0.0
docker run --name crime_agent --env-file .env -p 8003:8003 ghcr.io/sohansouri47/crime_agent:1.0.0
```

### 5. Spam Agent (Docker Image)

* Repository: [Spam Agent](https://github.com/sohansouri47/spam-agent)
* Pull and run the image (example):

```bash
docker pull ghcr.io/sohansouri47/spam_agent:1.0.1
docker run --name spam_agent --env-file .env -p 8001:8001 ghcr.io/sohansouri47/spam_agent:1.0.1
```

### 6. Fire Agent (Docker Image)

* Repository: [Fire Agent](https://github.com/sohansouri47/fire-agent)
* Pull and run the image (example):

```bash
docker pull ghcr.io/sohansouri47/fire_agent:2.0.0
docker run --name fire_agent --env-file .env -p 8002:8002 ghcr.io/sohansouri47/fire_agent:2.0.0
```

### 7. MCP (Docker Image)

* Repository: [MCP](https://github.com/sohansouri47/fire-agent)
* Pull and run the image (example):

```bash
docker pull ghcr.io/sohansouri47/orchestrator_mcp:2.0.0
docker run -d \                                   
  --name orchestrator_mcp \                
  -p 3000:3000 \
  -e MCP_HOST="0.0.0.0" \
  -e MCP_PORT="3000" \
  orchestrator_mcp:2.0.0
```

---

## ⚡ Notes

* **Frontend, Backend, Orchestrator** must run locally.
* **Sub-agent images and MCP** (Crime, Spam, Fire, MCP) are prebuilt and available via GHCR.
* Make sure all services are using the same `.env` configuration for Descope keys, database, and API credentials.
* You can monitor logs using `docker logs <container_name>` for agent containers.

---

## 📄 References

* Frontend: [Repo](https://github.com/sohansouri47/beacon-signal-hub)
* Backend : Current Repo
* Crime Agent: [Repo](https://github.com/sohansouri47/crime-agent/)
* Spam Agent: [Repo](https://github.com/sohansouri47/spam-agent/)
* Fire Agent: [Repo](https://github.com/sohansouri47/fire-agent/)
* Orchestrator Agent: [Repo](https://github.com/sohansouri47/orchestrator-agent)

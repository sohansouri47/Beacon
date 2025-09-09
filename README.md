# 🔔 Beacon – Full Application Setup

Beacon is an AI-powered emergency triage system. To run the full application, the following microservices must be running:



## 🏗️ Required Microservices

### 1. Frontend Service (Local)

* Repository: [Beacon Frontend](https://github.com/sohansouri47/beacon-signal-hub)
* Run locally with `npm run dev`.
* Ensure `.env` is configured with your Descope project and backend URL.

### 2. Backend Microservice (Local)

* Repository: [Beacon Backend](Current Repository)
* Install dependencies and run locally:

```bash
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
* **Sub-agent images** (Crime, Spam, Fire) are prebuilt and available via GHCR.
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

# CRM Voice Automation

[![Docker Hub](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/repository/docker/dattatraybodake/voice_bot-bot)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)[![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python)](https://www.python.org/)  
[![Postman](https://img.shields.io/badge/Postman-Collection-orange?logo=postman)](./VoiceBot_Collection.json)  [![Render](https://img.shields.io/badge/Deploy-Render-purple?logo=render)](https://render.com/)  

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Repository Structure](#repository-structure)  
- [Prerequisites](#prerequisites)  
- [Setup Instructions](#setup-instructions)  
- [Dockerization](#dockerization)  
- [Pushing to Docker Hub](#pushing-to-docker-hub)  
- [Image Signing](#image-signing)  
- [Deployment Instructions](#deployment-instructions)  
- [Environment Variables & Configurations](#environment-variables--configurations)  
- [Testing Instructions](#testing-instructions)  
- [Usage Examples](#usage-examples)  
- [Contributing Guidelines](#contributing-guidelines)  
- [Troubleshooting](#troubleshooting)

---

## Project Overview

**CRM Voice Automation** is an automated voice assistant application that integrates with a CRM system to create leads, schedule visits, and update lead statuses via natural language commands.  

Key features:

- Automated lead creation and updates via voice input.  
- Scheduling and tracking CRM visits.  
- Fully Dockerized for portability.  
- Docker images are pushed to Docker Hub and can be signed for verification.  
- Postman collection included for API testing.  

---

## Repository Structure
```bash
crm-voice-automation/
│
├── bot/                                                          # Bot service code
│ ├── init.py
│ ├── app.py
│ └── tests/
│ ├── test_bot_end_to_end.py                                      # all tests for bot
│ ├── test_lead_create.py
│ ├── test_lead_update.py
│ └── test_visit_schedule.py
│
├── mock_crm.py                                                   # Mock CRM service
├── requirements.txt                                              # Python dependencies
├── Dockerfile.bot                                                # Dockerfile for bot service
├── Dockerfile.crm                                                # Dockerfile for CRM service
├── docker-compose.yml                                            # Docker Compose configuration
├── .env                                                          # Environment variables
├── VoiceBot_Collection.json                                      # Postman collection
└── VoiceBot_Environment.json                                     # Postman environment for Lead ID testing
```

---

## Prerequisites

| Tool | Minimum Version | Installation |
|------|----------------|--------------|
| Docker | 20.x | [Docker Installation](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.x | [Docker Compose](https://docs.docker.com/compose/install/) |
| Git | 2.x | [Git Installation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) |
| Python | 3.11+ | [Python Installation](https://www.python.org/downloads/) |
| Postman | Latest | [Postman](https://www.postman.com/downloads/) |

---

## Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/DattatrayBodake25/crm-voice-automation.git

cd crm-voice-automation
```
2. **Create and activate a virtual environment (optional):**
```bash
#create virtual enviroment
python -m venv venv

#Activate venv for Windows
venv\Scripts\activate

#Activate venv for macOS/Linux
source venv/bin/activate
```
3. **Install dependencies:**
```bash
#install all dependencies
pip install -r requirements.txt
```

4. **Create a .env file and add your environment variables (refer to the Environment Variables section).**

---

## Local Testing
Run each service locally with uvicorn:
```bash
# Start mock CRM service
uvicorn mock_crm:app --host 0.0.0.0 --port 8001 --reload

# Start bot service
uvicorn bot.app:app --host 0.0.0.0 --port 8000 --reload
```
- Bot service docs: http://localhost:8000/docs
- CRM service docs: http://localhost:8001/docs

---

## Dockerization

1. **Build Docker images:**
```bash
# Bot service
docker build -f Dockerfile.bot -t voice_bot-bot .

# CRM service
docker build -f Dockerfile.crm -t voice_bot-crm .
```

2. **Run services using Docker Compose:**
```bash
docker compose up --build
```

3. **Verify services are running:**
- Bot: http://localhost:8000/docs
- CRM: http://localhost:8001/docs

---

## Pushing to Docker Hub

1. **Login to Docker Hub:**
```bash
docker login
```

2. **Tag Docker images:**
```bash
docker tag voice_bot-bot dattatraybodake/voice_bot-bot:latest

docker tag voice_bot-crm dattatraybodake/voice_bot-crm:latest
```

3. **Push images:**
```bash
docker push dattatraybodake/voice_bot-bot:latest

docker push dattatraybodake/voice_bot-crm:latest
```

---

## Image Signing
Enable Docker Content Trust to sign images:
```bash
export DOCKER_CONTENT_TRUST=1

docker push dattatraybodake/voice_bot-bot:latest

docker push dattatraybodake/voice_bot-crm:latest
```
- Ensure you have a Notary key configured for signing.

---

## Deployment Instructions
Deploying to Render:
1. Go to Render → New Web Service → Existing Image.
2. Use Docker Hub image URLs:
   - Bot: dattatraybodake/voice_bot-bot:latest
   - CRM: dattatraybodake/voice_bot-crm:latest
3. Set Environment Variables on Render.
4. Render automatically detects ports (8000 for bot, 8001 for CRM).
5. Deploy services and verify live URLs.

---

## Environment Variables & Configurations
The project requires certain environment variables to be set in a `.env` file or your deployment environment.  

| Variable       | Description             | Example                  |
|----------------|-------------------------|--------------------------|
| `CRM_URL`      | CRM service URL         | `http://mock-crm:8001`   |
| `BOT_API_KEY`  | Bot authentication key  | `your-secret-key`        |
| `DATABASE_URL` | Optional database URL   | `sqlite:///db.sqlite3`   |
| `PORT`         | Service port            | `8000` or `8001`         |

---

## Testing Instructions

1. Open Postman.
2. Import:
   - VoiceBot_Collection.json
   - VoiceBot_Environment.json
3. Select the environment for Lead ID testing.
4. Run requests and verify responses (200 OK expected).

---

## Usage Examples (with Postman)

You can test the APIs using the provided **Postman Collection** and **Environment** files located in the repository root.  

### 1. Create a Lead
**Request:** `POST /bot/handle`  
**Body (raw JSON):**
```json
{
  "transcript": "Add a new lead: John Doe from NY, phone 1234567890, source LinkedIn."
}
```

### 2. Schedule a Visit
**Request:** `POST /bot/handle`
**Body (raw JSON):**
```json
{
  "transcript": "Schedule a visit for lead <LEAD_ID> at 2025-10-10T14:00:00+05:30"
}
```

### 3. Update Lead Status
**Request:** `POST /bot/handle`
**Body (raw JSON):**
```json
{
  "transcript": "Update lead <LEAD_ID> to WON"
}
```

---

## Contributing Guidelines
1. Fork the repo.
2. Create a branch: git checkout -b feature/your-feature.
3. Make changes and add tests.
4. Commit: git commit -m "Add feature X".
5. Push: git push origin feature/your-feature.
6. Open a Pull Request.

---

## Troubleshooting

Common issues and their solutions:

| Issue                               | Solution                                                                  |
|-------------------------------------|---------------------------------------------------------------------------|
| **404 on `/` after deployment**     | Visit `/docs` instead or add a health check route.                        |
| **Docker push fails**               | Retry, check network, and ensure you are logged in using `docker login`.  |
| **Port conflicts**                  | Update Docker Compose or Render port settings.                            |
| **Environment variables not recognized** | Check the `.env` file or your Render environment settings.           |

---

# THANK YOU

---






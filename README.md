# CRM Voice Automation

[![Docker Hub](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/repository/docker/dattatraybodake/voice_bot-bot)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

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
- [License](#license)  

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






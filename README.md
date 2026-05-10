# 🚀 Nexus Intelligence: Enterprise Multi-Agent AI Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-000000.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Pinecone](https://img.shields.io/badge/VectorDB-Pinecone-262626.svg?style=flat&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![LangGraph](https://img.shields.io/badge/Orchestration-Custom%20Agents-blue.svg?style=flat)](https://langchain-ai.github.io/langgraph/)

> **Nexus Intelligence** is a state-of-the-art AI ecosystem designed to transform massive corporate data into instant, secure, and actionable insights. Built for **Meghna Group of Industries (MGI)**, it leverages a sophisticated multi-agent architecture to ensure grounded, compliant, and real-time intelligence.

---

## 👔 Executive Summary
In modern enterprise environments, critical knowledge is often siloed in thousands of PDFs, Excel sheets, and internal portals. **Nexus Intelligence** serves as a private, secure "Cognitive Layer" for the organization. It enables employees to query complex data and receive answers that are **100% grounded** in verified company documents, preventing "hallucinations" and ensuring data sovereignty.

### 📈 Business Impact
*   **Operational Efficiency**: Reduces data retrieval and analysis time by up to 90%.
*   **Data Security**: Private vector indexing ensures sensitive data never trains public LLMs.
*   **Regulatory Compliance**: Automated PII detection and policy enforcement on every AI response.
*   **Decision Support**: Real-time connectors for live data (weather, markets, etc.) alongside internal knowledge.

---

## 🏗️ Technical Architecture: The Agentic Workflow
Nexus utilizes a **decoupled, stateful agentic architecture**. Unlike linear RAG pipelines, Nexus employs specialized agents that reason, retrieve, and verify.

### 👑 The Supervisor Agent
The master orchestrator that manages the stateful workflow and handles provider fallbacks.
1.  **Intent Detection**: Routes queries to either the *Live Data Agent* (for external APIs) or the *Retriever Agent* (for internal knowledge).
2.  **Synthesis**: Coordinates the *Generator Agent* to produce a grounded response.
3.  **Verification**: Triggers the *Compliance Agent* for final security checks before user delivery.

### 🔍 Specialized Agents
*   **Retriever Agent**: Implements **Two-Step Semantic Search**. It first queries the `feedback_memory` namespace (Past Successes) before searching the main Pinecone index.
*   **Live Data Agent**: Real-time connectors (e.g., WeatherAPI) with robust regex-based entity extraction.
*   **Compliance Agent**: A dedicated security layer performing **PII Detection** (SSNs, Emails, Phone) and policy redaction.
*   **Generator Agent**: Multi-provider support (OpenAI GPT-4o, Google Gemini 1.5 Flash, X.AI Grok) for cost/performance optimization.

---

## 🛠️ Tech Stack
*   **Backend**: FastAPI (Async Python 3.10+), Pydantic v2.
*   **Frontend**: Next.js 14, Tailwind CSS, Framer Motion (High-Fidelity UI).
*   **Intelligence**: OpenAI API, Google Vertex AI, LangChain logic.
*   **Vector Engine**: Pinecone Cloud (Serverless).
*   **Ingestion**: BeautifulSoup4 (Web), Unstructured.io (PDF/Docx), Pandas (Tables).
*   **Security**: JWT Authentication (RS256), PII Redaction Logic.

---

## 📂 Project Structure
```text
├── backend/
│   ├── app/
│   │   ├── agents/      # Multi-agent logic (Supervisor, Retriever, etc.)
│   │   ├── api/         # V1 Endpoints (Auth, Chat, Ingestion)
│   │   ├── core/        # Security, Config, JWT logic
│   │   ├── db/          # Pinecone & Database connectors
│   │   └── services/    # Business logic & feedback loops
├── frontend/
│   ├── src/app/         # Next.js App Router (Dashboard & Auth)
│   └── public/          # Assets & Documentation
```

---

## 🚀 Deployment & Scaling
*   **Cloud Ready**: Dockerized for AWS ECS / Google Cloud Run.
*   **Monitoring**: Integrated agent-trace logs for real-time debugging.
*   **Scalability**: Stateless FastAPI backend and serverless Pinecone index scale horizontally.

---

## 👤 Recruiter-Focused Summary
This project demonstrates expertise in **Production-Level AI Engineering**:
*   **Full-Stack Ownership**: From Next.js UI to FastAPI backend.
*   **Advanced RAG**: Implementing namespaces, memory feedback, and multi-source ingestion.
*   **Agentic Systems**: Moving beyond "prompting" to "architecting" autonomous workflows.
*   **Enterprise Mindset**: prioritizing Security, Compliance, and Traceability.

---

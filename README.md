# 🚀 Nexus Intelligence: Enterprise Multi-Agent AI Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-000000.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Pinecone](https://img.shields.io/badge/VectorDB-Pinecone-262626.svg?style=flat&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![LangGraph](https://img.shields.io/badge/Orchestration-Custom%20Agents-blue.svg?style=flat)](https://langchain-ai.github.io/langgraph/)

> **Nexus Intelligence** is a state-of-the-art AI ecosystem designed to transform massive corporate data into instant, secure, and actionable insights. Built for **Business Product Solutions**, it leverages a sophisticated multi-agent architecture to ensure grounded, compliant, and real-time intelligence.

---

## 👔 Executive Summary
In modern enterprise environments, critical knowledge is often siloed in thousands of PDFs, Excel sheets, and internal portals. **Nexus Intelligence** serves as a private, secure "Cognitive Layer" for the organization. It enables employees to query complex data and receive answers that are **100% grounded** in verified company documents, preventing "hallucinations" and ensuring data sovereignty.

---

## 🛠️ My Key Contributions: What I Built & Why
This project demonstrates my ability to architect and deliver a full-lifecycle AI product.

- **System Orchestration**: I designed a **Supervisor-Worker pattern** that intelligently routes queries between live APIs and private RAG databases, optimizing both cost and accuracy.
- **Advanced Vector Engineering**: I implemented a **Multi-Namespace RAG Pipeline** in Pinecone, featuring a `feedback_memory` namespace that allows the AI to learn from user-upvoted answers.
- **Enterprise ETL Pipeline**: I built a robust ingestion engine that handles **Unstructured PDFs** and **Structured Excel/CSV data**, converting complex tables into semantic records the LLM can understand.
- **Security & Compliance**: I personally engineered the **Compliance Agent**, a post-processing layer that scans AI outputs for PII (emails, phones) and enforces enterprise safety standards.
- **Production DevOps**: I managed the end-to-end deployment on **AWS EC2**, using **PM2** for process management and **JWT (RS256)** for secure authentication.

---

## 🏗️ Technical Architecture: The Agentic Workflow
Nexus utilizes a **decoupled, stateful agentic architecture**. Unlike linear RAG pipelines, Nexus employs specialized agents that reason, retrieve, and verify.

### 👑 The Supervisor Agent
The master orchestrator that manages the stateful workflow.
1.  **Intent Detection**: Routes queries to the *Live Data Agent* or *Retriever Agent*.
2.  **Synthesis**: Coordinates the *Generator Agent* for grounded responses.
3.  **Verification**: Triggers the *Compliance Agent* for security checks.

### 🔍 Specialized Agents
*   **Retriever Agent**: Implements **Two-Step Semantic Search** (Memory Namespace + Main Index).
*   **Live Data Agent**: Real-time connectors for external APIs (e.g., WeatherAPI).
*   **Compliance Agent**: Dedicated security layer for **PII Detection** and redaction.
*   **Generator Agent**: Multi-provider support (OpenAI GPT-4o, Gemini 1.5 Flash, Grok).

---

## 🛠️ Tech Stack
- **Backend**: FastAPI (Async Python 3.10+), Pydantic v2.
- **Frontend**: Next.js 14, Tailwind CSS, Framer Motion (High-Fidelity UI).
- **Intelligence**: OpenAI API, Google Vertex AI, LangChain logic.
- **Vector Engine**: Pinecone Cloud (Serverless).
- **Ingestion**: BeautifulSoup4 (Web), Unstructured.io (PDF/Docx), Pandas (Tables).

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

## 🚶 Full Project Walkthrough

### 1. Secure Authentication
- **Logic**: JWT-based authentication with role-based access (Admin/User).
- **Backend**: `auth.py` handles token generation and hashing using Passlib.

### 2. Knowledge Ingestion
- **File Upload**: Supports PDF, Docx, CSV, and Excel. 
    - *Under the hood*: Files are partitioned, chunked, and vectorized using OpenAI/Google embeddings.
- **Web Scraping**: Input any URL to index its content.
    - *Under the hood*: BeautifulSoup4 extracts text, removes noise, and performs semantic indexing.

### 3. The Intelligent Chat
1. **Routing**: The Supervisor decides if the query needs real-time APIs or private documents.
2. **Context Retrieval**: The Retriever Agent checks memory first, then the main index.
3. **Reasoning**: LLM synthesizes an answer grounded **only** in the retrieved context.
4. **Agent Trace**: UI displays internal logs for 100% transparency.

---

## 💻 Deep File & Function Analysis (Core Logic)

### 👑 The Agent Layer (`backend/app/agents/`)

#### `supervisor.py` (The Orchestrator)
- **FUNCTION: `process_request(query)`**: Routes queries based on intent detection.
    ```python
    if live_data_agent.can_handle(query):
        return await live_data_agent.run(query)
    context, sources = retriever_agent.run(query)
    answer = generator_agent.run(query, context)
    ```

#### `retriever.py` (The Memory)
- **FUNCTION: `run(query)`**: Performs semantic search across Pinecone namespaces.
    ```python
    feedback_results = self.index.query(vector=query_vec, top_k=1, namespace="feedback_memory")
    results = self.index.query(vector=query_vec, top_k=4)
    ```

#### `compliance.py` (The Guardrail)
- **FUNCTION: `run(text)`**: Scans for PII and redacts sensitive data.
    ```python
    if not check["compliant"]:
        answer = "REDACTED: Response blocked by enterprise security policy."
    ```

### 📤 The Ingestion Layer (`backend/app/api/v1/endpoints/`)

#### `upload.py` (File Processing)
- **FUNCTION: `table_to_records(file_path)`**: Converts Excel/CSV rows into sentences.
    ```python
    text = f"Row: {idx + 2}\n" + "\n".join([f"{k}: {v}" for k, v in row_data.items()])
    ```

#### `scrape.py` (Web Ingestion)
- **FUNCTION: `_perform_scrape(url)`**: Extracts clean text from URLs.
    ```python
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    ```

---

## 🚀 Deployment & Scaling

### 1. AWS EC2 & PM2 Setup
The platform is designed to be managed using **PM2** on an Ubuntu-based AWS EC2 instance.
```bash
# Start Backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name nexus-backend

# Start Frontend
cd frontend && npm run build
pm2 start "npm run start" --name nexus-frontend
```

### 2. DuckDNS & SSL Setup
To provide a secure, production-ready URL (`https://nexusintelligence.duckdns.org`), we use **DuckDNS** and **Nginx** as a reverse proxy.

- **DuckDNS**: Syncs the AWS EC2 Elastic IP to a custom domain.
- **Nginx Config**:
```nginx
server {
    server_name nexusintelligence.duckdns.org;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
    }

    # Backend API (FastAPI)
    location /api {
        proxy_pass http://localhost:8000;
    }

    listen 443 ssl; # Managed by Certbot
}
```
- **SSL**: Secured via **Let's Encrypt (Certbot)** for enterprise-grade encryption.

#### 🛡️ Certificate Verification
To verify the SSL status and renewal on the AWS server, use:
```bash
# Check existing certificates
sudo certbot certificates

# Test live SSL connection and expiry
openssl s_client -connect nexusintelligence.duckdns.org:443 -servername nexusintelligence.duckdns.org | openssl x509 -noout -dates

# Check Nginx configuration health
sudo nginx -t
```

### 3. Scalability
The stateless FastAPI backend and serverless Pinecone index allow the system to scale horizontally to handle thousands of concurrent users.

---

## 👤 Recruiter-Focused Summary
This project demonstrates expertise in **Production-Level AI Engineering**:
*   **Full-Stack Ownership**: From Next.js UI to FastAPI backend.
*   **Advanced RAG**: Implementing namespaces, memory feedback, and multi-source ingestion.
*   **Agentic Systems**: Moving beyond "prompting" to "architecting" autonomous workflows.
*   **Enterprise Mindset**: Prioritizing Security, Compliance, and Traceability.

---

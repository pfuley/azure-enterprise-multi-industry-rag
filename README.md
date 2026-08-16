# Enterprise Multi-Industry RAG

A secure enterprise Retrieval-Augmented Generation (RAG) application built with **Python, FastAPI, React, Microsoft Entra ID, Azure AI Search, Azure OpenAI, Azure Cosmos DB, and Azure AI Content Safety**.

This project demonstrates how a RAG system can move beyond basic document retrieval by adding authentication, authorization, persistent conversation memory, AI guardrails, evaluation, and a complete web application layer.

---

## Architecture

    React + Vite
          ↓
    MSAL / Microsoft Entra ID
          ↓
        FastAPI
          ↓
    Token Validation + Authorization
          ↓
    Cosmos DB Conversation Memory
          ↓
      RAG Orchestrator
          ↓
      Azure AI Search
          ↓
       Azure OpenAI
          ↓
    Grounded Answer + Sources

---

## Key Features

- Azure OpenAI for embeddings and grounded answer generation
- Azure AI Search for vector, hybrid, and semantic retrieval
- Metadata and document-level authorization filtering
- Microsoft Entra ID authentication
- Delegated `RAG.Access` API scope
- Entra role mapping to internal application permissions
- Azure AI Content Safety and Prompt Shields
- Persistent multi-turn conversations using Azure Cosmos DB
- Conversational query rewriting using previous chat history
- FastAPI backend with protected REST endpoints
- React/Vite frontend with Microsoft authentication using MSAL
- Persistent conversation sidebar
- Markdown answer rendering
- Source and citation cards
- Automated RAG evaluation and quality gates
- Structured API error handling

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### AI & Retrieval

- Azure OpenAI
- Azure AI Search
- Azure AI Content Safety

### Security

- Microsoft Entra ID
- OAuth 2.0
- JWT validation
- MSAL
- Role and group-based authorization

### Persistence

- Azure Cosmos DB for NoSQL

### Frontend

- React
- Vite
- JavaScript
- CSS
- React Markdown

---

## Project Structure

    multi-industry-rag/
    │
    ├── src/                 # Backend application
    ├── scripts/             # Setup, testing and evaluation scripts
    ├── frontend-react/      # React/Vite frontend
    ├── frontend-basic/      # Basic HTML/CSS/JavaScript frontend
    ├── evaluation/          # Evaluation datasets and reports
    ├── data/                # Sample knowledge documents
    ├── requirements.txt
    ├── .env.example
    └── README.md

---

## Running the Backend

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file using `.env.example` as the template.

Do not commit secrets, API keys, tokens, or connection strings.

### 4. Start FastAPI

```powershell
uvicorn src.main:app --reload
```

The API runs locally at:

    http://127.0.0.1:8000

FastAPI API documentation is available at:

    http://127.0.0.1:8000/docs

---

## Running the React Frontend

Move into the React application:

```powershell
cd frontend-react
```

Install dependencies:

```powershell
npm install
```

Configure the frontend `.env` file with the required Microsoft Entra and API settings.

Start Vite:

```powershell
npm run dev
```

Open the application at:

    http://localhost:5173/

The frontend authenticates users through Microsoft Entra ID and sends the resulting access token to the protected FastAPI backend.

---

## API Endpoints

    POST   /api/v1/chat
    GET    /api/v1/sessions
    GET    /api/v1/sessions/{session_id}/history
    DELETE /api/v1/sessions/{session_id}
    GET    /health

---

## Evaluation

Run the RAG evaluation suite:

```powershell
python -m scripts.run_evaluation
```

The quality gate evaluates:

- Retrieval hit rate
- Concept coverage
- Groundedness
- Answer relevance
- Security behaviour

Example result:

    QUALITY GATE
    ==========================================

    hit_rate: PASS
    concept_score: PASS
    groundedness: PASS
    relevance: PASS
    security_pass_rate: PASS

    Overall: PASS

---

## Security Design

The application follows several important enterprise RAG security principles:

- Users authenticate before accessing protected endpoints.
- Microsoft Entra access tokens are validated by the backend.
- External Entra identities are mapped to internal authorization policies.
- Authorization filtering occurs before documents are provided to the LLM.
- Users can only access their own Cosmos DB conversations.
- Prompt Shields inspect user prompts and retrieved documents.
- Content safety controls protect the generation pipeline.
- Secrets and environment-specific credentials remain outside source control.

---

## Current Application Flow

    Microsoft Sign-In
            ↓
      React Frontend
            ↓
       Access Token
            ↓
         FastAPI
            ↓
    Identity Validation
            ↓
      Authorization
            ↓
    Cosmos DB Memory
            ↓
    Query Rewriting
            ↓
      RAG Retrieval
            ↓
    Azure AI Search
            ↓
      Guardrails
            ↓
      Azure OpenAI
            ↓
    Grounded Response
            ↓
    Sources + Answer
            ↓
      React Frontend

---

## Current Status

The project currently provides a working end-to-end authenticated enterprise RAG application with:

- Secure Microsoft sign-in
- Protected backend APIs
- Identity-aware retrieval
- Persistent conversation memory
- Multi-turn conversations
- Secure document retrieval
- AI safety guardrails
- Grounded answer generation
- Source attribution
- Automated RAG evaluation
- React-based chat interface

---

## Documentation

A dedicated `docs/` section is being developed to document the engineering journey behind this project.

It will cover:

- RAG concepts and architecture
- Document ingestion and chunking
- Embeddings and vector search
- Hybrid and semantic search
- RAG orchestration
- Authentication and authorization
- AI security and guardrails
- Evaluation and quality gates
- FastAPI architecture
- Cosmos DB conversation memory
- React and MSAL authentication
- Problems encountered and their solutions
- Architecture decisions and lessons learned

The goal is to document not only **what was built**, but also **why each component exists and how the complete system evolved**.

---

## Roadmap

Planned improvements include:

- [ ] Project journey and technical concept documentation
- [ ] OpenTelemetry tracing
- [ ] Azure Application Insights integration
- [ ] RAG pipeline observability
- [ ] Production deployment
- [ ] CI/CD
- [ ] Infrastructure as Code
- [ ] Response streaming
- [ ] Additional industry datasets
- [ ] Expanded authorization policies
- [ ] Automated conversation titles
- [ ] Production monitoring and alerting

---

## Project Goal

The goal of this project is to understand and implement the architecture required to move from a simple RAG prototype toward a secure, observable, testable, and deployable enterprise AI application.

Rather than treating RAG as only a vector-search problem, the project explores the wider engineering concerns required for real applications:

- retrieval quality
- security
- identity
- authorization
- conversation state
- AI safety
- evaluation
- API design
- frontend integration
- observability
- deployment

---

## License

See the `LICENSE` file for licensing information.
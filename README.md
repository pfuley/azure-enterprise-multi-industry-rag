# Azure Enterprise Multi-Industry RAG

A production-oriented, multi-industry **Retrieval-Augmented Generation (RAG)** platform built from scratch using **Python, Azure OpenAI, and Azure AI Search**.

The purpose of this project is to understand how an enterprise RAG system works at every layer rather than relying on a pre-built RAG framework.

The project is being developed incrementally so ingestion, retrieval, generation, conversation management, security, observability, evaluation, and deployment can be understood and debugged independently.

---

## Reference Architecture

This project is independently implemented from scratch for learning and portfolio purposes.

Microsoft's **Azure Search OpenAI Demo** is used as an architectural reference for understanding production Azure RAG patterns and comparing design decisions.

Reference repository:

https://github.com/Azure-Samples/azure-search-openai-demo

The Microsoft repository itself is not included in this repository.

---

# Current Architecture

```text
                         DOCUMENT INGESTION

Documents
   │
   ▼
File Detection / Parsing
   │
   ├──────────────┐
   ▼              ▼
 TXT             PDF
   │              │
   └──────┬───────┘
          ▼
      Document Model
          │
          ▼
Sentence + Token-Aware
       Chunking
          │
          ▼
    Business Metadata
          +
      Security ACLs
          │
          ▼
Azure OpenAI Embeddings
          │
          ▼
    Azure AI Search


                         SECURE RETRIEVAL

User Authorization Context
          │
          ▼
Security Filter Builder
          │
          ▼
      User Question
          │
          ▼
      Query Embedding
          │
    ┌─────┴─────┐
    ▼           ▼
 Keyword      Vector
 Search        Search
    │           │
    └─────┬─────┘
          ▼
         RRF
          │
          ▼
 Semantic Reranking
          │
          ▼
 Authorised Chunks Only


                      CONVERSATIONAL RAG

Conversation History
        +
User Question
        │
        ▼
   Query Rewriting
        │
        ▼
Standalone Search Query
        │
        ▼
Secure Retrieval
        │
        ▼
Context Builder
        │
        ▼
Azure OpenAI
        │
        ▼
Grounded Answer
        +
Sources
        +
Retrieval Diagnostics
```

---

# Technology Stack

## Application

- Python
- OpenAI Python SDK
- Azure SDK for Python
- Python virtual environments

## Azure

- Microsoft Foundry / Azure OpenAI
- Azure AI Search
- Azure OpenAI embedding deployment
- Azure OpenAI chat deployment

## Retrieval

- Vector search
- HNSW
- Keyword search
- Hybrid retrieval
- Reciprocal Rank Fusion (RRF)
- Semantic ranking
- Metadata filtering
- ACL-based security filtering

## Document Processing

- PyPDF
- Tiktoken
- Sentence-aware chunking
- Token-aware chunking
- Page-aware PDF processing

## Development

- Git
- GitHub
- VS Code
- PowerShell
- Environment-based configuration

---

# Project Structure

```text
multi-industry-rag/
│
├── data/
│   ├── it-support/
│   ├── financial-services/
│   └── government/
│
├── scripts/
│   ├── test_ingestion.py
│   ├── test_vector_search.py
│   ├── test_rag.py
│   ├── test_query_rewrite.py
│   ├── test_chat.py
│   ├── test_session_summary.py
│   └── test_authorization_filter.py
│
├── src/
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── parser.py
│   │   ├── pdf_parser.py
│   │   ├── models.py
│   │   ├── chunker.py
│   │   ├── metadata.py
│   │   ├── industry_config.py
│   │   ├── embeddings.py
│   │   └── pipeline.py
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── index_schema.py
│   │   ├── uploader.py
│   │   └── document_lifecycle.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── vector_search.py
│   │
│   ├── conversation/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── summarizer.py
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── authorization.py
│   │   └── filters.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── context_builder.py
│   │   ├── query_rewriter.py
│   │   ├── orchestrator.py
│   │   └── chat_service.py
│   │
│   └── main.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The application is intentionally separated into components so individual stages can be tested and debugged independently.

---

# Document Ingestion

The ingestion pipeline prepares enterprise documents for retrieval.

```text
File
 ↓
Load / Parse
 ↓
Document
 ↓
Chunk
 ↓
Metadata + ACL
 ↓
Embedding
 ↓
Azure AI Search
```

The pipeline currently supports:

- TXT documents
- PDF documents
- Page-aware PDF processing
- Sentence-aware chunking
- Token-aware chunking
- Chunk overlap
- Enterprise metadata
- Document ACL metadata
- Azure OpenAI embeddings
- Azure AI Search indexing

PDF page numbers are retained so retrieved information can later be traced back to the original source.

---

# Chunking

The project originally used character-based chunking and was later upgraded to sentence and token-aware chunking.

The current strategy uses:

```text
Sentence boundaries
        +
Token limits
        +
Sentence overlap
        +
PDF page boundaries
```

This reduces arbitrary text splitting and improves the quality of the units passed to retrieval.

Tiktoken is used to estimate chunk size using tokens rather than raw character counts.

---

# Multi-Industry Metadata

Chunks can contain business metadata such as:

```text
industry
department
document_type
classification
```

Example:

```text
industry: it-support
department: service-desk
document_type: knowledge-article
classification: internal
```

This allows one RAG platform to support multiple enterprise knowledge domains.

Planned domains include:

```text
Enterprise RAG
│
├── IT / Cyber Security
├── Financial Services
└── Government
```

---

# Azure OpenAI Embeddings

Document chunks are converted into vector representations using an Azure OpenAI embedding deployment.

The current implementation uses:

```text
text-embedding-3-small
```

with:

```text
1536 dimensions
```

User queries are embedded using the same deployment so semantic similarity can be calculated during vector retrieval.

---

# Azure AI Search

Azure AI Search stores searchable text, metadata, ACL information, and embeddings.

Current index information includes:

| Field | Purpose |
|---|---|
| `chunk_id` | Unique chunk identifier |
| `content` | Searchable chunk text |
| `file_name` | Original source |
| `chunk_index` | Chunk position |
| `page_number` | Original PDF page |
| `industry` | Knowledge domain |
| `department` | Business department |
| `document_type` | Document category |
| `classification` | Information classification |
| `allowed_groups` | Groups permitted to access the chunk |
| `allowed_roles` | Roles permitted to access the chunk |
| `embedding` | Vector representation |

---

# Retrieval

Three retrieval strategies have been implemented.

## Vector Search

```text
Question
   ↓
Embedding
   ↓
Vector Similarity
   ↓
Relevant Chunks
```

## Hybrid Search

```text
Keyword Search
       +
Vector Search
       ↓
      RRF
       ↓
Combined Ranking
```

## Semantic Hybrid Search

```text
Keyword Search
       +
Vector Search
       ↓
      RRF
       ↓
Semantic Reranking
       ↓
Final Results
```

The production-oriented RAG path currently uses semantic hybrid retrieval.

---

# Grounded Generation

Retrieved chunks are converted into grounding context before being passed to the Azure OpenAI chat model.

```text
Question
   ↓
Retrieval
   ↓
Relevant Authorised Chunks
   ↓
Context Builder
   ↓
Azure OpenAI
   ↓
Grounded Answer
```

The model is instructed to use retrieved knowledge-base content for factual claims.

If no authorised information is retrieved, generation is stopped and the application returns an insufficient-information response.

---

# Source Traceability

Retrieved chunks retain:

```text
file_name
page_number
chunk_id
```

This provides the foundation for citations such as:

```text
[SOURCE: policy.pdf, Page 17]
```

Source metadata is also returned separately from the generated response so a future API or web interface can display citations independently.

---

# Conversational RAG

The system supports multi-turn questions.

Example:

```text
User:
What is retrieval augmented generation?

Assistant:
...

User:
Why is it useful?
```

The second question is ambiguous by itself.

The system therefore performs:

```text
Conversation History
        +
Latest Question
        ↓
Query Rewriter
        ↓
Standalone Search Query
```

For example:

```text
Why is it useful?
```

can become:

```text
Why is retrieval augmented generation useful?
```

The rewritten query is then sent through the retrieval pipeline.

---

# Conversation Management

Each conversation has a unique session.

```text
ConversationSession
│
├── session_id
├── recent history
└── conversation summary
```

Conversation history is bounded to prevent unlimited growth.

Older messages can be summarised:

```text
Older Messages
      ↓
Summarisation
      ↓
Compact Summary
      +
Recent Messages
      ↓
Future Requests
```

This reduces token usage while retaining useful conversational context.

Conversation history helps understand the dialogue but is **not treated as authoritative enterprise knowledge**.

---

# Retrieval Diagnostics

The RAG pipeline returns diagnostic information including:

```text
session ID
rewritten search query
retrieved chunk IDs
source files
page numbers
search scores
semantic reranker scores
```

This allows incorrect answers to be investigated systematically.

```text
Bad Answer
    ↓
Query rewriting problem?
    ↓
Retrieval problem?
    ↓
Security filtering problem?
    ↓
Ranking problem?
    ↓
Context problem?
    ↓
Generation problem?
```

This is one of the reasons the application is divided into separate layers.

---

# Enterprise Authorization

Commit 9 introduces the first enterprise security layer.

The application now represents user permissions using an:

```text
AuthorizationContext
```

Example:

```text
User
│
├── User ID
├── Roles
├── Groups
├── Allowed Industries
├── Allowed Departments
└── Maximum Classification
```

This separates two important security concepts:

```text
Authentication
=
Who are you?

Authorization
=
What are you allowed to access?
```

Microsoft Entra ID authentication will be introduced in a later phase.

---

# Document-Level Access Control

Chunks can now contain Access Control List (ACL) metadata:

```text
allowed_groups
allowed_roles
```

Example:

```text
Document:
IT Support Knowledge Article

allowed_groups:
- service-desk
- it-admins

allowed_roles:
- employee
```

An authorised user may have:

```text
groups:
- service-desk

roles:
- employee
```

while an unauthorised user might have:

```text
groups:
- finance-team

roles:
- employee
```

The second user is prevented from retrieving the protected document.

---

# Security-Filtered Retrieval

Authorization is enforced during retrieval rather than after generation.

```text
User
   ↓
AuthorizationContext
   ↓
Security Filter Builder
   ↓
Azure AI Search
   ↓
Authorised Chunks Only
   ↓
Context Builder
   ↓
LLM
```

This is an important security principle.

The system does **not**:

```text
Retrieve restricted information
        ↓
Send it to the LLM
        ↓
Ask the LLM not to reveal it
```

Instead:

```text
Authorization
        ↓
Search filtering
        ↓
Restricted chunks excluded
        ↓
LLM never receives them
```

The authorization test currently verifies that the same question can produce different retrieval results for users with different permissions.

---

# Classification Enforcement

The authorization model includes a maximum classification level.

Current hierarchy:

```text
public
   ↓
internal
   ↓
confidential
   ↓
restricted
```

For example, a user with:

```text
max_classification = internal
```

can access:

```text
public
internal
```

but not:

```text
confidential
restricted
```

Classification filtering is combined with industry, department, group, and role restrictions.

---

# Secure Re-Ingestion and Document Lifecycle

A production search index must handle documents that change over time.

For example:

```text
Old version:
policy.pdf
→ 20 chunks

New version:
policy.pdf
→ 12 chunks
```

Simply uploading the new 12 chunks can leave obsolete chunks from the previous version in the index.

This can cause:

- stale information
- duplicate knowledge
- outdated policies
- obsolete ACLs
- restricted information remaining searchable

The ingestion pipeline therefore performs document cleanup before re-indexing:

```text
Re-ingest Document
       ↓
Find existing chunks
       ↓
Delete previous chunks
       ↓
Parse latest document
       ↓
Create fresh chunks
       ↓
Apply current metadata + ACLs
       ↓
Generate embeddings
       ↓
Upload fresh chunks
```

This ensures the search index represents the current document and current security configuration.

---

# Security Architecture So Far

```text
                 CURRENT DEVELOPMENT MODEL

Simulated User
      │
      ▼
AuthorizationContext
      │
      ├── roles
      ├── groups
      ├── industries
      ├── departments
      └── classification
      │
      ▼
Security Filter Builder
      │
      ▼
Azure AI Search
      │
      ▼
Authorised Chunks
      │
      ▼
RAG Pipeline


                   FUTURE PRODUCTION MODEL

Microsoft Entra ID
      │
      ▼
Authenticated Identity
      │
      ▼
Enterprise Groups / Roles
      │
      ▼
AuthorizationContext
      │
      ▼
Security-Filtered Retrieval
      │
      ▼
Azure AI Search
      │
      ▼
Authorised Context Only
      │
      ▼
Azure OpenAI
```

---

# Security Testing

The current test suite simulates users with different permissions.

### Authorised User

```text
Industry: IT Support
Department: Service Desk
Group: service-desk
Role: employee
Classification: internal
```

Expected:

```text
Protected IT document
        ↓
Retrieved
        ↓
Grounded answer
```

### Unauthorised User

```text
Industry: IT Support
Department: Service Desk
Group: finance-team
Role: employee
Classification: internal
```

Expected:

```text
Protected IT document
        ↓
Rejected by ACL
        ↓
No authorised chunks
        ↓
No grounded answer generated
```

This verifies that authorization is enforced at retrieval time.

---

# Key Learnings

Building the platform incrementally has demonstrated:

- RAG consists of independent ingestion, retrieval, augmentation, and generation stages.
- Embeddings enable semantic vector retrieval.
- Chunking strategy directly affects retrieval quality.
- Token-aware chunking is more appropriate for LLM workloads than arbitrary character boundaries.
- Page metadata enables traceable citations.
- Hybrid search combines lexical and semantic retrieval.
- Semantic ranking reranks retrieved candidates.
- Metadata enables knowledge-domain separation.
- Conversation memory and enterprise knowledge are different concepts.
- Query rewriting improves multi-turn retrieval.
- Conversation history should be bounded or summarised.
- Retrieval diagnostics are essential for debugging RAG failures.
- Authentication and authorization solve different problems.
- Client-provided filters should not determine user permissions.
- Authorization should be enforced before restricted content reaches the LLM.
- ACL metadata can provide document-level security trimming.
- Classification can provide an additional authorization boundary.
- Re-ingestion must remove stale chunks rather than only uploading new ones.
- Stale search data can become both a data-quality and security problem.
- Separating application layers makes production failures easier to diagnose.

---

# Development Progress

## Completed

- [x] Python project foundation
- [x] Environment-based configuration
- [x] Application logging
- [x] TXT ingestion
- [x] PDF parsing
- [x] Page-aware PDF processing
- [x] Sentence-aware chunking
- [x] Token-aware chunking
- [x] Chunk overlap
- [x] Multi-industry metadata
- [x] Azure OpenAI embeddings
- [x] Azure AI Search index
- [x] HNSW vector retrieval
- [x] Metadata filtering
- [x] Hybrid search
- [x] Semantic ranking
- [x] Grounded RAG generation
- [x] Source metadata and citations
- [x] Query rewriting
- [x] Multi-turn conversational RAG
- [x] Conversation sessions
- [x] Conversation summarisation
- [x] Retrieval diagnostics
- [x] Authorization context
- [x] Role and group ACL metadata
- [x] Classification-based authorization
- [x] Security filter generation
- [x] Security-filtered Azure AI Search retrieval
- [x] Positive authorization testing
- [x] Negative authorization testing
- [x] Secure document re-ingestion
- [x] Stale chunk cleanup

## Planned

- [ ] Microsoft Entra ID authentication
- [ ] Real Entra group/role mapping
- [ ] Managed identities
- [ ] Azure Key Vault
- [ ] Prompt injection defenses
- [ ] Input/output guardrails
- [ ] Azure AI Content Safety
- [ ] Real multi-industry document corpus
- [ ] Azure AI Document Intelligence
- [ ] Structure-aware chunking
- [ ] RAG evaluation framework
- [ ] Retrieval quality metrics
- [ ] Groundedness evaluation
- [ ] OpenTelemetry tracing
- [ ] Application Insights
- [ ] REST API
- [ ] Web application
- [ ] Persistent/distributed conversation storage
- [ ] Infrastructure as Code
- [ ] Automated testing
- [ ] CI/CD
- [ ] DEV / TEST / PROD environments
- [ ] Private networking
- [ ] Production deployment

---

# Environment Configuration

Application configuration is loaded from environment variables.

Real credentials should be stored locally in:

```text
.env
```

and must not be committed.

The repository contains:

```text
.env.example
```

to document required variables without exposing secrets.

The current development implementation uses API keys where required.

Later production stages will progressively replace key-based authentication with:

```text
Microsoft Entra ID
        +
Managed Identity
        +
Azure RBAC
        +
Azure Key Vault
```

---

# Real-World Knowledge Corpus

The platform is designed to eventually ingest large public documents rather than relying only on small artificial samples.

Planned domains include:

### IT / Cyber Security

Public cybersecurity standards, controls, manuals, and operational guidance.

### Financial Services

Public financial regulation, legislation, compliance material, and operational-risk guidance.

### Government

Public legislation, policy, standards, and administrative guidance.

Large third-party documents will generally not be committed directly to the repository. Official sources and ingestion instructions can instead be documented.

---

# Git Development Milestones

The project is being developed through capability-based commits.

```text
Commit 1
Project foundation

Commit 2
Document ingestion and metadata pipeline

Commit 3
Vector and hybrid retrieval with metadata filters

Commit 4
Semantic ranking

Commit 5
Grounded RAG generation and citations

Commit 6
Multi-format ingestion and page-aware PDF processing

Commit 7
Token and sentence-aware chunking

Commit 8
Conversational RAG, session memory and retrieval diagnostics

Commit 9
Enterprise authorization, document ACLs and secure re-ingestion

Next
Microsoft Entra ID authentication and identity integration
```

---

# Current End-to-End Flow

```text
                         USER
                           │
                           ▼
                 Authorization Context
                           │
                           ▼
                  Conversation Session
                           │
                           ▼
                    Query Rewriting
                           │
                           ▼
                  Standalone Query
                           │
                           ▼
                 Security Filter Builder
                           │
                           ▼
                    Azure AI Search
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
             Keyword              Vector
              Search               Search
                 │                   │
                 └─────────┬─────────┘
                           ▼
                          RRF
                           │
                           ▼
                  Semantic Reranking
                           │
                           ▼
                   Authorised Chunks
                           │
                           ▼
                    Context Builder
                           │
                           ▼
                     Azure OpenAI
                           │
                           ▼
                    Grounded Answer
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
             Sources          Retrieval Diagnostics
                           │
                           ▼
                  Conversation Memory
```

The project now has a functional end-to-end **security-aware conversational RAG pipeline**.

The next phase will replace simulated user identities with real enterprise identity information using **Microsoft Entra ID**, bringing authentication and authorization together.
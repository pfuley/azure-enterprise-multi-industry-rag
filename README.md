# Azure Enterprise Multi-Industry RAG

A production-oriented, multi-industry **Retrieval-Augmented Generation (RAG)** platform built from scratch using **Python, Azure OpenAI, and Azure AI Search**.

The purpose of this project is to understand how an enterprise RAG system works at every layer rather than relying on a pre-built framework. The project is being developed incrementally so that ingestion, retrieval, generation, conversation management, security, evaluation, observability, and deployment can be understood and debugged independently.

The architecture is designed to support multiple industry knowledge domains using the same RAG platform.

---

## Reference Architecture

This project is independently implemented from scratch for learning and portfolio purposes.

Microsoft's **Azure Search OpenAI Demo** is being used as a reference for studying production Azure RAG architecture and comparing design decisions.

Reference:

https://github.com/Azure-Samples/azure-search-openai-demo

The Microsoft repository itself is not included in this repository.

---

# Architecture

The system currently contains four major pipelines:

```text
                         DOCUMENT INGESTION

Documents
   │
   ▼
File Type Detection
   │
   ├──────────────┐
   ▼              ▼
 TXT             PDF
   │              │
Text Loader    PDF Parser
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
Metadata Enrichment
          │
          ▼
Azure OpenAI Embeddings
          │
          ▼
Azure AI Search Index


                         RETRIEVAL

User Query
     │
     ▼
Query Embedding
     │
     ├─────────────────────┐
     ▼                     ▼
Keyword Search        Vector Search
     │                     │
     └──────────┬──────────┘
                ▼
        Hybrid Search / RRF
                │
                ▼
        Semantic Reranking
                │
                ▼
        Relevant Chunks


                      RAG GENERATION

Relevant Chunks
      │
      ▼
Context Builder
      │
      ▼
Grounding Context
      │
      +
User Question
      │
      ▼
Azure OpenAI
      │
      ▼
Grounded Answer
      +
Source Information


                    CONVERSATIONAL RAG

User Question
      │
      +
Conversation History
      │
      ▼
Query Rewriting
      │
      ▼
Standalone Search Query
      │
      ▼
RAG Pipeline
      │
      ▼
Grounded Answer
      │
      ▼
Conversation Session
```

---

# Technology Stack

### Application

- Python
- Python virtual environments
- OpenAI Python SDK
- Azure SDK for Python

### Azure

- Microsoft Foundry / Azure OpenAI
- Azure AI Search
- Azure OpenAI embedding deployment
- Azure OpenAI chat deployment

### Retrieval

- Vector search
- HNSW
- Keyword search
- Hybrid retrieval
- Reciprocal Rank Fusion (RRF)
- Semantic ranking
- Metadata filtering

### Document Processing

- PyPDF
- Tiktoken
- Sentence-aware chunking
- Token-aware chunking
- Page-aware PDF processing

### Development

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
│   └── test_session_summary.py
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
│   │   └── uploader.py
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

# 1. Document Ingestion

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
Metadata
 ↓
Embedding
 ↓
Azure AI Search
```

The orchestration for this process is handled by:

```text
src/ingestion/pipeline.py
```

Individual modules remain responsible for specific operations such as loading, parsing, chunking and embedding.

---

# 2. Multi-Format Document Processing

The ingestion architecture currently supports:

- `.txt`
- `.pdf`

TXT documents are read directly.

PDF documents are processed page-by-page using PyPDF, allowing page information to be retained throughout the RAG pipeline.

The parser architecture is extensible so additional formats such as DOCX, HTML, JSON and CSV can be introduced later.

---

# 3. Page-Aware PDF Processing

PDF pages are retained separately inside the document model.

This allows chunks to preserve:

```text
file_name
page_number
chunk_index
```

For example:

```text
SOURCE: information-security-manual.pdf
PAGE: Page 147
CHUNK_ID: information-security-manual_pdf-381
```

This provides the foundation for page-level citations in generated answers.

Scanned and complex layout-heavy PDFs will later be handled through Azure AI Document Intelligence.

---

# 4. Token and Sentence-Aware Chunking

The original implementation used character-based chunking.

It has been upgraded to use:

- sentence boundaries
- token budgets
- sentence overlap
- page boundaries

Instead of arbitrarily producing:

```text
"artificial intelligence frame"
"l intelligence framework..."
```

the chunker attempts to retain complete sentences.

Tiktoken is used to estimate chunk size using tokens rather than raw character counts.

The current default strategy is approximately:

```text
300 token maximum chunk size
1 sentence overlap
```

More advanced structure-aware chunking will be introduced for large legislation, policies, manuals and other structured enterprise documents.

---

# 5. Enterprise Metadata

Each indexed chunk can contain metadata such as:

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

This metadata allows retrieval to be constrained to relevant knowledge domains.

The same platform can therefore eventually support:

```text
Enterprise RAG
│
├── IT / Cyber Security
├── Financial Services
└── Government
```

without creating three separate RAG applications.

---

# 6. Embeddings

Document chunks are converted into vector representations using an Azure OpenAI embedding deployment.

The current implementation uses:

```text
text-embedding-3-small
```

with:

```text
1536 dimensions
```

The same embedding process is used for user search queries so document and query vectors can be compared.

---

# 7. Azure AI Search Index

Azure AI Search stores both document content and vector representations.

Current index fields include:

| Field | Purpose |
|---|---|
| `chunk_id` | Unique chunk identifier |
| `content` | Searchable document content |
| `file_name` | Original source document |
| `chunk_index` | Position of the chunk |
| `page_number` | Original PDF page |
| `industry` | Industry/domain |
| `department` | Business department |
| `document_type` | Document category |
| `classification` | Information classification |
| `embedding` | Vector representation |

The index is configured for vector retrieval and semantic ranking.

---

# 8. Retrieval Strategies

Three retrieval strategies have been implemented and tested independently.

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

This retrieves text based on semantic similarity.

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

Hybrid search combines lexical matching with semantic vector similarity.

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

Semantic ranking adds an additional relevance-ranking stage over the hybrid candidate results.

---

# 9. Grounded RAG Generation

Retrieved chunks are passed through a context builder before being provided to the Azure OpenAI chat model.

```text
Question
   ↓
Retrieval
   ↓
Relevant Chunks
   ↓
Context Builder
   ↓
Grounded Prompt
   ↓
Azure OpenAI
   ↓
Answer
```

The model is instructed to use the retrieved knowledge-base context for factual claims rather than relying on outside knowledge.

If retrieval returns no authorised information, the pipeline stops and returns an insufficient-information response instead of asking the model to invent an answer.

---

# 10. Source Citations

Retrieved chunks retain structured source information:

```text
file_name
page_number
chunk_id
```

This allows answers to reference evidence such as:

```text
[SOURCE: policy.pdf, Page 17]
```

Structured source information is also returned separately from the generated answer for future UI and API use.

---

# 11. Conversational RAG

The project now supports multi-turn questions.

For example:

```text
User:
What is retrieval augmented generation?

Assistant:
...

User:
Why is it useful?
```

The second question does not contain enough context by itself.

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

may become:

```text
Why is retrieval augmented generation useful?
```

The rewritten query is then used for retrieval.

---

# 12. Conversation Sessions

Each conversation is represented by a `ConversationSession`.

Sessions currently contain:

```text
session_id
conversation history
conversation summary
```

A unique session ID allows conversations to remain logically separated.

The current implementation stores sessions in application memory.

A distributed store such as Redis or a database can replace this when the application is deployed across multiple instances.

---

# 13. Conversation Memory Management

Sending unlimited conversation history to an LLM would continually increase:

- token usage
- latency
- cost
- irrelevant context

The application therefore maintains a bounded recent history.

Older messages can be summarised into a compact conversation summary.

```text
Older Messages
      ↓
Summarisation
      ↓
Conversation Summary
      +
Recent Messages
      ↓
Future RAG Requests
```

This preserves useful conversational context without allowing raw history to grow indefinitely.

---

# 14. Conversation-Aware Generation

Conversation history is used in two places:

```text
Conversation History
      │
      ├───────────────┐
      ▼               ▼
Query Rewriting   Answer Generation
      │               ▲
      ▼               │
Retrieval ────────────┘
```

The history helps understand conversational intent.

However, conversation history is not treated as authoritative enterprise evidence. Factual answers must still be grounded in retrieved knowledge-base content.

---

# 15. Retrieval Diagnostics

The RAG orchestrator exposes diagnostic information alongside responses.

Current diagnostics include:

```text
session_id
original question
rewritten search query
retrieved chunk IDs
source documents
page numbers
search scores
semantic reranker scores
```

This helps isolate failures.

For example:

```text
Incorrect Answer
      ↓
Was the rewritten query wrong?
      ↓
Was the wrong document retrieved?
      ↓
Was ranking poor?
      ↓
Was good context retrieved but generation wrong?
```

This separation is important for debugging production RAG systems.

---

# Key Learnings

Building the system from individual components has demonstrated several important concepts:

- RAG consists of separate ingestion, retrieval, augmentation and generation stages.
- Embeddings represent semantic meaning and enable vector retrieval.
- Query and document embeddings must use compatible dimensions.
- Chunking strategy directly affects retrieval quality.
- Token-aware chunking is more appropriate for LLM systems than arbitrary character boundaries.
- Page metadata is important for traceability and citations.
- Azure AI Search document keys have formatting restrictions.
- Vector retrieval alone is not always sufficient.
- Hybrid retrieval combines lexical and semantic matching.
- Semantic ranking is a reranking stage rather than another embedding search.
- Metadata filters allow knowledge domains to be separated.
- Conversation memory and enterprise knowledge are different concepts.
- Query rewriting helps conversational questions become useful retrieval queries.
- Conversation history should be bounded or summarised.
- Retrieval diagnostics make incorrect RAG responses much easier to investigate.
- Components should remain separated so failures can be isolated instead of treating the entire system as a single "AI" component.

---

# Development Progress

## Completed

- [x] Python project foundation
- [x] Environment-based configuration
- [x] Application logging
- [x] Document models
- [x] TXT ingestion
- [x] PDF parsing
- [x] Page-aware PDF processing
- [x] Sentence-aware chunking
- [x] Token-aware chunking
- [x] Chunk overlap
- [x] Enterprise metadata
- [x] Multi-industry ingestion architecture
- [x] Azure OpenAI embeddings
- [x] Azure AI Search vector index
- [x] HNSW vector search
- [x] Metadata-filtered retrieval
- [x] Hybrid search
- [x] Semantic ranking
- [x] RAG orchestration
- [x] Grounded answer generation
- [x] Source metadata and citations
- [x] Query rewriting
- [x] Multi-turn conversational RAG
- [x] Conversation sessions
- [x] Conversation history management
- [x] Conversation summarisation
- [x] Conversation-aware generation
- [x] Retrieval diagnostics

## Planned

- [ ] Microsoft Entra ID integration
- [ ] User and group authorization context
- [ ] Document-level access control
- [ ] Security-filtered retrieval
- [ ] Classification enforcement
- [ ] Prompt injection defenses
- [ ] Input/output guardrails
- [ ] Azure AI Content Safety integration
- [ ] Real multi-industry document corpus
- [ ] Azure AI Document Intelligence
- [ ] Structure-aware document chunking
- [ ] RAG evaluation framework
- [ ] Retrieval quality metrics
- [ ] Groundedness evaluation
- [ ] Observability and distributed tracing
- [ ] OpenTelemetry
- [ ] Application Insights
- [ ] REST API
- [ ] Web application
- [ ] Persistent/distributed conversation storage
- [ ] Infrastructure as Code
- [ ] Automated testing
- [ ] CI/CD
- [ ] DEV / TEST / PROD environments
- [ ] Managed identities
- [ ] Azure Key Vault
- [ ] Private networking
- [ ] Production deployment

---

# Security Direction

The current development environment uses local environment variables for Azure credentials.

Real secrets are stored in:

```text
.env
```

and `.env` must not be committed to source control.

The repository contains:

```text
.env.example
```

to document required configuration without exposing credentials.

The production architecture will progressively replace development credentials with:

```text
Microsoft Entra ID
        ↓
Managed Identity
        ↓
Azure RBAC
        ↓
Application Authorization
        ↓
Document-Level Access Control
        ↓
Security-Filtered Retrieval
```

Additional guardrails, content safety, secret management and network isolation will be added as the architecture progresses.

---

# Real-World Knowledge Corpus

The project is designed to eventually ingest large public industry documents rather than relying only on artificial sample data.

Planned domains include:

### IT / Cyber Security

Public cybersecurity standards, controls, manuals and operational guidance.

### Financial Services

Public financial regulation, legislation and operational-risk guidance.

### Government

Public legislation, policies, standards and administrative guidance.

Large source documents will generally not be committed directly to this repository. The repository will instead document their official sources and provide ingestion instructions where appropriate.

This keeps the repository focused on the RAG platform rather than storing large third-party document collections.

---

# Git Development Milestones

The project is intentionally being developed through capability-based commits.

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

Next
Enterprise identity and document-level authorization
```

This approach keeps architectural changes isolated and makes the development history useful for understanding how the system evolved.

---

# Current System

The application now implements an end-to-end conversational RAG flow:

```text
                    USER
                      │
                      ▼
              Conversation Session
                      │
                      ▼
                Query Rewriting
                      │
                      ▼
             Standalone Search Query
                      │
              ┌───────┴───────┐
              ▼               ▼
          Keyword          Vector
           Search           Search
              │               │
              └───────┬───────┘
                      ▼
                     RRF
                      │
                      ▼
              Semantic Ranking
                      │
                      ▼
              Relevant Chunks
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
             ┌────────┴────────┐
             ▼                 ▼
          Sources       Retrieval Trace
             │
             └────────┬────────┘
                      ▼
             Conversation Memory
```

The next development phase moves from **functional enterprise RAG** toward **secured enterprise RAG** by introducing identity, authorization context and document-level access controls.
# Azure Enterprise Multi-Industry RAG

A production-oriented Retrieval-Augmented Generation (RAG) platform built from scratch using **Python, Azure OpenAI, and Azure AI Search**.

The goal of this project is to understand how an enterprise RAG system is designed, built, secured, tested, and deployed rather than relying on a pre-built RAG framework.

The architecture is designed to eventually support multiple industry knowledge domains while maintaining clear boundaries for retrieval, security, access control, evaluation, and observability.

---

## Reference Architecture

This project is implemented independently from scratch for learning and portfolio purposes.

Microsoft's **Azure Search OpenAI Demo** is being used as a reference architecture to understand production RAG patterns and compare architectural decisions.

Reference:

https://github.com/Azure-Samples/azure-search-openai-demo

The Microsoft repository itself is not included in this repository.

---

## Current Architecture

The system currently implements the ingestion and retrieval portions of the RAG architecture.

```text
                        DOCUMENT INGESTION

Document
   │
   ▼
Loader
   │
   ▼
Parser
   │
   ▼
Document Model
   │
   ▼
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
   ├─────────────────────────┐
   │                         │
   ▼                         ▼
Keyword Search        Query Embedding
                             │
                             ▼
                       Vector Search
   │                         │
   └────────────┬────────────┘
                │
                ▼
       Hybrid Search / RRF
                │
                ▼
        Semantic Reranking
                │
                ▼
      Top Relevant Chunks
```

The next stage will connect these retrieved chunks to an Azure OpenAI chat model to produce grounded answers with citations.

---

## Technology Stack

- Python
- Microsoft Foundry / Azure OpenAI
- Azure AI Search
- OpenAI Python SDK
- Azure Search Documents SDK
- Git / GitHub
- PowerShell
- Python virtual environments

### Azure AI

Currently using:

- `text-embedding-3-small`
- 1536-dimensional embeddings
- Azure AI Search vector indexing
- HNSW vector search
- Hybrid search
- Semantic ranking

---

## Project Structure

```text
multi-industry-rag/
│
├── src/
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── parser.py
│   │   ├── models.py
│   │   ├── chunker.py
│   │   ├── metadata.py
│   │   └── embeddings.py
│   │
│   ├── retrieval/
│   │   └── vector_search.py
│   │
│   ├── search/
│   │   ├── index_schema.py
│   │   └── uploader.py
│   │
│   └── main.py
│
├── scripts/
│   ├── test_ingestion.py
│   └── test_vector_search.py
│
├── data/
│   └── sample.txt
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Each package has a specific responsibility so failures can be isolated and debugged without treating the RAG application as one large block of code.

---

## Document Ingestion Pipeline

Documents currently move through the following stages:

### 1. Loading

The loader validates the supplied file path and reads the document content.

### 2. Parsing

Raw content is converted into a consistent internal `Document` model.

### 3. Chunking

Documents are divided into smaller overlapping chunks that can be independently retrieved.

The current implementation uses character-based chunking. More advanced token and structure-aware chunking will be introduced later.

### 4. Metadata Enrichment

Chunks contain enterprise metadata such as:

```text
industry
department
document_type
classification
```

This allows retrieval to be restricted to appropriate business domains.

### 5. Embeddings

Chunk content is sent to Azure OpenAI and converted into numerical vector representations.

### 6. Indexing

The chunks, metadata, text, and embeddings are uploaded into Azure AI Search.

---

## Azure AI Search Index

The current index contains:

| Field | Purpose |
|---|---|
| `chunk_id` | Unique Azure Search document key |
| `content` | Searchable chunk text |
| `file_name` | Original source document |
| `chunk_index` | Position within the source document |
| `industry` | Industry/domain identifier |
| `department` | Business department |
| `document_type` | Document category |
| `classification` | Information classification |
| `embedding` | Vector representation of the content |

The embedding field currently contains **1536-dimensional vectors** generated using `text-embedding-3-small`.

---

## Retrieval Strategies

Three retrieval approaches have been implemented so they can be compared independently.

### Vector Search

The user question is converted into an embedding and compared against stored document vectors.

```text
Question
   ↓
Embedding
   ↓
Vector similarity
   ↓
Relevant chunks
```

### Hybrid Search

Combines traditional keyword search with vector similarity.

```text
Keyword Search
      +
Vector Search
      ↓
     RRF
      ↓
Combined Ranking
```

### Semantic Hybrid Search

Adds semantic reranking after hybrid retrieval.

```text
Keyword Search
      +
Vector Search
      ↓
     RRF
      ↓
Semantic Reranker
      ↓
Final Results
```

---

## Multi-Industry Design

The long-term architecture is intended to support multiple knowledge domains using shared RAG infrastructure.

For example:

```text
Enterprise RAG
│
├── IT Support
│
├── Financial Services
│
└── Government
```

Metadata filtering allows queries to retrieve information from the appropriate domain instead of searching every document indiscriminately.

This also establishes the foundation for later document-level authorization and security filtering.

---

## Key Learnings So Far

Building the pipeline from scratch has demonstrated several important RAG concepts:

- A RAG system consists of separate **ingestion, indexing, retrieval, and generation** stages.
- Documents need to be normalized before downstream processing.
- Chunk size and overlap directly affect retrieval behaviour.
- Embeddings represent semantic meaning as vectors.
- Query embeddings and document embeddings must use compatible models and dimensions.
- Azure AI Search document keys have specific formatting restrictions.
- Vector similarity alone is not always sufficient for enterprise retrieval.
- Metadata can restrict retrieval to specific industries or departments.
- Hybrid search combines lexical and semantic retrieval.
- Semantic ranking is a separate reranking stage rather than another embedding search.
- Clear boundaries between components make integration failures significantly easier to diagnose.

---

## Development Progress

### Completed

- [x] Python project foundation
- [x] Environment configuration
- [x] Application logging
- [x] Document loading
- [x] Document parsing
- [x] Document and Chunk models
- [x] Document chunking
- [x] Enterprise metadata
- [x] Azure OpenAI embedding integration
- [x] Azure AI Search index
- [x] Vector document indexing
- [x] Vector retrieval
- [x] Metadata-filtered retrieval
- [x] Hybrid retrieval
- [x] Semantic ranking

### Next

- [x] RAG orchestration
- [x] Azure OpenAI answer generation
- [x] Grounded responses
- [x] Basic source citations
- [x] PDF parsing
- [x] Page-aware chunking
- [x] Page metadata
- [x] Page-aware source citations
- [x] Generic multi-industry ingestion pipeline
- [x] Token-aware chunking
- [x] Sentence-aware chunk boundaries
- [x] Sentence overlap
- [ ] Real multi-industry document sets
- [ ] Improved document parsing
- [ ] Authentication and authorization
- [ ] Document-level access control
- [ ] Guardrails
- [ ] Evaluation framework
- [ ] Observability and tracing
- [ ] API layer
- [ ] Web application
- [ ] Infrastructure as Code
- [ ] CI/CD
- [ ] DEV / TEST / PROD environments
- [ ] Production security and networking

---

## Security Direction

The current DEV environment uses environment variables for service credentials.

Real credentials are stored in:

```text
.env
```

and `.env` is excluded from Git.

The production architecture will progressively introduce:

- Microsoft Entra ID
- Managed identities
- Azure RBAC
- Least-privilege service access
- Document-level authorization
- Secure secret management
- Network isolation
- Application guardrails

Security will be implemented as part of the architecture rather than added only after the RAG functionality is complete.

---

## Git Development Approach

The repository is being developed through capability-based commits.

```text
Commit 1
Project foundation

Commit 2
Document ingestion and metadata pipeline

Commit 3
Vector and hybrid retrieval with metadata filters

Commit 4
Semantic ranking

Future commits
RAG generation → citations → security → evaluation
→ observability → API → deployment
```

This keeps each architectural change isolated and makes the evolution of the RAG platform easy to follow.

---

## Current Status

The project currently has a functioning **ingestion → embedding → indexing → retrieval** pipeline.

The next milestone is to connect semantic hybrid retrieval to an Azure OpenAI chat model:

```text
User Question
      ↓
Semantic Hybrid Retrieval
      ↓
Relevant Enterprise Context
      ↓
Azure OpenAI
      ↓
Grounded Answer
      ↓
Source Citations
```

This will complete the first end-to-end RAG flow before additional enterprise security, evaluation, observability, and deployment capabilities are introduced.
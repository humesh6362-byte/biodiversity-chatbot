Yes — here is the **entire updated `README.md` as one single file**. Copy everything below and replace your current `README.md`.

````markdown
# Darukaa.Earth — AI Biodiversity Intelligence Chatbot

A RAG-grounded conversational AI system that helps users describe real-world land and ecosystem problems, asks clarifying questions for missing environmental variables, retrieves relevant knowledge from a local vector database, and provides evidence-backed, multi-metric recommendations.

The current system works **without an OpenAI API key** by using local embeddings and a locally running LLM.

---

## Architecture

```text
                         ┌──────────────────────────┐
                         │      User / Frontend      │
                         │   Natural-language text   │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   FastAPI /api/chat      │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │          extractor.py              │
                    │   Local rule-based extraction      │
                    │                                    │
                    │ Soil / rainfall / crop / land     │
                    │ use / pollution / deforestation   │
                    └─────────────────┬─────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │           session.py                │
                    │                                     │
                    │ Per-session environmental slots    │
                    │ + conversation history             │
                    └─────────────────┬─────────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │        engine.py         │
                         │                          │
                         │ < 3 variables           │
                         │       ↓                  │
                         │ Clarifying question      │
                         │                          │
                         │ >= 3 variables          │
                         │       ↓                  │
                         │ RAG retrieval            │
                         │       ↓                  │
                         │ Local LLM generation     │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │         retriever.py                │
                    │                                     │
                    │ Sentence Transformers embeddings   │
                    │ + ChromaDB similarity retrieval    │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │        ChromaDB          │
                         │ Persistent local vector  │
                         │ database / knowledge     │
                         └──────────────────────────┘
````

---

## Key Features

* RAG-based environmental knowledge retrieval
* Local AI pipeline
* No OpenAI API key required
* Sentence Transformers embeddings
* ChromaDB vector database
* Ollama local LLM
* Multi-turn conversational memory
* Environmental variable extraction
* Clarifying questions
* Multi-metric environmental reasoning
* Evidence/source display
* Structured recommendations
* Soil-health analysis
* Rainfall and climate analysis
* Land-use analysis
* Biodiversity analysis
* Pollution analysis
* Deforestation analysis
* Optional geographical fields
* FastAPI backend
* Web-based frontend

---

# 1. Local AI Pipeline

The current project does not require an OpenAI API key.

## Local Embedding Model

The project uses:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

This model converts knowledge documents and user queries into numerical
embeddings that can be compared for semantic similarity.

## Local LLM

The chatbot uses:

```text
Ollama
llama3.2:3b
```

The LLM runs locally through Ollama.

The architecture is therefore:

```text
User Message
     ↓
Environmental Variable Extraction
     ↓
Sentence Transformer Embedding
     ↓
ChromaDB Retrieval
     ↓
Relevant Knowledge
     ↓
Ollama llama3.2:3b
     ↓
Structured Recommendation
```

---

# 2. RAG Knowledge System

The project contains a local environmental knowledge base under:

```text
knowledge/
```

The knowledge covers areas including:

* Soil health
* Land use
* Biodiversity indicators
* Climate factors
* Human environmental impact

The system uses a Retrieval-Augmented Generation approach.

Instead of relying only on the language model, the chatbot retrieves relevant
knowledge before generating recommendations.

---

# 3. Knowledge Ingestion

Knowledge ingestion is implemented in:

```text
app/knowledge/ingest.py
```

The ingestion process is:

```text
Knowledge documents
        ↓
Text chunks
        ↓
Sentence Transformer embeddings
        ↓
ChromaDB
        ↓
Persistent local vector database
```

The embeddings are generated locally using:

```text
all-MiniLM-L6-v2
```

No OpenAI embedding API is required.

The knowledge index can be generated using:

```powershell
python scripts/ingest_knowledge.py
```

---

# 4. Retrieval

The retrieval system is implemented in:

```text
app/knowledge/retriever.py
```

The system takes the user's question and known environmental variables,
creates an embedding, and searches ChromaDB for relevant knowledge.

Retrieved information includes:

```text
Knowledge text
Domain
Source
Similarity / relevance
```

The retrieved sources are displayed in the chatbot response.

This makes the RAG process visible to the user.

---

# 5. Environmental Variable Extraction

The current implementation uses local rule-based extraction in:

```text
app/chat/extractor.py
```

The extractor can identify variables such as:

```text
Soil organic carbon
Soil pH
Rainfall
Temperature
Crop
Land use
Pollution
Deforestation
Region
```

For example:

```text
My farm is in a semi-arid region and rainfall is low.
```

The system can extract:

```text
rainfall = low
region = semi-arid
```

Another example:

```text
The soil organic carbon is 0.3% and I grow wheat using monoculture.
```

The system can extract:

```text
soil_organic_carbon_pct = 0.3
crop = wheat
land_use_type = monoculture
```

These variables are stored and combined with information from previous
conversation turns.

---

# 6. Conversational Intelligence

The chatbot supports multi-turn conversations.

The system does not immediately generate a recommendation when insufficient
environmental information is available.

Instead, it checks the number of known environmental variables.

If fewer than 3 relevant variables are available, the chatbot asks a
clarifying question.

Example:

```text
User:
Biodiversity is declining on my land.

Assistant:
I have 0 environmental variable(s) so far. To give you a grounded,
multi-metric recommendation, could you also share:

- soil organic carbon
- rainfall pattern
- current land use / crop type
```

The user can then provide additional information.

---

# 7. Multi-Turn Memory

Conversation state is maintained using:

```text
app/chat/session.py
```

The current implementation stores:

```text
session_id
conversation history
environmental variables
```

For example:

### Turn 1

```text
Biodiversity is declining on my land.
```

### Turn 2

```text
My farm is in a semi-arid region and rainfall is low.
```

### Turn 3

```text
The soil organic carbon is 0.3% and I grow wheat using monoculture.
```

The system combines the information from the conversation.

The resulting environmental context can include:

```text
Region: semi-arid
Rainfall: low
Soil organic carbon: 0.3%
Crop: wheat
Land use: monoculture
```

The current implementation uses in-memory session storage.

For production, this could be replaced with Redis or a database.

---

# 8. Clarifying Questions

The chatbot requires sufficient environmental information before producing
grounded recommendations.

The current system uses a minimum threshold of 3 relevant environmental
variables.

The purpose is to reduce generic responses and encourage multi-variable
reasoning.

Example:

```text
Biodiversity is declining.
```

Instead of immediately guessing, the chatbot asks for information such as:

```text
Soil organic carbon
Rainfall
Land use
Crop
```

---

# 9. Multi-Metric Environmental Reasoning

The system is designed to connect multiple environmental variables.

Examples include:

```text
Soil health ↔ Biodiversity

Rainfall ↔ Soil moisture ↔ Species survival

Land use ↔ Habitat diversity

Agriculture ↔ Soil health

Pollution ↔ Biodiversity

Deforestation ↔ Habitat loss

Climate ↔ Ecosystem resilience
```

The system therefore attempts to provide recommendations that affect more than
one environmental metric.

---

# 10. Recommendation Output

Recommendations can contain:

```text
Action
Reasoning
Impacted metrics
Estimated improvement
Time horizon
Confidence
Reference
```

Example structure:

```json
{
  "action": "Introduce legume-based cover crops",
  "reasoning": "Cover crops can improve soil organic carbon and support biodiversity.",
  "impacted_metrics": [
    "soil organic carbon",
    "biodiversity"
  ],
  "estimated_improvement": "15-25%",
  "time_horizon": "medium",
  "confidence": "medium",
  "reference": "FAO conservation agriculture studies; USDA-NRCS"
}
```

---

# 11. Example End-to-End Demonstration

The following conversation demonstrates the main functionality.

## Message 1

```text
Biodiversity is declining on my land.
```

The system asks for additional environmental variables.

## Message 2

```text
My farm is in a semi-arid region and rainfall is low.
```

The system identifies:

```text
Rainfall: low
Region: semi-arid
```

The system still asks for additional variables because more information is
required.

## Message 3

```text
The soil organic carbon is 0.3% and I grow wheat using monoculture.
```

The system identifies:

```text
Soil organic carbon: 0.3%
Rainfall: low
Crop: wheat
Land use: monoculture
Region: semi-arid
```

The system then retrieves relevant knowledge and generates recommendations.

Example recommendations can include:

```text
1. Introduce legume-based cover crops

2. Integrate trees with wheat / agroforestry
```

The response also provides:

```text
Impacted metrics
Estimated improvement
Time horizon
Confidence
Retrieved knowledge sources
```

---

# 12. Input Handling

## Free-Text Input

The main API accepts natural-language messages.

Example:

```json
{
  "session_id": "demo-1",
  "message": "My farm has low rainfall and I grow wheat using monoculture."
}
```

## Structured Input

The API can also accept structured environmental information.

The schema is defined in:

```text
app/models.py
```

Supported fields include:

```text
soil_organic_carbon_pct
soil_ph
rainfall
land_use_type
crop
region
temperature
pollution_level
deforestation_rate
lat
lon
```

Structured values can be combined with information extracted from free text.

---

# 13. Project Structure

```text
darukaa-chatbot/
│
├── app/
│   ├── chat/
│   │   ├── engine.py
│   │   ├── extractor.py
│   │   └── session.py
│   │
│   ├── knowledge/
│   │   ├── ingest.py
│   │   └── retriever.py
│   │
│   ├── routers/
│   │   └── chat.py
│   │
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── models.py
│
├── chroma_db/
│
├── frontend/
│   └── index.html
│
├── knowledge/
│   └── *.md
│
├── scripts/
│   └── ingest_knowledge.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 14. Technology Stack

## Backend

```text
Python
FastAPI
Uvicorn
Pydantic
```

## AI / Machine Learning

```text
Sentence Transformers
all-MiniLM-L6-v2
Ollama
llama3.2:3b
```

## RAG / Vector Database

```text
ChromaDB
Local embeddings
Semantic similarity search
```

## Frontend

```text
HTML
CSS
JavaScript
```

## Development

```text
Visual Studio Code
Python virtual environment
Git / GitHub
```

---

# 15. Local Setup

## Step 1 — Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
```

## Step 2 — Activate Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

## Step 3 — Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 4 — Start Ollama

Make sure Ollama is installed and running.

Pull the local model:

```powershell
ollama pull llama3.2:3b
```

The chatbot uses this model locally.

## Step 5 — Build Knowledge Index

Run:

```powershell
python scripts/ingest_knowledge.py
```

This creates the local ChromaDB knowledge index.

## Step 6 — Start Backend

Run:

```powershell
uvicorn app.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Step 7 — Start Frontend

Open another terminal:

```powershell
python -m http.server 5500 --directory frontend
```

Open:

```text
http://localhost:5500
```

---

# 16. API

Main endpoint:

```text
POST /api/chat
```

Example:

```json
{
  "session_id": "demo-1",
  "message": "Biodiversity is declining on my land."
}
```

The same `session_id` should be used for multiple messages when demonstrating
multi-turn memory.

---

# 17. Testing

Tests are located in:

```text
tests/
```

Run:

```powershell
pytest -q
```

The tests can cover:

* Environmental variable extraction
* Clarifying questions
* Multi-turn behavior
* Sufficient-variable recommendation flow
* Recommendation generation
* Retrieval behavior

---

# 18. Current Implementation Status

The current prototype successfully demonstrates:

* Local AI processing
* No OpenAI API dependency
* Local embeddings
* ChromaDB vector retrieval
* RAG-based recommendations
* Rule-based environmental variable extraction
* Multi-turn conversation
* Clarifying questions
* Environmental variable accumulation
* Multi-metric reasoning
* Retrieved source display
* Structured recommendation output
* FastAPI backend
* Web-based frontend
* Local knowledge indexing

---

# 19. Hackathon Demo Flow

The recommended live demonstration is:

```text
User describes biodiversity problem
              ↓
System checks environmental information
              ↓
Missing information detected
              ↓
Clarifying question
              ↓
User provides environmental variables
              ↓
Variables stored in session
              ↓
At least 3 variables available
              ↓
ChromaDB retrieves relevant knowledge
              ↓
Local LLM processes retrieved context
              ↓
Multi-metric recommendation
              ↓
Sources + metrics + time horizon + confidence
```

---

# 20. Example Demo

Use these messages during the demonstration:

### Message 1

```text
Biodiversity is declining on my land.
```

### Message 2

```text
My farm is in a semi-arid region and rainfall is low.
```

### Message 3

```text
The soil organic carbon is 0.3% and I grow wheat using monoculture.
```

The final response should demonstrate the complete pipeline:

```text
Problem
   ↓
Clarification
   ↓
Environmental extraction
   ↓
Session memory
   ↓
RAG retrieval
   ↓
Local LLM
   ↓
Evidence-backed recommendation
```

---

# 21. Limitations

## In-Memory Sessions

The current session system is stored in memory.

Therefore, conversation state is lost when the backend process restarts.

A production implementation could use:

```text
Redis
PostgreSQL
MongoDB
```

for persistent conversation storage.

## Rule-Based Extraction

The current extractor uses local rules and regular expressions.

It may not recognize every possible natural-language expression.

For example, users may describe environmental conditions in many different
ways.

A production version could use:

```text
NER model
Information extraction model
Few-shot classifier
Hybrid rule + ML extraction
```

## Local LLM

The quality of generated recommendations depends on the selected local model
and available hardware.

A larger local model could be used when more computational resources are
available.

## Knowledge Base

The current knowledge base is curated for the hackathon prototype.

A production system could ingest:

```text
Research papers
Government reports
Scientific datasets
Environmental reports
Agricultural datasets
Satellite data
Geospatial datasets
```

---

# 22. Future Improvements

Potential improvements include:

```text
Persistent conversation storage
        ↓
Larger environmental knowledge corpus
        ↓
Research paper / PDF ingestion
        ↓
Improved information extraction
        ↓
Geospatial intelligence
        ↓
Satellite imagery
        ↓
Remote sensing data
        ↓
Real-time weather information
        ↓
Environmental datasets
        ↓
Citation verification
        ↓
Improved evaluation
        ↓
Cloud deployment
```

---

# 23. Production Architecture

A future production version could use:

```text
                    Web / Mobile Client
                            │
                            ▼
                       FastAPI API
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       Conversation DB              RAG Pipeline
       Redis / PostgreSQL                │
                                         ▼
                                Vector Database
                                         │
                                         ▼
                               Environmental Data
                                         │
                                         ▼
                                  Local / Cloud LLM
```

---

# 24. Design Philosophy

The project is designed around the following workflow:

```text
ASK
 ↓
UNDERSTAND
 ↓
RETRIEVE
 ↓
REASON
 ↓
RECOMMEND
 ↓
SHOW EVIDENCE
```

The chatbot does not simply respond with generic environmental advice.

It first identifies missing information, collects environmental variables
through conversation, retrieves relevant knowledge, and then produces
recommendations based on multiple environmental factors.

---

# 25. Project Goal

The goal of **Darukaa.Earth — AI Biodiversity Intelligence** is to provide a
conversational system for understanding relationships between:

```text
Soil Health
     ↕
Climate
     ↕
Water
     ↕
Land Use
     ↕
Biodiversity
     ↕
Human Environmental Impact
```

The project demonstrates how conversational AI, local embeddings, vector
databases, retrieval-augmented generation, and structured environmental
reasoning can be combined to support practical ecosystem intelligence.

---

## Built for the Darukaa.Earth AI Biodiversity Intelligence Challenge

**Core technologies:**

```text
Python + FastAPI
Sentence Transformers
ChromaDB
Ollama
llama3.2:3b
HTML/CSS/JavaScript
RAG
Multi-turn conversational reasoning
```

**No OpenAI API key is required for the current implementation.**

```
```

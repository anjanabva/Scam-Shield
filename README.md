# Scam Shield - AI-Powered Digital Fraud Detection 🛡️

Scam Shield (formerly known as Citizen Fraud Shield) is an intelligent, real-time web application designed to protect users from digital scams, fraud, and digital arrest schemes. By simply pasting suspicious messages, emails, or chat transcripts into the app, users receive an instant verdict on whether the communication is a scam, along with a detailed explanation, confidence score, and specific red flags identified in the text. 

The application doesn't stop at classification; it features an interactive AI assistant that allows users to ask follow-up questions, get guidance on what to do next, and view live, trending scam campaigns happening in the community. 

Under the hood, Scam Shield leverages cutting-edge LLMs (OpenAI), RAG (Retrieval-Augmented Generation) for up-to-date scam knowledge, and a vector database (Pinecone) to cluster cross-user submissions and identify emerging fraud campaigns in real time.

---

## 🏗️ Architecture

The system uses a modern client-server architecture with heavy reliance on external AI and vector database services for intelligence.

```mermaid
graph TD
    subgraph Frontend [Frontend - React + Vite]
        UI[User Interface]
        Chat[Chat Interface]
        Dashboard[Trending Campaigns Dashboard]
        UI <--> Chat
        UI <--> Dashboard
    end

    subgraph Backend [Backend - FastAPI]
        API[API Router]
        Detection[Scam Detection Engine]
        Intelligence[Threat Intelligence & Clustering]
        RAG[RAG Engine]
        LLM_Client[LLM Client]
        
        API --> Detection
        API --> Intelligence
        API --> RAG
        Detection --> LLM_Client
        Detection --> RAG
    end

    subgraph External Services
        OpenAI[OpenAI / LLM API]
        Pinecone[(Pinecone Vector DB)]
    end

    Frontend -- HTTP/REST --> API
    Frontend -- Server-Sent Events --> API
    
    LLM_Client -- API Calls --> OpenAI
    Intelligence -- Embeddings / Query --> Pinecone
    RAG -- Vector Search --> Pinecone
```

---

## ✨ Features

- **Real-Time Scam Analysis**: Paste any text and get an immediate classification (Scam, Suspicious, or Safe) along with actionable advice.
- **Interactive Chat Assistant**: Have a conversation with the AI about the scam. Ask follow-up questions like "Should I block this number?" or "What if I already clicked the link?".
- **Threat Intelligence (Trending Campaigns)**: Aggregates and clusters anonymous submissions in real-time using Vector DB embeddings to warn users about emerging, widespread scams.
- **RAG-Powered Knowledge**: Utilizes Retrieval-Augmented Generation to reference a database of known scam tactics and historical fraud data, ensuring highly accurate verdicts.
- **Beautiful & Modern UI**: A sleek, dark-themed, glassmorphism interface built with React and Tailwind CSS.

---

## 💻 Tech Stack

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS v4
- **Architecture**: Component-based UI with interactive chat and real-time trending updates.

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM Integration**: OpenAI API
- **Vector Database**: Pinecone (for RAG and Campaign Clustering)
- **Data Validation**: Pydantic

---

## 📂 Folder Structure

```text
scam-shield/
├── backend/
│   ├── .env.example
│   ├── api/
│   │   └── routes.py
│   ├── config.py
│   ├── data/
│   │   └── scam_corpus.json
│   ├── detection/
│   │   ├── classifier.py
│   │   ├── prompts.py
│   │   └── rules.py
│   ├── intelligence/
│   │   ├── campaign_log.py
│   │   └── clustering.py
│   ├── llm/
│   │   └── openai_client.py
│   ├── main.py
│   ├── rag/
│   │   ├── ingest.py
│   │   └── vectorstore.py
│   ├── requirements.txt
│   └── tests/
│       ├── test_campaign_log.py
│       ├── test_classifier.py
│       ├── test_clustering.py
│       ├── test_openai_client.py
│       ├── test_pinecone.py
│       └── test_rules.py
├── frontend/
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── components/
│   │   │   ├── ActionButtons.jsx
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── TrendingPanel.jsx
│   │   │   └── VerdictCard.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   └── vite.config.js
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API Key
- Pinecone API Key

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd scam-shield
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

Set up your environment variables by creating a `.env` file in the `backend/` directory:
```env
# Example .env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
# Add any other required environment variables
```

Run the FastAPI server:
```bash
uvicorn main:app --reload
# Server will start at http://0.0.0.0:8000
```

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
# The UI will be accessible at http://localhost:5173
```


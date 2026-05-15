# Blinders: Neuro-Symbolic Governance for Autonomous Agents

Blinders is a governance layer designed to provide safety guardrails for autonomous AI agents within a Fantasy Football Premier League ecosystem. It utilizes a neuro-symbolic architecture that combines the natural language reasoning of Large Language Models (LLMs) with the formal logic and strict enforcement of a symbolic AtomSpace.

## System Overview

The system operates on a five-step pipeline to ensure every agent intent is verified against a formal constitution before execution:

1.  **AtomSpace Engine:** A persistent knowledge graph built on Hyperon MeTTa that serves as the "Source of Truth" for league rules, player data, and user permissions.
2.  **Intent Interpreter:** Utilizes Google Gemini 1.5 Pro to extract structured plans from natural language requests.
3.  **Symbolic Verifier:** Performs recursive proof checking within the AtomSpace to ensure the plan adheres to constitutional laws (e.g., budget integrity, role-based access control).
4.  **Decision Guardrail:** Intercepts any unauthorized actions and provides a detailed symbolic trace for audit purposes.
5.  **Tool Executor:** Persists authorized state changes directly back into the AtomSpace and triggers external management tools.

## Architecture

### Backend
- **Framework:** FastAPI
- **Reasoning Engine:** Google Gemini 2.5 Flash (via LangChain)
- **Symbolic Logic:** Hyperon MeTTa (Custom Pure-Python Interpreter)
- **State Management:** MeTTa AtomSpace

### Frontend
- **Framework:** Next.js 16 (React)
- **Styling:** Vanilla CSS with Tailwind CSS for layout
- **Components:** Custom "Lucide" inspired components for a high-end management dashboard

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Blinders
   ```

2. Setup the server:
   ```bash
   cd server
   pip install -r requirements.txt
   ```

3. Setup the client:
   ```bash
   cd ../client
   npm install
   ```

4. Configure Environment:
   Create a `.env` file in the `server` directory with your `GOOGLE_API_KEY`.

### Running the System

Start the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

Start the Next.js frontend:
```bash
npm run dev
```

## Constitutional Laws

The system currently enforces the following symbolic laws:
- **L1 (Authorization):** Role-based permission checks (Manager, Coach, Staff, Guest).
- **L4 (Budget):** Real-time tracking of squad value vs. bank balance.
- **L5 (Squad Size):** Enforcement of exactly 15 players per team.
- **L6 (Club Quota):** Maximum of 3 players from any single club.

## License

This project is proprietary and intended for research and demonstration purposes in the field of AI Safety and Neuro-Symbolic Integration.

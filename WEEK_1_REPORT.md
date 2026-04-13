# Week 1 Technical Report — Veriable AI Agent Development

## Overview
This week focused on building the professional foundation for AI agent development at Veriable. We moved from a simple "Hello World" to a persistence-enabled, multi-agent system capable of handling complex client intake and market research.

---

## 📂 Architecture Overview

### 1. Core Research Engine (`main.py`)
This is the "Think Tank" built on **CrewAI**.
*   **Multi-Agent Orchestration**: Separate agents for "Research" and "Writing".
*   **Multi-Model Strategy**: Uses `llama-3.3-70b-versatile` for high-reasoning research and `llama-3.1-8b-instant` for concise writing to optimize speed.
*   **External Intelligence**: Integrated with **Serper.dev** for real-time web access.

### 2. Business Intake Layer (`veriable_agent.py`)
A specialized interactive agent focused on the Veriable sales funnel.
*   **Stateful Interaction**: Implements a "Clarify once, then Solve" logic.
*   **Automated Scoping**: Categorizes projects into Basic, Standard, or Premium tiers automatically.

### 3. Data Infrastructure (`.env` & Supabase)
*   **Persistent Memory**: Uses a Supabase PostgreSQL backend to store `session_id` and message history.
*   **Context Retrieval**: The system reads past interactions *before* starting a new task, ensuring continuity.

---

## ✅ What the Agent Does Well
*   **Context Awareness**: Successfully pulls historical data from Supabase to inform current tasks.
*   **Resource Management**: Efficiently routes tasks to different LLM models based on complexity.
*   **Constraint Following**: The Intake agent strictly adheres to the "one round of questions" rule to prevent user fatigue.

## ⚠️ Known Limitations
*   **Primitive Loop Detection**: The session controller relies on simple character detection (`?`) which can occasionally misinterpret rhetorical questions.
*   **Linear Memory**: Memory is currently stored as a flat list; it does not yet perform vector-based "semantic search" for long-term knowledge pieces.
*   **Standardized Validation**: Lacks robust error handling if external APIs (Groq/Serper) experience downtime.

---

## 🛠️ Technical Hurdles Overcome
*   **Supabase Configuration**: Resolved a critical 404 error caused by malformed REST URL structures in the environment variables.
*   **CrewAI Protocol**: Mastered the requirement for explicit `expected_output` strings to prevent agent stalling.
*   **Prompt Engineering**: Iteratively refined the `SYSTEM_PROMPT` to ensure the agent doesn't loop infinitely when asking for details.

---

## 🚀 Next Steps (Week 2)
1.  **Semantic Memory**: Upgrade from flat storage to Vector Embeddings for smarter context retrieval.
2.  **Web Interface**: Move from Terminal-based interaction to a clean web dashboard.
3.  **Human-in-the-loop**: Add a review step where a team member can approve the agent's scoped delivery plan before it saves to the database.

---
**Report Generated on:** April 8, 2026
**Status:** Tangible Prototype Ready for Team Review.

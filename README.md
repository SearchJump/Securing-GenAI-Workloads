# 🛡️ Securing GenAI Workloads: RAG Pipeline & LLM Guardrails

**Role-Based Access Control (RBAC) and Prompt Injection Defense for Enterprise AI**

## 📖 Executive Summary
As enterprises rush to adopt Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) architectures, they inadvertently expose themselves to novel attack vectors such as Prompt Injection and Sensitive Data Disclosure. 

**The Objective:** Design and deploy a secure, container-first RAG pipeline that enforces strict data authorization boundaries and sanitizes both user inputs and LLM outputs, directly addressing the **OWASP LLM Top 10 vulnerabilities**.

## 🏗️ System Architecture
This project is engineered to simulate a hybrid enterprise environment (local secure storage + cloud inference) while maintaining a minimal compute footprint.
* **Vector Database:** `Qdrant` running rootless via **Podman** for secure, isolated local storage.
* **Embeddings:** `all-MiniLM-L6-v2` (running locally on CPU for fast, private vectorization).
* **LLM Inference:** GitHub Models API / Azure AI infrastructure (`gpt-4o-mini`).
* **Orchestration:** Custom Python pipeline with integrated security gates.

## 🔒 Security Implementations (The Defense)

### 1. Vector Database RBAC (Mitigating OWASP LLM06)
In a standard RAG pipeline, the retriever fetches the most mathematically relevant document, regardless of the user's security clearance. 
* **Action:** Implemented metadata filtering at the database query level. The vector search restricts context retrieval strictly to documents that match the user's authorized role (e.g., `public` vs. `admin`), preventing authorization bypass.

### 2. Input Guardrails (Mitigating OWASP LLM01)
* **Action:** Deployed a pre-retrieval validation layer that screens user prompts against heuristic threat patterns (e.g., "ignore previous instructions", "system prompt override"). Malicious payloads are intercepted and dropped before they ever reach the database or the LLM.

### 3. Output Sanitization (Mitigating OWASP LLM06 & Data Leaks)
* **Action:** Implemented a post-generation regex screening layer. If the LLM hallucinates or is tricked into exposing API keys, passwords, or PII from the context window, the output guardrail intercepts the payload and redacts the sensitive strings prior to user delivery.

## 🧪 Execution & Test Cases
The `app.py` script runs four distinct security simulations to validate the defensive posture:

1. **Standard Authorized Request:** Standard employee requests public data. *(Result: Granted & Answered)*.
2. **Horizontal Privilege Escalation Attempt:** Standard employee requests confidential database credentials. *(Result: Denied at the Vector DB level; LLM receives no context and declines to answer)*.
3. **Authorized Secret Retrieval & Redaction:** Admin requests confidential credentials. *(Result: Granted by DB, but Output Guardrail successfully catches and `[REDACTS]` the raw password before display)*.
4. **Direct Prompt Injection:** User attempts a jailbreak. *(Result: Input Guardrail triggers; pipeline execution is halted instantly).*

## 🚀 How to Run Locally

1. **Start the Qdrant Container:**
   ```bash
   podman run -d -p 6333:6333 -p 6334:6334 -v qdrant_data:/qdrant/storage:Z qdrant/qdrant


   Export API Key:
code Bash

export GITHUB_TOKEN="your_fine_grained_token"

Run the Pipeline:
code Bash

python3 app.py

# Using linear `RAG` and agents to fill out an OASIS form.

An [OASIS form](https://www.cms.gov/files/document/oasis-e1-all-item-508.pdf) is filled out by a provider who follows a strict [manual](https://www.cms.gov/files/document/oasis-e1-manualfinal12-9-2024.pdf-0). Obviously most nurses don't necessarily follow the manual, but this is the most business logic we have.

- `agents` : typically contains agent definitions for a Agentic workflow.
- `engine` : provides a suite of machine learning analytic functions to perform model training and analytics on your dataset without giving up end-to-end performance
- `models` : typically contains model definitions. 
- `backend`: code for the backend layer of the application--mostly delegates to the other layers
- `frontend`: code for the frontend layer of application

## Decision Making for linear RAG vs Agentic approaches

An Agentic workflow  is necessary when 
  - Cross-referencing between documents
  - Temporal reasoning (e.g., comparing current/past conditions)
  - Conflict resolution between sources
  - Multi-hop reasoning (e.g., "If X in transcript and Y in history, then Z"),

In a healthcare application, a supervised agentic approach will be the best way to think about these problems. Easier fields will just need a RAG extraction.
The issue with an agentic workflow is that there will need to be a series of decisions to "hop" around, and in a healthcare context these decisions will need to be recorded and audited.

| Factor                  | Agentic Needed                          | Basic RAG Sufficient                  |
|-------------------------|-----------------------------------------|---------------------------------------|
| **Field Complexity**    | High (e.g., M1033 risk scores)          | Low (e.g., M0100 dates)               |
| **Data Consistency**    | Multiple conflicting sources            | Single source of truth                |
| **Error Tolerance**     | Critical (high stakes)                  | Moderate (with human review)          |
| **Regulatory Needs**    | Strict audit requirements               | Basic logging sufficient              |
| **Latency Budget**      | Seconds acceptable                      | Sub-second required                   |
| **Reasoning Depth**     | Multi-hop or conditional logic needed   | Direct extraction possible            |
| **Data Sources**        | Multiple documents (transcript, history)| Single document                       |
| **Validation Needs**    | Iterative self-correction required      | Basic validation sufficient           |
| **Human-in-the-Loop**   | Minimal human intervention desired      | Human review acceptable               |
| **Scalability**         | Moderate to high scalability needed     | Small-scale use cases                 |

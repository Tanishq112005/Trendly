# Trendly LangGraph Architecture

This diagram shows the complete flow of our customer support AI, including the new `UnrelatedAgent` and `GuardrailAgent`.

```mermaid
flowchart TD
    %% Define Node Styles
    classDef startEnd fill:#000,stroke:#333,stroke-width:2px,color:#fff;
    classDef router fill:#8a2be2,stroke:#333,stroke-width:2px,color:#fff;
    classDef agent fill:#007acc,stroke:#333,stroke-width:2px,color:#fff;
    classDef tools fill:#d4af37,stroke:#333,stroke-width:2px,color:#000;
    classDef guardrail fill:#d9534f,stroke:#333,stroke-width:2px,color:#fff;

    %% Nodes
    S((START)):::startEnd
    E((END)):::startEnd
    
    R[Router Node<br><i>LLM w/ Structured Output</i>]:::router
    
    PolA[Policy Agent<br><i>Reads trendly_policy.md</i>]:::agent
    ProdA[Product Agent<br><i>Has Lookup & Return Tools</i>]:::agent
    TickA[Ticket Agent<br><i>Has Escalate Tool</i>]:::agent
    UnrelA[Unrelated Agent<br><i>Hardcoded Refusal</i>]:::agent
    
    T[Tool Node<br><i>Executes Python Functions</i>]:::tools
    G[Guardrail Node<br><i>Regex Policy Enforcement</i>]:::guardrail

    %% Edges
    S -->|User Input| R
    
    R -->|Intent: policy| PolA
    R -->|Intent: product| ProdA
    R -->|Intent: ticket| TickA
    R -->|Intent: unrelated| UnrelA
    
    ProdA -->|Calls Tool| T
    TickA -->|Calls Tool| T
    
    T -->|Returns Result| ProdA
    T -->|Returns Result| TickA
    
    ProdA -->|Final Answer| G
    TickA -->|Final Answer| G
    PolA -->|Final Answer| G
    UnrelA -->|Final Answer| G
    
    G -->|Scanned Output| E
```

### Visual Output from LangGraph:
Here is the actual graph generated directly from our LangGraph code:
![LangGraph PNG](file:///a:/Projects/Trendly/langgraph.png)

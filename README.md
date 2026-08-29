# AI Ticket Assistant

An LLM-powered CRM and support-ticket management system built with **Python, FastAPI, Streamlit, LangChain, and Groq-hosted LLMs**.

AI Ticket Assistant combines a conversational AI interface with traditional backend business logic to allow **customers, support agents, and administrators** to manage and monitor support tickets according to their roles.

The system is designed around a simple principle:

> **The LLM handles natural-language reasoning, while controlled backend tools execute the actual business operations.**

This helps keep operational data authoritative and prevents the model from simply generating or fabricating CRM information.

---

## Overview

Traditional support systems often require users to navigate multiple dashboards, forms, filters, and ticket-management screens.

AI Ticket Assistant provides a conversational interface where users can perform support and CRM operations using natural language.

Depending on their role, users can:

* Create and track support tickets
* Manage assigned tickets
* Retrieve customers and support agents
* Update ticket information
* Monitor ticket activity
* Perform ticket searches and filtering
* Request ticket analytics and reports
* Navigate paginated ticket results
* Continue conversations using persistent context

The system also includes automated ticket assignment and administrative oversight to support a more realistic customer-support workflow.

---

# Architecture

```text
                         User
                          │
                          ▼
                  Streamlit Client
                          │
                          ▼
                    Authentication
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
        Customer      Support Agent    Admin
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                     FastAPI API
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
        AI Assistant   Sessions     History
             │
             ▼
          LLM + Tools
             │
       ┌─────┼──────────────┐
       │     │              │
       ▼     ▼              ▼
    Tickets Customers   Support Agents
       │     │              │
       └─────┼──────────────┘
             ▼
        Backend / CRM APIs
```

---

# Role-Based Access Control

The system supports different workflows depending on the authenticated user's role.

## Customer

Customers can interact with their support tickets through the system.

Typical customer operations include:

* Creating a support ticket
* Viewing their tickets
* Checking ticket status
* Following up on existing issues
* Interacting with the AI assistant

When a customer creates a new ticket, the system can automatically assign it to a support agent using the ticket-assignment mechanism.

---

## Support Agent

Support agents are responsible for handling tickets assigned to them.

Depending on the available operations, agents can:

* View assigned tickets
* Retrieve ticket details
* Update ticket information
* Work on customer issues
* Track ticket status
* Interact with the AI assistant to retrieve relevant information

The role-based structure prevents support workflows from being treated as a single unrestricted user workflow.

---

## Administrator

Administrators have broader visibility over the support operation.

Administrators can:

* View overall ticket activity
* Monitor tickets handled by support agents
* Review agent workloads
* Check the progress of assigned work
* Inspect ticket activity across the support system
* Reassign tickets between support agents when required

This provides an administrative layer for monitoring and managing the overall support workflow.

---

# Automated Ticket Assignment

One of the core backend business rules is automated ticket assignment.

When a customer creates a ticket, the system distributes the ticket among available support agents using a **round-robin strategy**.

The basic workflow is:

```text
Customer creates ticket
        │
        ▼
Find available support agents
        │
        ▼
Select next agent in rotation
        │
        ▼
Assign ticket
        │
        ▼
Support agent handles ticket
```

For example:

```text
Agent A → Ticket 1
Agent B → Ticket 2
Agent C → Ticket 3
Agent A → Ticket 4
Agent B → Ticket 5
Agent C → Ticket 6
```

The goal is to avoid repeatedly assigning new tickets to the same support agent and provide a simple workload-distribution mechanism.

Administrators can manually reassign tickets when operational requirements change.

---

# Administrative Monitoring

The administrator workflow provides visibility across the support operation.

Instead of an administrator only seeing individual tickets, the system is designed around an overall operational view.

Administrators can use the system to:

```text
                  Administrator
                        │
                        ▼
                Support Overview
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       Tickets       Agents        Activity
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                 Management Actions
                        │
                        ▼
                  Reassign Tickets
```

This allows administrators to identify tickets that require attention and redistribute work when necessary.

---

# LLM Tool Calling

The assistant uses **LangChain with a Groq-hosted LLM** and binds backend operations as tools.

Instead of allowing the LLM to directly modify application state, the model determines which operation is required and invokes a controlled backend function.

Examples of supported operations include:

* `create_ticket`
* `get_tickets`
* `update_tickets`
* `show_support`
* `show_customers`

This creates a separation between:

```text
Natural Language Reasoning
            │
            ▼
       LLM Decision
            │
            ▼
       Tool Selection
            │
            ▼
     Backend Operation
            │
            ▼
       Authoritative Data
            │
            ▼
       LLM Response
```

---

# Preventing Fabricated CRM Data

The assistant is designed so that operational CRM information should come from backend tools rather than being invented by the language model.

For example:

```text
User:
"Show me ticket #123"

        ↓

LLM determines that ticket data is required

        ↓

get_tickets(...)

        ↓

Backend / CRM

        ↓

Actual ticket information

        ↓

LLM

        ↓

Response to user
```

This separation is important because an LLM-generated answer alone should not be treated as the authoritative source for ticket information.

---

# Ticket Management

The assistant supports multiple ticket-management workflows.

## Creating Tickets

The assistant can collect information required to create a ticket, such as:

* Customer
* Title
* Description
* Priority

The request is then passed to the appropriate backend tool.

---

## Retrieving Tickets

Tickets can be retrieved and filtered using information such as:

* Ticket ID
* Customer
* Priority
* Status
* Date/time

This allows users to ask conversational questions instead of manually constructing every query.

---

## Updating Tickets

Controlled backend tools can be used to update ticket information and status.

The LLM is responsible for understanding the user's request, while the backend performs the actual update.

---

# Conversational Navigation

The assistant contains logic for handling references to previously displayed ticket lists.

For example:

```text
User:
Show me the open tickets.

Assistant:
1. Ticket A
2. Ticket B
3. Ticket C
...

User:
Show me the second one.

        ↓

Resolve list reference

        ↓

Identify canonical ticket

        ↓

Retrieve ticket information

        ↓

Return result
```

This allows users to interact with results conversationally rather than repeatedly providing ticket IDs.

The system also supports pagination-related interactions such as:

* Next page
* Previous page
* Specific page
* Show first N results
* Show all results

---

# Conversation Memory

The application maintains persistent conversation history using session and conversation identifiers.

The conversation workflow includes:

```text
User Message
     ↓
Conversation Storage
     ↓
Previous Context
     ↓
LLM
     ↓
Response
     ↓
Stored Conversation
```

The project also includes an LLM-based conversation summarization mechanism.

Instead of repeatedly sending an entire long conversation to the model, relevant conversation information can be summarized and reused as context.

The goal is to:

* Preserve useful conversational context
* Reduce unnecessary repeated context
* Control token usage
* Improve long-running conversations

---

# Ticket Analytics

The assistant supports ticket analytics and reporting workflows.

Potential analytical views include:

* Ticket status distribution
* Priority distribution
* Open vs. closed tickets
* Resolution rates
* Agent workload
* Weekly performance
* Ticket trends

The intention is for analytics to be derived from retrieved ticket data rather than allowing the LLM to fabricate statistics.

---

# Backend Architecture

The backend is implemented using **FastAPI** and is divided into separate responsibilities.

The major areas include:

```text
server/
│
├── ai_schemas/
│   ├── chat.py
│   ├── customer_inp.py
│   ├── support_ag.py
│   └── ticket_input.py
│
├── routes/
│   ├── history.py
│   └── session.py
│
├── tools_function/
│   └── chatbot.py
│
├── utils/
│   ├── chat_storage.py
│   └── chat_summary.py
│
├── assistant.py
└── fast_main.py
```

This separation keeps AI orchestration, API routing, data schemas, tools, and conversation utilities independently manageable.

---

# Frontend

The frontend is implemented using **Streamlit**.

The client provides functionality for:

* User authentication
* Role-aware interaction
* Conversational chat
* Conversation history
* Session handling
* Logout

The frontend communicates with the FastAPI backend through HTTP requests.

---

# Project Structure

```text
AI-Ticket-Assistant/
│
├── client/
│   ├── app.py
│   └── auth.py
│
├── server/
│   ├── ai_schemas/
│   │   ├── chat.py
│   │   ├── customer_inp.py
│   │   ├── support_ag.py
│   │   └── ticket_input.py
│   │
│   ├── routes/
│   │   ├── history.py
│   │   └── session.py
│   │
│   ├── tools_function/
│   │   └── chatbot.py
│   │
│   ├── utils/
│   │   ├── chat_storage.py
│   │   └── chat_summary.py
│   │
│   ├── assistant.py
│   └── fast_main.py
│
├── project_notes.txt
└── requirement.txt
```

---

# Technology Stack

| Component            | Technology                             |
| -------------------- | -------------------------------------- |
| Programming Language | Python                                 |
| Backend              | FastAPI                                |
| Frontend             | Streamlit                              |
| LLM Orchestration    | LangChain                              |
| LLM Provider         | Groq                                   |
| Data Validation      | Pydantic                               |
| API Communication    | REST                                   |
| Authentication       | Session-based                          |
| AI Interaction       | LLM Tool Calling                       |
| Conversation Memory  | Persistent Storage + LLM Summarization |

---

# Key Engineering Concepts

The project explores several areas of modern backend and AI engineering:

### LLM Tool Orchestration

Connecting natural-language reasoning with deterministic backend operations.

### Role-Based Access Control

Different users receive different capabilities based on their role.

### Business Logic Automation

Round-robin ticket assignment distributes incoming workload across support agents.

### Administrative Workflows

Administrators can monitor support operations and redistribute work.

### Conversational Memory

Persistent conversation history and summarization allow the assistant to maintain context across interactions.

### Structured AI Inputs

Pydantic-based schemas provide structured representations for important application data.

### Separation of Concerns

The project separates:

```text
Frontend
   ↓
API Layer
   ↓
AI Orchestration
   ↓
Tool Layer
   ↓
Backend/CRM Operations
```

---

# Example Workflow

## Customer Creates a Ticket

```text
Customer
   │
   ▼
Creates Ticket
   │
   ▼
Backend receives request
   │
   ▼
Round-robin assignment
   │
   ▼
Support Agent selected
   │
   ▼
Ticket assigned
   │
   ▼
Agent works on ticket
   │
   ▼
Administrator can monitor progress
```

---

## Administrator Reassigns a Ticket

```text
Administrator
      │
      ▼
View support tickets
      │
      ▼
Identify ticket requiring reassignment
      │
      ▼
Select another support agent
      │
      ▼
Update ticket assignment
```

---

# Design Philosophy

The project intentionally combines **probabilistic AI behavior with deterministic backend logic**.

The LLM is useful for:

* Understanding natural language
* Determining user intent
* Selecting appropriate tools
* Generating conversational responses

The backend remains responsible for:

* Authentication
* Authorization
* Ticket state
* Ticket assignment
* Data retrieval
* Data modification
* Business rules
* Operational correctness

This separation makes the system more predictable than allowing the LLM to directly control application state.

---

# Current Status

This is a personal engineering project focused on exploring practical integration of LLMs with backend systems and business workflows.

The project is being developed incrementally, with additional improvements planned around reliability, testing, authentication, data storage, observability, and AI evaluation.

---

# Future Improvements

Potential future improvements include:

* Database-backed ticket and conversation storage
* More granular role and permission management
* Improved ticket-assignment and workload-balancing logic
* Automated ticket-priority classification
* Retrieval-augmented generation
* Automated evaluation of LLM responses and tool calls
* Better error handling and recovery
* Automated testing for conversational workflows
* Observability and tracing
* Improved security and authorization
* Production deployment

---

# Repository

GitHub: https://github.com/AdtyDev/AI-Ticket-Assistant

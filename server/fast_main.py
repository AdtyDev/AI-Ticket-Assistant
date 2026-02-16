"""
Main FastAPI application entry point.

This module initializes the FastAPI server instance and
registers all route groups (routers) that power the AI CRM system.

It acts as the central API gateway that exposes endpoints for:

    • AI Assistant interactions
    • Conversation history management
    • Session lifecycle operations

Routers are modularized to maintain separation of concerns:

    assistant_router → AI chat + tool orchestration
    history_router   → Conversation storage & retrieval
    session_router   → Session cleanup & logout handling

This structure enables scalable API expansion while keeping
feature domains isolated.

Typical server startup command:

    uvicorn main:app --reload

Architecture Role:

    Client → FastAPI App → Routers → Services → Storage / Tools
"""



from fastapi import FastAPI
from server.assistant import router as assistant_router
from server.routes.history import router as history_router
from server.routes.session import router as __router

app = FastAPI(
    title="AI CRM Assistant API",
    description=(
        "Backend service powering the AI-driven CRM assistant. "
        "Provides conversational support, ticket operations, "
        "customer insights, and session-based memory."))


"""
Register all application routers.

Each router encapsulates a specific functional domain
and exposes its endpoints under predefined prefixes.
"""

app.include_router(assistant_router)

app.include_router(history_router)

app.include_router(__router)
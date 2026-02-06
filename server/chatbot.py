from langchain.tools import tool
import requests
from server.ai_schemas.ticket_input import GetTicketInput, CreateTicketInput

BASE_URL = "http://127.0.0.1:8000"


priority_map = {
    "LOW": "low",
    "MEDIUM": "medium",
    "HIGH": "high"
    }

# Customer lookup function
def get_customer_id_from_email(email: str, auth_token: str) -> int:
    """
    Fetch customer ID using email.
    Uses same auth header as Streamlit UI.
    """

    url = f"{BASE_URL}/customers/"
    headers = {"X-SESSION-ID": auth_token}

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Customer fetch failed: {res.text}")

    customers = res.json()

    # Search email match
    for customer in customers:
        if customer["email"] == email:
            return customer["id"]

    raise Exception(f"No customer found with email: {email}")


# Ticket creation tool
@tool("create_ticket", args_schema=CreateTicketInput)
def create_ticket_tool(
    customer_email: str,
    title: str,
    description: str,
    priority: str,
    auth_token: str,
):
    """Create a support ticket in the system."""

    # Step 1 — resolve customer_id
    customer_id = None
    if customer_email:
        customer_id = get_customer_id_from_email(
            customer_email,
            auth_token
        )

    normalized_priority = priority_map.get(priority.upper())

    if not normalized_priority:
        raise Exception(f"Invalid priority: {priority}")
    payload = {
        "title": title,
        "description": description,
        "priority": normalized_priority,
        "customer_id": customer_id,
    }

    headers = {
        "X-SESSION-ID": auth_token,
        "Content-Type": "application/json",
    }

    res = requests.post(
        f"{BASE_URL}/tickets/",
        json=payload,
        headers=headers,
    )

    if res.status_code != 200:
        raise Exception(f"Ticket creation failed: {res.text}")

    data = res.json()

    return {
        "ticket_id": data["id"],
        "message": "Ticket created successfully"
    }


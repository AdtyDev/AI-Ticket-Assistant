from langchain.tools import tool
import requests
from server.ai_schemas.ticket_input import GetTicketInput, CreateTicketInput, UpdateTicket


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

@tool("get_tickets",args_schema=GetTicketInput)
def get_ticket_tool(customer_email: str, priority:str , ticket_id: str  ,auth_token:str):
    """Fetch or get tickets from the system according to what was been asked or with optional Filters provided by the user."""
    
    if not auth_token:
        raise Exception("Not able to fetch because auth token is missing.")
    
    headers = {
        "X-SESSION-ID": auth_token 
    }

    res = requests.get(f"{BASE_URL}/tickets",headers=headers)

    if res.status_code != 200:
        raise Exception(f"Failed to fetch tickets: {res.text}")
    tickets = res.json()

    if customer_email:
        customer_id = get_customer_id_from_email(customer_email,auth_token)

        tickets = [
            t for t in tickets
            if t["customer_id"] == customer_id
        ]
    
    if priority:
        normalized_priority = priority_map.get(priority.upper())

        tickets = [
            t for t in tickets
            if t["priority"] ==  normalized_priority
        ]

    if ticket_id:
        tickets = [
            t for t in tickets
            if t['id'] == ticket_id
        ]

    if not tickets:
        return "No tickets found"
    
    formats = [
        f"ID: {t['id']} | title: {t['title']} | Description: {t['description']} | Priority: {t['priority']} | Status: {t['status']} | Assigned_agent: {t['assigned_agent']} | Customer_ID: {t['customer_id']} "
        for t in tickets
    ]

    return formats


@tool("update_tickets",args_schema=UpdateTicket)
def update_ticket_tool(ticket_id : int , status : str, auth_token : str):
    """Update ticket status."""

    if not auth_token:
        raise Exception("Not able to fetch because auth token is missing.")
    
    headers = {
        "X-SESSION-ID": auth_token,
        "Content-type": "application/json"
    }

    payload = {
        "status": status
    }

    response = requests.patch(f"{BASE_URL}/tickets/{ticket_id}/status", headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Not able to update the ticket, the reason might be: {response.text}")
    
    return response.json()



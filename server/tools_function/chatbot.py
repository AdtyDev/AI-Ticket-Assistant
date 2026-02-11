from langchain.tools import tool
import requests
from server.ai_schemas.ticket_input import GetTicketInput, CreateTicketInput, UpdateTicket
from server.ai_schemas.support_ag import All_Support
from server.ai_schemas.customer_inp import ShowCustomers
from fastapi import logger
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
    try:
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
    
    except ValueError as e:
        raise Exception(f"Not able to  {e}")
        


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
    try:
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
    except Exception as e:
        return Exception(f"Not able to create because: {e}")

@tool("get_tickets",args_schema=GetTicketInput)
def get_ticket_tool(customer_email: str, priority:str , ticket_id: str  ,auth_token:str):
    """Fetch or get tickets from the system according to what was been asked or with optional Filters provided by the user."""
    try:
        if not auth_token:
            raise Exception("Not able to fetch because auth token is missing.")
        
        headers = {
            "X-SESSION-ID": auth_token 
        }

        res = requests.get(f"{BASE_URL}/tickets",headers=headers)

        if res.status_code != 200:
            raise Exception(f"Failed to fetch tickets: {res.text}")
        tickets = res.json()
        print("@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@_@")
        # print(tickets)

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
            f"ID: {t['id']} | title: {t['title']} | Description: {t['description']} | Priority: {t['priority']} | Status: {t['status']} | Assigned_agent: {t['assigned_agent']} | Customer_ID: {t['customer_id']} | Created_At: {t['created_at']} | Updated_at: {t['updated_at']}"
            for t in tickets
        ]

        return formats
    except Exception as e:
        return Exception(f"Not able to get the tickets because: {e}")


@tool("update_tickets",args_schema=UpdateTicket)
def update_ticket_tool(ticket_id : int , status : str, auth_token : str):
    """Update ticket status."""
    
    try:
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
    except Exception as e:
        return Exception(f"Not able to update the ticket because: {e}")


@tool("show_support", args_schema=All_Support)
def show_all_support(auth_token: str ):
    """
    Show all the support agents
    """
    try:
        if not auth_token:
            raise Exception("Not able to fetch because auth token is missing.")
        
        headers = {
            "X-SESSION-ID" : auth_token
        }

        response = requests.get(f"{BASE_URL}/users/support",headers=headers)

        if response.status_code != 200:
            raise Exception(f"Not able to fetch or show agents because: {response.text}")
        
        support_agents = response.json()

        return support_agents
    except Exception as e:
        return Exception(f"Not able to show all the support agents because: {e}")

@tool("show_customers",args_schema=ShowCustomers)
def show_all_customer(auth_token:str):

    """ Fetch all the customers"""
    try:
        if not auth_token:
            raise Exception("Not able to fetch because auth token is missing.")
        
        headers = {
            "X-SESSION-ID" : auth_token
        }

        response = requests.get(f"{BASE_URL}/customers/",headers=headers)

        if response.status_code !=200:
            raise Exception(f"Not able to fetch all customers because of: {response.text}")
        
        customers = response.json()

        return {
        "type": "customers",
        "data": customers
    }
        
    except Exception as e:
        return Exception(f"Not able to show all the customers because: {e}")

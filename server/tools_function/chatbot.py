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
    Retrieve a customer ID using their email address.

    This helper function queries the customer service endpoint
    and searches for a customer whose email matches the provided value.
    It uses the session authentication header for authorization.

    Args:
        email (str):
            Email address of the customer whose ID should be retrieved.

        auth_token (str):
            Session authentication token passed via `X-SESSION-ID` header.
            Required to authorize the request.

    Returns:
        int:
            Unique customer ID corresponding to the provided email.

    Raises:
        Exception:
            - If the customer service request fails
            - If no customer exists with the given email
            - If response parsing fails

    Example:
        > get_customer_id_from_email("user@example.com", "abc123")
        42
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
    """
    Create a new support ticket in the system.

    This tool allows an AI agent to create a ticket by providing
    customer details, issue description, and priority level.

    Workflow:
        1. Resolve customer ID from email
        2. Normalize priority value
        3. Send ticket creation request
        4. Return created ticket metadata

    Args:
        customer_email (str):
            Email of the customer for whom the ticket is created.

        title (str):
            Short summary of the issue.

        description (str):
            Detailed explanation of the problem.

        priority (str):
            Ticket urgency level. Accepted values:
            LOW, MEDIUM, HIGH (case-insensitive).

        auth_token (str):
            Session authentication token used for API authorization.

    Returns:
        dict:
            {
                "ticket_id": int,
                "message": "Ticket created successfully"
            }

    Raises:
        Exception:
            - If customer lookup fails
            - If priority is invalid
            - If ticket creation API fails

    Notes:
        Priority values are normalized using `priority_map`.
    """
    try:
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
def get_ticket_tool(customer_email: str, 
                    priority:str , 
                    ticket_id: str , 
                    auth_token:str):
    """
    Retrieve tickets from the system with optional filters.

    This tool fetches all tickets and applies filters based on
    customer email, priority, or ticket ID if provided.

    Filters are optional and can be combined.

    Args:
        customer_email (str):
            Filter tickets belonging to a specific customer.

        priority (str):
            Filter by ticket priority (LOW, MEDIUM, HIGH).

        ticket_id (str):
            Retrieve a specific ticket by its ID.

        auth_token (str):
            Session authentication token required for access.

    Returns:
        list[str] | str:
            - Formatted ticket summaries if found
            - "No tickets found" if no match exists

    Raises:
        Exception:
            - If authentication token is missing
            - If ticket retrieval API fails

    Notes:
        Filtering is performed client-side after fetching tickets.
    """
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
    """
    Update the status of an existing support ticket.

    This tool allows an AI agent to modify ticket progress
    (e.g., open → in_progress → resolved).

    Args:
        ticket_id (int):
            Unique identifier of the ticket to update.

        status (str):
            New status value to assign to the ticket.

        auth_token (str):
            Session authentication token required for authorization.

    Returns:
        dict:
            Updated ticket data returned by the API.

    Raises:
        Exception:
            - If auth token is missing
            - If ticket does not exist
            - If update request fails
    """
    
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
    Retrieve all support agents from the system.

    This tool fetches the list of users who have
    support/agent roles assigned.

    Args:
        auth_token (str):
            Session authentication token required for access.

    Returns:
        list[dict]:
            List of support agents with their details
            (e.g., ID, name, email, role).

    Raises:
        Exception:
            - If auth token is missing
            - If API request fails
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

    """
    Retrieve all customers from the system.

    This tool returns the full customer directory,
    typically used for lookup, ticket creation,
    or analytics.

    Args:
        auth_token (str):
            Session authentication token required
            to authorize the request.

    Returns:
        dict:
            {
                "type": "customers",
                "data": [ ... customer objects ... ]
            }

    Raises:
        Exception:
            - If auth token is missing
            - If API request fails
    """
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


@tool("employee_ticket_summary")
def employee_ticket_summary_tool(auth_token: str):
    """
    Fetch ticket summary for the logged-in employee.

    Returns:

        • Total tickets created
        • Ticket list with status & priority
    """

    try:
        if not auth_token:
            raise Exception("Missing auth token")

        headers = {
            "X-SESSION-ID": auth_token
        }

        res = requests.get(
            f"{BASE_URL}/analytics/employee/summary",
            headers=headers
        )

        if res.status_code != 200:
            raise Exception(res.text)

        data = res.json()

        return {
            "type": "employee_summary",
            "total_tickets": data["total_tickets"],
            "tickets": data["tickets"]
        }

    except Exception as e:
        return Exception(
            f"Failed to fetch employee summary: {e}"
        )
    


@tool("support_ticket_summary")
def support_ticket_summary_tool(auth_token: str):
    """
    Fetch workload summary for support agents.

    Returns:

        • Total assigned tickets
        • Tickets grouped by customer
    """

    try:
        if not auth_token:
            raise Exception("Missing auth token")

        headers = {
            "X-SESSION-ID": auth_token
        }

        res = requests.get(
            f"{BASE_URL}/analytics/support/summary",
            headers=headers
        )

        if res.status_code != 200:
            raise Exception(res.text)

        data = res.json()

        return {
            "type": "support_summary",
            "total_tickets": data["total_tickets"],
            "tickets_by_customer": data["tickets_by_customer"]
        }

    except Exception as e:
        return Exception(
            f"Failed to fetch support summary: {e}"
        )
    
@tool("team_lead_ticket_summary")
def team_lead_ticket_summary_tool(auth_token: str):
    """
    Fetch organization-wide ticket overview.

    Accessible only by team leads.

    Returns:

        • Total tickets
        • Detailed ticket dataset
    """

    try:
        if not auth_token:
            raise Exception("Missing auth token")

        headers = {
            "X-SESSION-ID": auth_token
        }

        res = requests.get(
            f"{BASE_URL}/analytics/team-lead/summary",
            headers=headers
        )

        if res.status_code != 200:
            raise Exception(res.text)

        data = res.json()

        return {
            "type": "team_lead_summary",
            "total_tickets": data["total_tickets"],
            "tickets": data["tickets"]
        }

    except Exception as e:
        return Exception(
            f"Failed to fetch team lead summary: {e}"
        )
    
@tool("weekly_agent_stats")
def weekly_agent_stats_tool(auth_token: str):
    """
    Fetch weekly performance metrics for agents.

    Returns per-day stats:

        • Opened tickets
        • Pending tickets
        • Closed tickets
        • Agent mapping
    """

    try:
        if not auth_token:
            raise Exception("Missing auth token")

        headers = {
            "X-SESSION-ID": auth_token
        }

        res = requests.get(
            f"{BASE_URL}/analytics/weekly",
            headers=headers
        )

        if res.status_code != 200:
            raise Exception(res.text)

        data = res.json()

        return {
            "type": "weekly_stats",
            "data": data
        }

    except Exception as e:
        return Exception(
            f"Failed to fetch weekly stats: {e}"
        )
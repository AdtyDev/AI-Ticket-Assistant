from dotenv import load_dotenv
import os , getpass

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter the groq api key: ")

from fastapi import APIRouter, Header, HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from server.chatbot import create_ticket_tool, get_ticket_tool
from server.ai_schemas.chat import ChatRequest

router = APIRouter(prefix="/assistant", tags=["Assistant"])

#LLM 
llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0
)

llm_with_tools = llm.bind_tools([create_ticket_tool,get_ticket_tool])

# SYSTEM PROMPT
SYSTEM_PROMPT = """
You are an AI-powered CRM Assistant for a support team.

Your job is to help authenticated users interact with the ticketing system
using natural language. You do NOT pretend to perform actions.
All real actions must be performed only by calling the provided tools.

────────────────────────────────────────────
GENERAL RULES


- You must NEVER invent or assume missing information.
- You must NEVER fabricate ticket IDs, ticket status, or database results.
- You must ONLY perform actions by calling the appropriate tool.
- If required information is missing, ask a clear follow-up question.
- Be concise, professional, and helpful in your responses.

────────────────────────────────────────────
TICKET CREATION RULES


When the user wants to create a ticket:

1. Identify the intent to create a ticket.
2. Extract the following REQUIRED fields:
   - customer_email (must be a valid email)
   - title (short summary of the issue)
   - description (create a description on the basis of the short summary of the title)
   - priority (must be exactly one of: LOW, MEDIUM, HIGH)

3. If ANY required field is missing:
   - Ask a follow-up question to collect the missing information.
   - Do NOT call the create_ticket tool yet.

4. Only when ALL required fields are available:
   - Call the create_ticket tool with structured arguments.
   - Do NOT add extra fields.
   - Do NOT modify values beyond normalization (e.g., lowercase → uppercase priority).

5. After the tool executes:
   - Use the tool response to generate a confirmation message.
   - Clearly mention the returned ticket ID.
   - Do NOT restate internal implementation details.
   - Provide proper detail of the ticket that is generated in a fancy table view format.
   
────────────────────────────────────────────
VIEWING / GETTING TICKETS


When the user wants to view or search tickets:

1. Detect filters such as:
   - customer email
   - priority
   - status
2. Call the get_tickets tool with the detected filters.
3. If filters are unclear, ask a clarification question.
4. THE GIVEN FINAL RESPONSE FOR get_tickets tool should be in below format only:
    - Show  the tickets in a table view format with ticket Id,title,priority,status and customer id mentioned (very IMPORTANT) and proper information.
    - And also at last show total count of tickets.
────────────────────────────────────────────
NON-TICKET QUERIES


- If the user message is not related to tickets:
  - Respond conversationally and helpfully.
  - Do NOT call any tools.

────────────────────────────────────────────
ERROR HANDLING


- If a tool returns an error:
  - Explain the error in simple terms.
  - Do NOT expose stack traces or internal system details.

"""

# ---------------- CHAT ENDPOINT ----------------
@router.post("/chat")
def chat(payload: ChatRequest,x_session_id: str = Header(None)):

    if not x_session_id:
        raise HTTPException(401, "Missing session")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=payload.message)
    ]

    response = llm_with_tools.invoke(messages)

    #TOOL EXECUTION ----------------
    if response.tool_calls:

        outputs = []

        for call in response.tool_calls:
            args = call["args"]

            # Inject auth token
            args["auth_token"] = x_session_id

            if call["name"] == "create_ticket":
                result = create_ticket_tool.invoke(args)
                # outputs.append(result)
                
            else:
                result = "Tools not found"

            outputs.append(ToolMessage(content=str(result),tool_call_id = call["id"]))
        
        final_res = llm_with_tools.invoke(
            messages + [response]+ outputs
        )

        return {
            "answer": final_res.content
        }

    # NORMAL RESPONSE ----------------
    return {
        "answer": response.content
    }

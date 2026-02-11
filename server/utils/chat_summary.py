from dotenv import load_dotenv
import os , getpass

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter the groq api key: ")

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

# Small fast model for summaries
summary_llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0
)


def summarize_conversation(messages: list) -> str:
    """
    Summarize chat history for context memory.
    """

    if not messages:
        return ""

    text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in messages]
    )

    prompt = f"""
Summarize the following conversation briefly so it can be used
as context for future responses.

Conversation:
{text}

Summary:
"""

    res = summary_llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return res.content # type: ignore



from dotenv import load_dotenv
import os , getpass

load_dotenv()

# Enable LangChain tracing for observability/debugging
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Ensure GROQ API key is available
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter the groq api key: ")

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

# Small fast model optimized for summarization
summary_llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0
)


def summarize_conversation(messages: list) -> str:
    """
    Generate a concise summary of a conversation history.

    This function converts a list of chat messages into a short
    textual summary that can be used as contextual memory for
    future LLM responses.

    It is typically used to:
        - Reduce token usage
        - Preserve long-term context
        - Maintain conversation continuity
        - Store memory snapshots

    The summarization is performed using a deterministic
    (temperature=0) LLM to ensure consistent outputs.

    Args:
        messages (list[dict]):
            List of conversation messages in chronological order.

            Expected message schema:
                {
                    "role": "user" | "assistant" | "system",
                    "content": "Message text"
                }

            Example:
                [
                    {"role": "user", "content": "I need help"},
                    {"role": "assistant", "content": "Sure"}
                ]

    Returns:
        str:
            A brief natural-language summary capturing key points,
            user intent, and important context from the conversation.

            Returns an empty string if no messages are provided.

    Prompt Design:
        The prompt instructs the LLM to:
            - Summarize briefly
            - Preserve context relevance
            - Produce forward-usable memory

    Side Effects:
        - Sends conversation data to GROQ API
        - Consumes LLM tokens

    Raises:
        Exception:
            If the LLM request fails or API key is invalid.

    Example:
        > summarize_conversation(messages)

        "User asked about ticket creation and priority handling.
         Assistant explained workflow and API usage."
    """
    try:
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
    except Exception as e:
        return (f"The problem is this: {e}")



from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
import os
from dotenv import load_dotenv


# 1. Define a tool
@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

# 2. Load model (flash = faster)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

# 3. Create agent with tools
agent_executor = create_react_agent(model, tools=[calculator])

# 4. Chat loop with streaming + final output
print("Welcome! I'm your AI assistant. Type 'quit' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    print("Assistant: ", end="")
    for chunk in agent_executor.stream({"messages": [HumanMessage(content=user_input)]}):
        # Stream intermediate agent messages
        if "agent" in chunk and "messages" in chunk["agent"]:
            for message in chunk["agent"]["messages"]:
                print(message.content, end="", flush=True)

        # Stream final output
        if "output" in chunk:
            print(chunk["output"], end="", flush=True)

    print()  # Newline after full response








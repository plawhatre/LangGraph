from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

@tool(return_direct=False)
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
agent = create_react_agent(
    model=model,
    tools=[add]
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what's 3 + 5?"}]}
)["messages"][-1].pretty_print()
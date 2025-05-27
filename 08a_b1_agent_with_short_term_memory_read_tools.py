import uuid
from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent, chat_agent_executor, InjectedState
from langgraph.checkpoint.memory import InMemorySaver

class CustomState(chat_agent_executor.AgentState):
    user_id: str

def get_weather(city: str) -> str:
    """Get weather for the city"""
    city_dict = {
        "Mumbai": "Hot and Humid",
        "Delhi": "Rainy"
    }
    return city_dict.get(city, f"{city}'s weather is unkown at the moment")

def get_user_info(state: Annotated[CustomState, InjectedState]):
    "Get information about the user"
    usr = state['user_id']
    return "User is Prashant" if usr == "user1" else "Unkown User"

if __name__ == "__main__":
    # Stage 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Stage 2: Tools
    tools = [get_weather, get_user_info]

    # Stage 3: Short Term Memory
    memory = InMemorySaver()

    # Stage 4: Agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=memory,
        state_schema=CustomState
    )

    # Stage 5: Invoke
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    messages = [{
        "role": "user",
        "content": "What is the weather like in Mumbai?"
    }]
    agent.invoke({"messages": messages, "user_id": "user1"}, config=config)["messages"][-1].pretty_print()

    messages = [{
        "role": "user",
        "content": "Look up the user"
    }]
    agent.invoke({"messages": messages, "user_id": "user1"}, config=config)["messages"][-1].pretty_print()

import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

def get_weather(city: str) -> str:
    """Get weather for the city"""
    city_dict = {
        "Mumbai": "Hot and Humid",
        "Delhi": "Rainy"
    }
    return city_dict.get(city, f"{city}'s weather is unkown at the moment")

if __name__ == "__main__":
    # Stage 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Stage 2: Tools
    tools = [get_weather]

    # Stage 3: Short Term Memory
    memory = InMemorySaver()

    # Stage 3: Agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=memory
    )

    # Stage 4: Invoke
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    messages = [{
        "role": "user",
        "content": "What is the weather like in Mumbai?"
    }]
    agent.invoke({"messages": messages}, config=config)["messages"][-1].pretty_print()

    messages = [{
        "role": "user",
        "content": "What is the weather like in Nagpur?"
    }]
    agent.invoke({"messages": messages}, config=config)["messages"][-1].pretty_print()

import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

def get_weather(city: str) -> str:
    """Get weather for the city"""
    city_dict = {
        "Mumbai": "Hot and Humid",
        "Delhi": "Rainy"
    }
    return city_dict.get(city, f"{city}'s weather is unkown at the moment")

def pre_model_hook(state):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=380,
        start_on="human",
        end_on=("human", "tool")
    )
    return {"llm_inp_messages": trimmed_messages}

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
        checkpointer=memory,
        pre_model_hook=pre_model_hook
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

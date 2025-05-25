import uuid
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.prebuilt import create_react_agent, chat_agent_executor
from langgraph.checkpoint.memory import InMemorySaver

from  langmem.short_term import SummarizationNode

class State(chat_agent_executor.AgentState):
    # this is for previous summary information
    context: dict[str, Any]


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

    # Step 4: Summarization Node
    summarization_node = SummarizationNode(
        model=model,
        token_counter=count_tokens_approximately,
        max_tokens=380,
        max_summary_tokens=120,
        output_messages_key="llm_inp_messagees"
    )

    # Stage 3: Agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=memory,
        state_schema=State,
        pre_model_hook=summarization_node
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

import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition


def chatbot(state: MessagesState):
    return {"messages": [model_with_tools.invoke(state['messages'])]}

@tool
def get_weather(city: str) -> str:
    """This tool return the weather condition of the city for which query is made"""
    city = city.capitalize()
    forecast ={
        "Delhi": {
            "Temperature": '41°C', 
            "Outlook": "with hazy conditions"
        },
        "Mumbai": {
            "Temperature": '31°C', 
            "Outlook": "experiencing haze"
        },
        "Chennai": {
            "Temperature": '34°C', 
            "Outlook": "with light rain"
        },
        "Kolkata": {
            "Temperature": '37°C', 
            "Outlook": "mostly sunny with some haze"
        },
        "Default": {
            "Temperature": 'unkown',
            "Outlook": 'unkown'

        }
    }
    return forecast.get(city, forecast.get('Default'))
if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    model_with_tools = model.bind_tools([get_weather])

    # Step 2: Graph
    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node(chatbot)
    graph_builder.add_node("tools", ToolNode([get_weather]))

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    graph_builder.add_edge("tools", "chatbot")
    graph = graph_builder.compile(MemorySaver())

    # Step 3: Invocation
    config = {
        "configurable": {"thread_id": uuid.uuid4()}
    }
    messages = [
        {
            "role": "user",
            "content": "What's the weather like in Mumbai."
        },
        {
            "role": "user",
            "content": "Should I step outside today or stay in?"
        }]
    for message in messages:
        events = graph.stream({"messages": [message]}, config=config, stream_mode='values')
        for event in events:
            if "messages" in event:
                event["messages"][-1].pretty_print()

    

    # Step 4: Replay the full state history
    to_replay = None
    print(">> "*15+ "State History" +" << "*15)
    for state in graph.get_state_history(config=config):
        print(
            "Num States: ",
            f"{len(state.values["messages"])}",
            "Next: ",
            state.next
        )
        print("-"*80)
        if len(state.values["messages"]) == 2:
            to_replay = state

    # Step 5: Load a state from moment in time
    print(">> "*15+ "State From Moment In Time" +" << "*15)
    for event in graph.stream(None, to_replay.config, stream_mode="values"):
        event["messages"][-1].pretty_print()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from langgraph.graph import START, END, StateGraph, MessagesState
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
    # Step 1: Model and tool
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash"
    )
    model_with_tools = model.bind_tools([get_weather])

    # Step 2: Graph
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)
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
    graph = graph_builder.compile()

    # Step 3: Invocation
    while True:
        inp = str(input("User: "))
        if inp.lower() in ['exit', 'quit', 'q']:
            break
        prompt = [{
            "role": 'user',
            "content": inp
        }] 
        response = graph.invoke({"messages": prompt})
        response["messages"][-1].pretty_print()
import uuid

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

"""
Example Usage:
--------------
User: What's the weather like in Chennai?
================================== Ai Message ==================================

The weather in Chennai is 34°C with light rain.
User: What about Bombay?
================================== Ai Message ==================================

I am unable to find the weather details for Bombay. Would you like me to get assistance from a human?
User: Yes
================================== Ai Message ==================================
Tool Calls:
  human_assitance (433dbc20-54ec-4e24-a366-bae6ef2ca4d2)
 Call ID: 433dbc20-54ec-4e24-a366-bae6ef2ca4d2
  Args:
    query: Unable to find weather details for Bombay.
Human Intervention: Bombay is the old name for Mumbai.
================================== Ai Message ==================================

Bombay is the old name for Mumbai. Would you like me to search for Mumbai?
User: Yes
================================== Ai Message ==================================

The weather in Mumbai is 31°C and experiencing haze.
"""

def chatbot(state: MessagesState):
    response = model_with_tools.invoke(state['messages'])
    return {"messages": response}

@tool
def human_assitance(query):
    """Request Assitance from Human"""
    human_response = interrupt(
        f'query: {query}'
    )
    return human_response['data']

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
    model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
    model_with_tools = model.bind_tools([get_weather, human_assitance])

    # Step 2: Graph
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node(chatbot)
    graph_builder.add_node("tools", ToolNode([get_weather, human_assitance]))

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
    graph = graph_builder.compile(checkpointer=MemorySaver())

    # Step 3: Invocation
    config = {"configurable": {
        "thread_id": uuid.uuid4()
    }}

    while True:
        inp = input("User: ")
        if inp.lower() in ['exit', 'quit', 'q']:
            break
        messages = [
            {
                "role": 'user',
                "content": inp
            }
        ]

        response = graph.invoke({"messages": messages}, config=config)
        response['messages'][-1].pretty_print()

        if len(response['messages'][-1].tool_calls) == 0:
            continue

        else:
            if response['messages'][-1].tool_calls[0]['name'] == 'human_assitance':
                human_response = input("Human Intervention: ")
                human_command = Command(resume={"data": human_response})

                response = graph.invoke(human_command, config=config)
                response['messages'][-1].pretty_print()

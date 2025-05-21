from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from typing import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(msg: str):
    resp = model.invoke(msg["messages"])
    return {"messages": [resp]}

def human_review(state: State):
    application = f"Submitted application:\n{state['messages'][-1].content}\n"
    print(application)
    human_inp = interrupt(application)
    if human_inp['human_inp'] in ['y', 'yes', 'approve', 'approved']:
        return Command(goto="approve_application")
    else:
        return Command(goto="reject_application")

def approve_application(state):
    print("\nYou application is approved.")

def reject_application(state):
    print("\nYou application is rejected.")


if __name__ == "__main__":

    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 2: Graph
    graph_builder = StateGraph(State)
    graph_builder.add_node(chatbot)
    graph_builder.add_node(human_review)
    graph_builder.add_node(approve_application)
    graph_builder.add_node(reject_application)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "human_review")

    graph = graph_builder.compile(MemorySaver())

    # Step 3: Invoke
    config = {"configurable": {"thread_id": "123abc"}}

    msgs = [{
        "role": "user",
        "content": """I'm a policy holder of an insurance. 
                        Write shortest claim possible requesting 
                        the amount ranging between 10-100.
                        Fill all the placeholders like name etc. with any value."""
    }]
    graph.invoke({"messages": msgs},config=config)

    human_inp_decision = input("Do you approve or reject the claim?").lower().strip()
    graph.invoke(Command(resume={"human_inp": human_inp_decision}), config=config)

    
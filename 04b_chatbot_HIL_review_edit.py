from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from typing import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]
    company_total_liability: list

def chatbot(msg: str):
    resp = model.invoke(msg["messages"])
    return {"messages": [resp]}

def human_review(state: State):
    state['messages'][-1].pretty_print()
    human_inp = interrupt(f"Claim :\n{state['messages'][-1].content}\n")
    
    company_total_liability = human_inp['human_inp'] + sum([state.get("company_total_liability", 0.0)])
    return {"company_total_liability": company_total_liability}

def communicate(state: State):
    print("-*-"*50)
    print("The total Liability on the company is = ",state["company_total_liability"])
    print("-*-"*50)



if __name__ == "__main__":

    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 2: Graph
    graph_builder = StateGraph(State)
    graph_builder.add_node(chatbot)
    graph_builder.add_node(human_review)
    graph_builder.add_node(communicate)


    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "human_review")
    graph_builder.add_edge("human_review", "communicate")

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

    # First round
    graph.invoke({"messages": msgs},config=config)

    print("-*-"*50)
    human_inp_decision = float(input("Enter the amount that you want to approve for this claim: "))
    print("-*-"*50)
    graph.invoke(Command(resume={"human_inp": human_inp_decision}), config=config)

    # Second round
    graph.invoke({"messages": msgs},config=config)

    print("-*-"*50)
    human_inp_decision = float(input("Enter the amount that you want to approve for this claim: "))
    print("-*-"*50)
    graph.invoke(Command(resume={"human_inp": human_inp_decision}), config=config)

    
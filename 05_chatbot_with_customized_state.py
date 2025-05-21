from typing import Annotated, TypedDict, List, Literal

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]
    funny: Literal["y", 'n']
    rating: Literal[1, 2, 3, 4, 5]


def chatbot(msg: List[BaseMessage]):
    response = model.invoke(msg["messages"])
    return {"messages": [response]}


def human_review(state: State):
    "Get comments on joke if it is funny or not and how much it should be rated."
    print(
        f"The joke was: \n\t{state["messages"][-1].content}"
    )
    resp = interrupt("This only gets printed when it is tool called!")

    return {"funny": resp["funny"], "rating": resp["rating"]}

    
def publish(state: State):
    print(
        f"""Published joke: {state["messages"][-1].content}
            Funny: {state["funny"]}  
            Rating: {state["rating"]}
        """
    )



if __name__ == "__main__":


    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step2: Graph
    graph_builder = StateGraph(State)
    graph_builder.add_node(chatbot)
    graph_builder.add_node("human_review", human_review)
    graph_builder.add_node(publish)
    
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "human_review")
    graph_builder.add_edge("human_review", "publish")

    graph = graph_builder.compile(checkpointer=MemorySaver())

    # Step 3: Invoke
    config = {"configurable": {"thread_id": "123abc"}}
    print("You may ask the bot to crack a joke.")

    message = [{
        "role": "user",
        "content": "Tell me a joke on Mario"
    }]
    

    resp = graph.invoke({"messages": message}, config=config)

    resp_funny = input("Enter values for key 'funny'")
    resp_rating = input("Enter values for key 'rating'")
    graph.invoke(Command(resume={"funny": resp_funny, "rating": resp_rating}), config=config)
        


from pydantic import BaseModel, Field
from typing import Literal, TypedDict
from langgraph.graph import START, END, StateGraph
from langchain_ollama import ChatOllama

"""
                          +-----------+
                          | __start__ |
                          +-----------+
                                *
                                *
                                *
                    +-----------------------+
                    | router_classification |
                    +-----------------------+
                  ....          .          ....
              ....              .              ....
           ...                  .                  ...
+------------+           +------------+           +-------------+  
| write_joke |           | write_poem |           | write_story |  
+------------+****       +------------+        ***+-------------+  
                  ****          *          ****
                      ****      *      ****
                          ***   *   ***
                           +---------+
                           | __end__ |
                           +---------+
"""
# Router output format
class Route(BaseModel):
    route: Literal["joke", "story", "poem"] = Field(None, description="The next step in the workflow")

# Graph State
class State(TypedDict):
    inp: str
    decision: Literal["joke", "story", "poem"]
    out: str
    

# Graph Nodes
def write_joke(state: State):
    """This function writes a joke on a given topic"""
    msg = llm.invoke(f"Write a joke on topic: {state['inp']}")
    return {"out": msg.content}

def write_story(state: State):
    """This function writes a story on a given topic"""
    msg = llm.invoke(f"Write a story on topic: {state['inp']}")
    return {"out": msg.content}

def write_poem(state: State):
    """This function writes a poem on a given topic"""
    msg = llm.invoke(f"Write a poem on topic: {state['inp']}")
    return {"out": msg.content}

def router_classification(state: State):
    msgs = [
        {
            "role": "system",
            "content": "Route the input to write_joke, write_story or write_poem based on the user input"
        },
        {
            "role": "user",
            "content": state["inp"]
        }
    ]
    resp = llm_with_struct_out.invoke(msgs)
    return {"decision": resp.content}

def router_decision(state: State):
    if state["decision"] == "joke":
        return "write_joke"
    elif state["decision"] == "story":
        return "write_story"
    elif state["decision"] == "poem":
        return "write_poem"
    else:
        raise Exception("Unkown output")

if __name__ == "__main__":
    # Step 1: Model
    llm = ChatOllama(model="llama3.2:latest")
    llm_with_struct_out = llm.with_structured_output(Route)

    # Step 2: Graph
    workflow = StateGraph(State)
    workflow.add_node(router_classification)
    workflow.add_node("write_joke", write_joke)
    workflow.add_node("write_story", write_story)
    workflow.add_node("write_poem", write_poem)

    workflow.add_edge(START, "router_classification")
    workflow.add_conditional_edges(
        "router_classification", 
        router_decision,
        {
            "write_joke": "write_joke",
            "write_story": "write_story",
            "write_poem": "write_poem"
        }
    )

    workflow.add_edge("write_joke", END)
    workflow.add_edge("write_story", END)
    workflow.add_edge("write_poem", END)

    chain = workflow.compile()
    # print(chain.get_graph().draw_ascii())

    # # Step 3: Invoke
    state = chain.invoke({"topic": "Write a joke on dogs for me"})

    print(state)

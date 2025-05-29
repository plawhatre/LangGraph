from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from langchain_ollama import ChatOllama

"""
                          +-----------+
                          | __start__ |
                      ****+-----------+****
                  ****          *          ****
              ****              *              ****
           ***                  *                  ***
+------------+           +------------+           +-------------+  
| write_joke |           | write_poem |           | write_story |  
+------------+****       +------------+        ***+-------------+  
                  ****          *          ****
                      ****      *      ****
                          ***   *   ***
                         +------------+
                         | aggregator |
                         +------------+
                                *
                                *
                                *
                           +---------+
                           | __end__ |
                           +---------+
"""

# Graph State
class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str

# Graph Nodes
def write_joke(state: State):
    """This function writes a joke on a given topic"""
    msg = llm.invoke(f"Write a joke on topic: {state['topic']}")
    return {"joke": msg.content}

def write_story(state: State):
    """This function writes a story on a given topic"""
    msg = llm.invoke(f"Write a story on topic: {state['topic']}")
    return {"story": msg.content}

def write_poem(state: State):
    """This function writes a poem on a given topic"""
    msg = llm.invoke(f"Write a poem on topic: {state['topic']}")
    return {"poem": msg.content}

def aggregator(state: State):
    """It combines the joke, story and poem"""
    msg = f"Combine the joke, story and the poem on the topic {state['topic']}\n"
    msg += f"Joke:\n\t{state['joke']}"
    msg += f"Stroy:\n\t{state['story']}"
    msg += f"Poem:\n\t{state['poem']}"
    return {"combined_output": msg}

if __name__ == "__main__":
    # Step 1: Model
    llm = ChatOllama(model="llama3.2:latest")

    # Step 2: Graph
    workflow = StateGraph(State)
    workflow.add_node(write_joke)
    workflow.add_node(write_story)
    workflow.add_node(write_poem)
    workflow.add_node(aggregator)

    workflow.add_edge(START, "write_joke")
    workflow.add_edge(START, "write_story")
    workflow.add_edge(START, "write_poem")

    workflow.add_edge("write_joke", "aggregator")
    workflow.add_edge("write_story", "aggregator")
    workflow.add_edge("write_poem", "aggregator")

    workflow.add_edge("aggregator", END)

    chain = workflow.compile()
    # print(chain.get_graph().draw_ascii())

    # Step 3: Invoke
    state = chain.invoke({"topic": "dogs"})

    print(state)

from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from langchain_ollama import ChatOllama

"""
+-----------+
               | __start__ |
               +-----------+
                     *
                     *
                     *
             +---------------+
             | generate_joke |
             +---------------+
              ..           ..
            ..               ..
          ..                   ..
+--------------+                 ..
| improve_joke |                  .
+--------------+                  .
        *                         .
        *                         .
        *                         .
+-------------+                  ..
| polish_joke |                ..
+-------------+              ..
              **           ..
                **       ..
                  **   ..
                +---------+
                | __end__ |
                +---------+
"""

# Graph State
class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    polished_joke: str

# Nodes
def generate_joke(state: State):
    """This function generates joke onn a topic"""
    msg = model.invoke(f"Generate a joke on topic: {state['topic']}")
    return {"joke": msg.content}

def check_punchline(state: State):
    """Gate function to check if the joke has a punchline"""
    if "??" in state['joke'] or "!!" in state['joke']:
        return "Pass"
    return "Fail"

def improve_joke(state: State):
    """Improve the already generated joke"""
    msg = model.invoke(f"Make this joke funnier: {state['joke']}")
    return {"improved_joke": msg.content}

def polish_joke(state: State):
    """Polish the already improved joke"""
    msg = model.invoke(f"Polish the already improved joke: {state['joke']}")
    return {"polished_joke": msg.content}

if __name__ == "__main__":
    # Stage 1: model
    model = ChatOllama(model="llama3.2:latest")

    # Stage 2: Graph
    workflow = StateGraph(State)

    workflow.add_node(generate_joke)
    workflow.add_node(check_punchline)
    workflow.add_node(improve_joke)
    workflow.add_node(polish_joke)

    workflow.add_edge(START, "generate_joke")
    workflow.add_conditional_edges(
        "generate_joke",
        check_punchline,
        {
            "Pass": END,
            "Fail": "improve_joke"
        }
    )
    workflow.add_edge("improve_joke", "polish_joke")
    workflow.add_edge("polish_joke", END)

    chain = workflow.compile()
    # print(chain.get_graph().draw_ascii())

    # State 3: Invoke
    state = chain.invoke({"topic": "dogs"})
    print(f"Joke after first call:\n\t{state['joke']}")
    if "improved_joke" in state:
        print(f"Joke after second call:\n\t{state['improved_joke']}")
        print(f"Joke after third call:\n\t{state['polished_joke']}")
    else:
        print("Joke failed punchline check")
   
from typing import TypedDict, Literal
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END

"""
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
+-----------+  
| generator |
+-----------+
      *
      *
      *
+-----------+
| evaluator |
+-----------+
      .
      . (loop back to generator)
      .
 +---------+
 | __end__ |
 +---------+
"""


# Structured Output
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        "Decide if the joke is funny or not"
    )
    feedback: str = Field(
        "If the joke is not funny then provide feedback on how to improve the joke"
    )

# Graph State
class State(TypedDict):
    topic: str
    joke: str
    funny_or_not: str
    feedback: str

def generator(state: State):
    """
    This function generates the joke or 
    improves the already generated joke based on feedback
    """
    if state.get('feedback'):
        messages = [
            HumanMessage(
                f"Generate a joke on topic: {state['topic']}.\n"
                f"Also consider feedback:\n\t{state['feedback']}\n\n"
                f"on old joke:\n\t{state['joke']}"
            )
        ]
    else:
        messages = [
            HumanMessage(f"Generate a joke on topic: {state['topic']}.")
        ]
    resp = llm.invoke(messages).content
    return {"joke": resp}

def evaluator(state: State):
    """
    This function provides the feedback on the generated joke
    """
    messages = [
        HumanMessage(f"Provide a feedback on the joke: {state['joke']}")
    ]
    resp = llm_feedback.invoke(messages)
    return {"funny_or_not": resp.grade, "feedback": resp.feedback}

def router(state: State):
    """
    This function decides END the programme or 
    route it back to the generator based 
    on the feedback
    """
    if state['funny_or_not'] == "funny":
        return "Accept"
    else:
        return "Loop"


if __name__ == "__main__":
    # Step 1: Model
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    llm_feedback = llm.with_structured_output(Feedback)

    # Step 2: Graph
    workflow = StateGraph(State)
    workflow.add_node(generator)
    workflow.add_node(evaluator)

    workflow.add_edge(START, "generator")
    workflow.add_edge("generator", "evaluator")
    workflow.add_conditional_edges(
        "evaluator",
        router,
        {
            'Accept': END,
            'Loop': "generator"
        }
    )
    chain = workflow.compile()
    # print(chain.get_graph().draw_ascii()) 

    # Step 3: Invoke
    state = chain.invoke({"topic": "dogs"})
    print(state)

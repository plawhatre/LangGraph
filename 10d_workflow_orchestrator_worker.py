import operator
from typing import List, TypedDict, Annotated
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.constants import Send
from langgraph.graph import StateGraph, START, END

"""
  +-----------+  
  | __start__ |  
  +-----------+  
        *        
        *        
        *        
+--------------+ 
| orchestrator | 
+--------------+ 
        .        
        .        
        .        
  +-----------+  
  | llm_calls |  (# workers)
  +-----------+  
        *        
        *        
        *        
 +------------+
 | syntheizer |
 +------------+
        *
        *
        *
  +---------+
  | __end__ |
  +---------+
"""

# Structured Output
class Section(BaseModel):
    name: str = Field("Name for this section of this report")
    description: str = Field("Brief overview of the topics and concept covered in this section")

class Sections(BaseModel):
    sections: List[Section] = Field("List of sections in the report")

# Graph State
class State(TypedDict):
    topic: str
    sections: Sections
    completed_sections: Annotated[list, operator.add]
    final_report: str

# Worker State
class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[list, operator.add]

# Node
def orchestrator(state: State):
    "It generates the plan for the report"
    messages = [
        {
            "role": "system",
            "content": "Generate a plan for the report"
        },
        {
            "role": "user",
            "content": f"Here is the report topic: {state['topic']}"
        }
    ]
    report_sections = planner.invoke(messages)
    return {"sections": report_sections.sections}

def assign_workers(state: State):
    """Assign worker to each section of the plan"""
    return [Send("llm_calls", {"section": section}) for section in state['sections']]

def llm_calls(state: WorkerState):
    """Worker writes a section of the report"""
    messages = [
        {
            "role": "system",
            "content": (
                "Write a report section given name and description of the section."
                "Do not include preamble for each section."
                "Use Markdown formatting"
            )
        },
        {
            "role": "user",
            "content": f"Section Name: {state['section'].name} and Description: {state['section'].description}"
        }
    ]
    section = model.invoke(messages)
    return {"completed_sections": section.content}

def syntheizer(state: State):
    """It synthesizes full report from the sections"""
    completed_sections = "\n\n---\n\n".join(state['completed_sections'])
    return {"final_report": completed_sections}


if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    planner = model.with_structured_output(Sections)

    # Step 2: Graph
    workflow = StateGraph(State)

    workflow.add_node(orchestrator)
    workflow.add_node(llm_calls)
    workflow.add_node(syntheizer)

    workflow.add_edge(START, "orchestrator")
    workflow.add_conditional_edges(
        "orchestrator",
        assign_workers,
        ["llm_calls"]
    )
    workflow.add_edge("llm_calls", "syntheizer")
    workflow.add_edge("syntheizer", END)
    chain = workflow.compile()
    # print(chain.get_graph().draw_ascii())

    # Step 3: Invoke
    state = chain.invoke({"topic": "Create a report on LLM scaling laws"})
    print(state['final_report'])

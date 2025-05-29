from typing import Annotated, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage, HumanMessage

from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig


class CustomState(AgentState):
    user_name: str

def get_user_info(
        tool_call_id: Annotated[str, InjectedToolCallId],
        config: RunnableConfig,
        user_name: Optional[str]
) -> Command:
    """Get the user name if the HummanMessage or CustomState doesn't have it."""
    #Google models can't access config. So, using input to access the name directly
    if user_name == "": user_name = config["configurable"]["user_name"]
    return Command(
        goto="greet",
        update={
            "user_name": user_name,
            "messages": [
                ToolMessage(
                    "Successfully changed the custom state using tool calls",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

    

def greet(state: Annotated[CustomState, InjectedState]) -> str:
    """This function can greet the user"""
    user_name = state["user_name"]
    return f"Hello hello {user_name} !!"

if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)

    # Step 2: Agent
    prompt = """If you don't have user name then 
                call get_user_info function and then 
                call greet.
                If the user prompt doesn't have the name then 
                call get_user_info as well
            """
    agent = create_react_agent(
        model=model,
        tools=[get_user_info, greet],
        state_schema=CustomState,
        prompt=prompt
    )

    # Step 3: Invoke the agent with prompt
    config= {"configurable": {"thread_id": "123abc"}}
    msgs = [HumanMessage("Hi there. I'm Phantom")]
    resp = agent.invoke({"messages": msgs}, config=config)
    resp['messages'][-1].pretty_print()

    print("-.-"*30)

    config= {"configurable": {"thread_id": "123xyz", "user_name": "Prashant"}}
    msgs = [HumanMessage("Hi there")]
    resp = agent.invoke({"messages": msgs}, config=config)
    resp['messages'][-1].pretty_print()
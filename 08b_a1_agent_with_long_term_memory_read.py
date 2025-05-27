from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.config import get_store

class CustomState(AgentState):
    key: str

def get_user_info(state: CustomState) -> str:
    """Look up user info from LTM"""
    store = get_store(("users_namespace",), state["key"])
    values = store.get()
    return str(values.value) if values else "unkown user"

if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 2: Store
    store = InMemoryStore()
    store.put(
        ("users_namespace",), "user_key",
        {
            "name": "Prashant",
            "language": "Marathi"
        }
    )

    # Step 3: Agent
    prompt="""If ask about user information, 
            get it from the InMemoryStore using 
            tool calling get_user_info
        """
    agent = create_react_agent(
        model=model,
        tools=[get_user_info],
        store=store,
        state_schema=CustomState,
        prompt=prompt
    )

    # Step 4: Invoke
    config = {"configurable": {"thread_id": "123abc"}}
    messages = [{
        "role": "user",
        "content": "Get the user information"
    }]
    resp = agent.invoke({
        "messages": messages, 
        "key": "user_key"
    }, config=config)
    # resp["messages"][-1].pretty_print()
    for msg in resp["messages"]:
        msg.pretty_print()
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph.config import get_store


def get_user_info() -> str:
    """Look up user info from LTM"""
    key = input("Enter the Key for Long Term Memory:\n\t")
    store = get_store()
    values = store.get(("users_namespace",), key)
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
    agent = create_react_agent(
        model=model,
        tools=[get_user_info],
        store=store
    )

    # Step 4: Invoke
    config = {"configurable": {"thread_id": "123abc"}}
    messages = [{
        "role": "user",
        "content": "Get the user information"
    }]
    resp = agent.invoke({
        "messages": messages
    }, config=config)
    # resp["messages"][-1].pretty_print()
    for msg in resp["messages"]:
        msg.pretty_print()
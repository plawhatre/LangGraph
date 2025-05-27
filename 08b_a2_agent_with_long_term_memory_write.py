from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph.config import get_store

store = InMemoryStore()

class UserInfo(TypedDict):
    name: str
    language: str

def save_user_info(user_info: UserInfo) -> str:
    """Saves user info into LTM"""
    usr_key = input("Enter the Key for Long Term Memory:\n\t")
    store = get_store()
    values = store.put(("users_namespace",), usr_key, user_info)
    return "Successfully saved the values in Long-Term Memory"

if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")    

    # Step 2: Agent
    agent = create_react_agent(
        model=model,
        tools=[save_user_info],
        store=store
    )

    # Step 3: Invoke
    config = {"configurable": {"thread_id": "123abc"}}
    messages = [{
        "role": "user",
        "content": "My name is Phantom and I speak gibberish language"
    }]
    _ = agent.invoke({
        "messages": messages
    }, config=config)

    # Step 4: Access stored values
    print(str(store.get(("users_namespace",), "user_123").value))
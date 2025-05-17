import uuid
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import START, StateGraph, MessagesState

def chatbot(state: MessagesState):
    out = model.invoke(state['messages'])
    return {"messages": out}


if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model='gemini-1.5-flash')

    # Step 2: Graph
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, 'chatbot')
    graph = graph_builder.compile()

    # Step 3: Invocation
    while True:
        inp = input("User: ")
        if inp.lower() in ['quit', 'exit', 'q']:
            break
        prompt = [
            {
                "role": "user",
                "content": str(inp)
            }
        ]
        response = graph.invoke({"messages": prompt})
        response["messages"][-1].pretty_print()
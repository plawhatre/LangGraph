from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

def book_flight(source: str, destination: str):
    """Book a flight"""
    return f"Successfully booked your flight from {source} to {destination}"

def book_hotel(hotel_name: str):
    """Book the hotel"""
    return f"Successfully book your stay at {hotel_name}"

if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 2: Agents
    flight_agent = create_react_agent(
        model=model,
        tools=[book_flight],
        prompt="You are a flight booking assitant",
        name="flight_assistant"
    )

    hotel_agent = create_react_agent(
        model=model,
        tools=[book_hotel],
        prompt="You are a hotel booking assitant",
        name="hotel_assistant"
    )

    # Step 3: Supervisor Agent
    supervisor = create_supervisor(
        model=model,
        agents=[flight_agent, hotel_agent],
        prompt=(
            "You are a supervisor of two assistants who can book lights and hotels"
            "Assign work to them based on their role and capability"
        )
    ).compile()

    # Step 4: Invoke
    messages = [{
        "role": "user",
        "content": "Book a flight from Bangalore to Yangon and then book a stay at Wyndham hotel"
    }]
    resps = supervisor.invoke({"messages": messages})
    for resp in resps["messages"]:
        resp.pretty_print()


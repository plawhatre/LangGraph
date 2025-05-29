from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_swarm, create_handoff_tool

def book_flight(source: str, destination: str):
    """Book a flight"""
    return f"Successfully booked your flight from {source} to {destination}"

def book_hotel(hotel_name: str):
    """Book the hotel"""
    return f"Successfully book your stay at {hotel_name}"

if __name__ == "__main__":
    # Step 1: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 2: handoff tool
    transfer_to_flight_agent = create_handoff_tool(
        agent_name="flight_assistant",
        description="Transfer the user to flight booking assistant"
    )

    transfer_to_hotel_agent = create_handoff_tool(
        agent_name="hotel_assistant",
        description="Transfer the user to hotel booking assistant"
    )

    # Step 3: Agents
    flight_agent = create_react_agent(
        model=model,
        tools=[book_flight, transfer_to_hotel_agent],
        prompt="You are a flight booking assitant",
        name="flight_assistant"
    )

    hotel_agent = create_react_agent(
        model=model,
        tools=[book_hotel, transfer_to_flight_agent],
        prompt="You are a hotel booking assitant",
        name="hotel_assistant"
    )

    # Step 4: Swarm
    swarm = create_swarm(
        agents=[flight_agent, hotel_agent],
        default_active_agent="flight_assistant"
    ).compile()

    # Step 5: Invoke
    messages = [{
        "role": "user",
        "content": "Book a flight from Bangalore to Yangon and then book a stay at Wyndham hotel"
    }]
    resps = swarm.invoke({"messages": messages})
    for resp in resps["messages"]:
        resp.pretty_print()


import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


async def main():
    
    # Step 1: Client
    client = MultiServerMCPClient({
        "math":{
            "command": "python",
            "args": ["./07_MCP_server_math.py"],
            "transport": "stdio"
        },
        "weather":{
            "url": "https:localhost:8080/mcp",
            "transport": "streamable_http"
        }
    })

    # Step 2: Model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 3: Tools
    tools = await client.get_tools()

    # Step 3: Model and Agent
    agent  = create_react_agent(model=model, tools=tools)

    # Step 4: Query
    math_query = "What is 2 * 3 + 6 ?"
    math_result = await agent.ainvoke(
        {
            "messages": [{
                "role": "user",
                "content": math_query
        }]
        }
    )
    print(f"Query: {math_query}")
    print(f"Result: {math_result}")

    weather_query = "What is the present weather condition in Mumbai?"
    weather_result = await agent.ainvoke(
        {
            "messages": [{
                "role": "user",
                "content": weather_query
        }]
        }
    )
    print(f"Query: {weather_query}")
    print(f"Result: {weather_result}")



if __name__ == "__main__":
    asyncio.run(main())
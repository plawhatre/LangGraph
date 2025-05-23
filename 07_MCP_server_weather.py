import mcp
from mcp.server.fastmcp import FastMCP

mcp =FastMCP("Weather")

@mcp.tool()
async def get_weather(city: str) -> str:
    """This tool return the weather condition of the city for which query is made"""
    city = city.capitalize()
    forecast ={
        "Delhi": {
            "Temperature": '41°C', 
            "Outlook": "with hazy conditions"
        },
        "Mumbai": {
            "Temperature": '31°C', 
            "Outlook": "experiencing haze"
        },
        "Chennai": {
            "Temperature": '34°C', 
            "Outlook": "with light rain"
        },
        "Kolkata": {
            "Temperature": '37°C', 
            "Outlook": "mostly sunny with some haze"
        },
        "Default": {
            "Temperature": 'unkown',
            "Outlook": 'unkown'

        }
    }
    city_forecast = forecast.get(city, forecast.get('Default'))
    return f"The weather in {city} is {city_forecast['Temperature']} {city_forecast['Outlook']}."



if __name__ == "__main__":
    print("Starting MCP weather Server.")
    mcp.run(transport="streamable-http")
    print("MCP Weather Server started")

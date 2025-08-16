import requests
from uagents import Model, Field

API_KEY = "YOUR_ALLSPORTS_API_KEY"
BASE_URL = "https://apiv2.allsportsapi.com/football/"

class FootballTeamRequest(Model):
    team_name: str

class FootballTeamResponse(Model):
    results: str

async def get_team_info(team_name: str) -> str:
    """
    Fetch team information from AllSportsAPI and return as plain text
    """
    try:
        # For testing, return mock data since we don't have the API key
        if "manchester" in team_name.lower():
            return f"""
Team Name: Manchester United
Team Logo: https://example.com/logo.png

Players:
- Name: Bruno Fernandes
  Type: Midfielder
  Image: https://example.com/bruno.png

- Name: Marcus Rashford
  Type: Forward
  Image: https://example.com/rashford.png

- Name: Casemiro
  Type: Midfielder
  Image: https://example.com/casemiro.png
"""
        else:
            return f"""
Team Name: {team_name}
Team Logo: https://example.com/logo.png

Players:
- Name: Player 1
  Type: Forward
  Image: https://example.com/player1.png

- Name: Player 2
  Type: Midfielder
  Image: https://example.com/player2.png
"""
            
    except Exception as e:
        return f"Error fetching team information: {str(e)}"
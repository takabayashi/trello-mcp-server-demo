from mcp.server.fastmcp import FastMCP
import requests
import json
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Trello MCP Server Demo")

# Trello API configuration
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BASE_URL = "https://api.trello.com/1"

# Validate required environment variables
if not TRELLO_API_KEY or not TRELLO_TOKEN:
    raise ValueError(
        "Missing required environment variables. Please set TRELLO_API_KEY and TRELLO_TOKEN "
        "in your .env file or environment variables. See .env.example for reference."
    )

def get_boards():
    """Get all boards for the authenticated user"""
    url = f"{TRELLO_BASE_URL}/members/me/boards"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching boards: {str(e)}")

def get_board_by_name(board_name: str):
    """Find a board by name"""
    boards = get_boards()
    
    for board in boards:
        if board['name'].lower() == board_name.lower():
            return board
    
    raise Exception(f"Board '{board_name}' not found")

def get_lists_for_board(board_id: str):
    """Get all lists for a specific board"""
    url = f"{TRELLO_BASE_URL}/boards/{board_id}/lists"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching board lists: {str(e)}")

@mcp.tool()
def create_trello_list(board_name: str, list_name: str, position: Optional[str] = "bottom") -> dict:
    """
    Create a new list in a specific Trello board
    
    Args:
        board_name: Name of the Trello board
        list_name: Name of the list to create
        position: Position of the list ('top', 'bottom', or a number)
    
    Returns:
        dict: Information about the created list
    """
    try:
        # Find the board by name
        board = get_board_by_name(board_name)
        board_id = board['id']
        
        # Check if list already exists
        existing_lists = get_lists_for_board(board_id)
        for lst in existing_lists:
            if lst['name'].lower() == list_name.lower():
                return {
                    "success": False,
                    "error": f"List '{list_name}' already exists in board '{board_name}'"
                }
        
        # Create the list
        url = f"{TRELLO_BASE_URL}/lists"
        params = {
            'name': list_name,
            'idBoard': board_id,
            'pos': position,
            'key': TRELLO_API_KEY,
            'token': TRELLO_TOKEN
        }
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        list_data = response.json()
        
        return {
            "success": True,
            "list_id": list_data['id'],
            "list_name": list_data['name'],
            "board_name": board_name,
            "position": list_data.get('pos', position)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.resource("lists://{board_name}")
def list_trello_lists(board_name: str) -> dict:
    """
    List all lists in a specific Trello board
    
    Args:
        board_name: Name of the Trello board
    
    Returns:
        dict: List of lists with their names and IDs
    """
    try:
        # Find the board by name
        board = get_board_by_name(board_name)
        board_id = board['id']
        
        # Get lists for the board
        lists = get_lists_for_board(board_id)
        list_data = []
        
        for lst in lists:
            list_data.append({
                "id": lst['id'],
                "name": lst['name'],
                "position": lst.get('pos', 0),
                "closed": lst.get('closed', False)
            })
        
        return {
            "success": True,
            "board_name": board_name,
            "lists": list_data,
            "count": len(list_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def create_trello_card(board_name: str, card_name: str, description: Optional[str] = None, list_name: Optional[str] = None) -> dict:
    """
    Create a Trello card in a specific board
    
    Args:
        board_name: Name of the Trello board
        card_name: Name/title of the card to create
        description: Optional description for the card
        list_name: Optional name of the list to add the card to (defaults to first list)
    
    Returns:
        dict: Information about the created card
    """
    try:
        # Find the board by name
        board = get_board_by_name(board_name)
        board_id = board['id']
        
        # Get lists for the board
        lists = get_lists_for_board(board_id)
        
        if not lists:
            raise Exception(f"No lists found in board '{board_name}'")
        
        # Determine which list to use
        list_id = None
        if list_name:
            # Find the specified list
            for lst in lists:
                if lst['name'].lower() == list_name.lower():
                    list_id = lst['id']
                    break
            if not list_id:
                raise Exception(f"List '{list_name}' not found in board '{board_name}'")
        else:
            # Use the first list (usually "To Do")
            list_id = lists[0]['id']
        
        # Create the card
        url = f"{TRELLO_BASE_URL}/cards"
        params = {
            'idList': list_id,
            'name': card_name,
            'key': TRELLO_API_KEY,
            'token': TRELLO_TOKEN
        }
        
        if description:
            params['desc'] = description
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        card_data = response.json()
        
        return {
            "success": True,
            "card_id": card_data['id'],
            "card_name": card_data['name'],
            "card_url": card_data['url'],
            "board_name": board_name,
            "list_name": next((lst['name'] for lst in lists if lst['id'] == list_id), "Unknown")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.resource("boards://all")
def list_trello_boards() -> dict:
    """
    List all available Trello boards for the authenticated user
    
    Returns:
        dict: List of boards with their names and IDs
    """
    try:
        boards = get_boards()
        board_list = []
        
        for board in boards:
            board_list.append({
                "id": board['id'],
                "name": board['name'],
                "url": board['url']
            })
        
        return {
            "success": True,
            "boards": board_list,
            "count": len(board_list)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    mcp.run()

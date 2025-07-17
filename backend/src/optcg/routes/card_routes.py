from fastapi import APIRouter, HTTPException
import logging
import requests
import os

# Custom Imports
from optcg import state
from optcg.models import CardSearchRequest

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
async def card_search(request: CardSearchRequest):
    """Search for cards in the One Piece TCG database with API TCG. Returns a list of cards matching the search criteria."""
    api_key = os.getenv("APITCG_API_KEY")
    url = "https://apitcg.com/api/one-piece/cards/"
    headers = {"x-api-key": api_key}
    
    # Build query parameters, filtering out None values
    params = {}
    if request.query:
        params["name"] = request.query
    if request.set:
        params["code"] = request.set
    if request.type:
        params["type"] = request.type
    if request.cost is not None: # Allows for cost to be 0
        params["cost"] = request.cost
    if request.power is not None: # Allows for power to be 0
        params["power"] = request.power
    if request.counter:
        params["counter"] = request.counter
    if request.color:
        params["color"] = request.color
    if request.family:
        params["family"] = request.family
    if request.ability:
        params["ability"] = request.ability
    if request.trigger:
        params["trigger"] = request.trigger
    
    try:
        logger.debug(f"Searching cards with params: {params}")
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            logger.error(f"Card search failed with status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=f"Error searching cards: {response.status_code}")
        data = response.json()
        if data.get("error"):
            logger.error(f"API TCG returned error for card search: {data['error']}")
            raise HTTPException(status_code=400, detail=f"Error searching cards: {data['error']}")
        if not data.get("data"):
            logger.error("API TCG called but no cards found (empty data)")
            raise HTTPException(status_code=404, detail="No cards found matching the search criteria")
        return data
    except requests.RequestException as e:
        logger.exception(f"Error contacting API TCG: {e}")
        raise HTTPException(status_code=502, detail="Error contacting API TCG")

@router.get("/{card_id}")
async def get_card(card_id: str):
    """Get details of a specific card by ID from API TCG"""
    api_key = os.getenv("APITCG_API_KEY")
    url = f"https://apitcg.com/api/one-piece/cards/{card_id}"
    headers = {"x-api-key": api_key}

    try:
        logger.debug(f"Fetching card {card_id} from {url}")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Card not found: {card_id}, status code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching card data: {response.status_code}")
        data = response.json()
        if data.get("error"):
            logger.error(f"API TCG returned error for card {card_id}: {data['error']}")
            raise HTTPException(status_code=404, detail=f"Error fetching card data: {data['error']}")
        if not data.get("data"):
            logger.error(f"API TCG called and card not found (empty data): {card_id}")
            raise HTTPException(status_code=404, detail="Card not found")
        return data
    except requests.RequestException as e:
        logger.exception(f"Error contacting API TCG: {e}")
        raise HTTPException(status_code=502, detail="Error contacting API TCG")
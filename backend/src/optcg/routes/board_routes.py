from fastapi import APIRouter, HTTPException
import logging

# Custom Imports
from optcg import state
from optcg.schemas import BoardState

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
async def set_board_state(board_state: dict): # TODO: add type: BoardState
    """Save the current board state for the session"""
    state.current_board_state = board_state
    logger.debug("Board state saved")
    return {"status": "Board state saved successfully"}

@router.get("/") 
async def get_board_state():
    """Get the current board state"""
    if state.current_board_state is None:
        logger.debug("No board state found. Returning 404.")
        raise HTTPException(status_code=404, detail="No board state found. Please update the board state first.")
    return state.current_board_state

@router.delete("/")
async def clear_board_state():
    """Clear the current board state"""
    logger.debug("Clearing board state")
    state.current_board_state = None
    return {"status": "Board state cleared"}
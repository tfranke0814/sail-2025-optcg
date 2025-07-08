from pydantic import BaseModel
from typing import Optional, List

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    agent_type: str

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    agent_type: str

class CardSearchRequest(BaseModel):
    query: Optional[str] = None # Query by name of a card
    set: Optional[str] = None # Set code, e.g. "OP01"
    # rarity: Optional[str] = None # "C" returns both "C", "UC", and "SEC"... similarly with "R"
    type: Optional[str] = None
    cost: Optional[int] = None
    power: Optional[int] = None
    counter: Optional[str] = None # Counter value, e.g. "1000" or "-" for no counter
    color: Optional[str] = None
    family: Optional[str] = None
    ability: Optional[str] = None
    trigger: Optional[str] = None
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

class CardImages(BaseModel):
    small: str
    large: str

class CardAttribute(BaseModel):
    name: str
    image: str

class CardSet(BaseModel):
    name: str

class CardData(BaseModel):
    id: str
    code: str
    rarity: str
    type: str
    name: str
    images: CardImages
    cost: Optional[int] = None # Can be null
    attribute: CardAttribute
    power: Optional[int] = None # Can be null
    counter: str
    color: str
    family: str
    ability: str
    trigger: str
    set: CardSet
    notes: List # List[str] -- if list vals are all str

class PlayerState(BaseModel):
    life: int
    don: int
    leader: Optional[CardData] = None
    event: Optional[CardData] = None
    stage: Optional[List[CardData]] = None
    character: Optional[List[CardData]] = None

class BoardState(BaseModel):
    UserState: PlayerState
    OpponentState: PlayerState

"""Schemas for the analysis agent"""

from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import TypedDict, Literal
from langgraph.graph import MessagesState

class AnalysisStateInput(MessagesState):
    user_message: str

class AnalysisState(MessagesState):
    user_message: str
    board: dict | None
    extraction: Optional[List[str]]
    retrieval: Optional[str] 

class AnalysisExtractorSchema(BaseModel):
    queries: List[str]

class AnalysisRouterSchema(BaseModel):
    rule_retrieval: bool
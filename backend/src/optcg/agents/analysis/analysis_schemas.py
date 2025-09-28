"""Schemas for the analysis agent"""

from pydantic import BaseModel
from typing import Optional, List
from langgraph.graph import MessagesState

class AnalysisStateInput(MessagesState):
    user_message: str

class AnalysisState(MessagesState):
    board: dict | None
    extraction: Optional[List[str]]
    retrieval: Optional[str] 

class AnalysisExtractorSchema(BaseModel):
    queries: List[str]

class AnalysisRouterSchema(BaseModel):
    rule_retrieval: bool
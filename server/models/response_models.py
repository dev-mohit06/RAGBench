from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryResponse(BaseModel):
    query: str
    architecture: str
    response: str
    context: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time: float

class ComparisonResponse(BaseModel):
    query: str
    results: List[QueryResponse]
    total_processing_time: float

class DocumentStatus(BaseModel):
    status: str
    message: str
    document_count: Optional[int] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    available_architectures: List[str]

class ArchitectureInfo(BaseModel):
    architectures: List[str]
    descriptions: Dict[str, str]
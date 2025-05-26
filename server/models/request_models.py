from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question")
    architectures: List[str] = Field(
        default=["simple"], 
        description="List of RAG architectures to use (simple, reranking, hyde)"
    )
    k: int = Field(default=5, description="Number of documents to retrieve")
    show_context: bool = Field(default=True, description="Whether to return retrieved context")
    
    # Architecture-specific parameters
    rerank_top_k: Optional[int] = Field(default=5, description="Top K for reranking")
    rerank_weight: Optional[float] = Field(default=0.6, description="Reranking weight")
    hyde_doc_length: Optional[str] = Field(default="medium", description="HyDE document length")
    use_original_query: Optional[bool] = Field(default=False, description="Use original query with HyDE")
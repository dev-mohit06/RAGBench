from rags.BaseRag import BaseRAG

from rags.implementations._simpleRAG import Simpleragsystem
from rags.implementations._rerankingRAG import Rerankingragsystem
from rags.implementations._HyDERAG import HyDEragsystem

class ragsystemFactory:
    """Factory class to create different types of RAG systems."""
    
    @staticmethod
    def create_rag_system(
        rag_type: str = "simple",
        **kwargs
    ) -> BaseRAG:
        """
        Create a RAG system of the specified type.
        
        Args:
            rag_type: Type of RAG system ("simple", "reranking", "hyde")
            **kwargs: Arguments to pass to the RAG system constructor
            
        Returns:
            Instance of the specified RAG system
        """
        rag_type = rag_type.lower()
        
        if rag_type == "simple":
            return Simpleragsystem(**kwargs)
        elif rag_type == "reranking":
            return Rerankingragsystem(**kwargs)
        elif rag_type == "hyde":
            return HyDEragsystem(**kwargs)
        else:
            raise ValueError(f"Unknown RAG type: {rag_type}. Choose from: simple, reranking, hyde")
from .BaseRag import BaseRAG

from .implementations._simpleRAG import SimpleRAGSystem
from .implementations._rerankingRAG import RerankingRAGSystem
from .implementations._HyDERAG import HyDERAGSystem

class RAGSystemFactory:
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
            return SimpleRAGSystem(**kwargs)
        elif rag_type == "reranking":
            return RerankingRAGSystem(**kwargs)
        elif rag_type == "hyde":
            return HyDERAGSystem(**kwargs)
        else:
            raise ValueError(f"Unknown RAG type: {rag_type}. Choose from: simple, reranking, hyde")
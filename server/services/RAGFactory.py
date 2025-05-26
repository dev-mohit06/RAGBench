from RAGs.BaseRag import BaseRAG

from RAGs.implementations._simpleRAG import SimpleRAGsystem
from RAGs.implementations._rerankingRAG import RerankingRAGsystem
from RAGs.implementations._HyDERAG import HyDERAGsystem

class RAGsystemFactory:
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
            return SimpleRAGsystem(**kwargs)
        elif rag_type == "reranking":
            return RerankingRAGsystem(**kwargs)
        elif rag_type == "hyde":
            return HyDERAGsystem(**kwargs)
        else:
            raise ValueError(f"Unknown RAG type: {rag_type}. Choose from: simple, reranking, hyde")
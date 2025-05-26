# controllers/controller_factory.py
from services.rag_service import RAGservice
from controllers.rag_controller import RAGController

class ControllerFactory:
    """Factory for creating controllers with their dependencies"""
    
    @staticmethod
    def create_rag_controller() -> RAGController:
        """Create RAG controller with all dependencies"""
        rag_service = RAGservice()
        return RAGController(rag_service)
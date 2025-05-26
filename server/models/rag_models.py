from typing import Dict, Any, List
from abc import ABC, abstractmethod

class RAGsystemInterface(ABC):
    """Interface for RAG systems"""
    
    @abstractmethod
    def chat(self, query: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def add_documents(self, file_paths: List[str]) -> None:
        pass
    
    @abstractmethod
    def clear_documents(self) -> None:
        pass

class DocumentProcessor:
    """Model for document processing operations"""
    
    def __init__(self):
        self.status = "not_initialized"
        self.message = "No documents processed yet"
        self.document_count = None
        self.processing_time = None
    
    def set_processing(self, file_count: int):
        self.status = "processing"
        self.message = f"Processing {file_count} documents..."
    
    def set_completed(self, file_count: int, processing_time: float):
        self.status = "completed"
        self.message = f"Successfully processed {file_count} documents for all RAG systems"
        self.document_count = file_count
        self.processing_time = processing_time
    
    def set_failed(self, error_message: str):
        self.status = "failed"
        self.message = f"Document processing failed: {error_message}"
    
    def set_cleared(self):
        self.status = "cleared"
        self.message = "All documents cleared from RAG systems"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "document_count": self.document_count,
            "processing_time": self.processing_time
        }
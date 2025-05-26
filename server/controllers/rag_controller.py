# controllers/rag_controller.py
from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from typing import List

from services.rag_service import RAGService
from models.request_models import QueryRequest
from models.response_models import (
    QueryResponse, ComparisonResponse, DocumentStatus, 
    HealthResponse, ArchitectureInfo
)

class RAGController:
    """Controller for handling RAG-related HTTP requests"""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all routes for the controller"""
        self.router.get("/health", response_model=HealthResponse)(self.health_check)
        self.router.post("/upload-documents", response_model=DocumentStatus)(self.upload_documents)
        self.router.get("/status", response_model=DocumentStatus)(self.get_processing_status)
        self.router.post("/query", response_model=ComparisonResponse)(self.query_rag_systems)
        self.router.get("/architectures")(self.get_available_architectures)
        self.router.delete("/documents")(self.clear_documents)
    
    async def health_check(self) -> HealthResponse:
        """Health check endpoint"""
        return self.rag_service.get_health_status()
    
    async def upload_documents(
            self,
            background_tasks: BackgroundTasks,
            files: List[UploadFile] = File(...)
        ) -> DocumentStatus:
            """Upload and process PDF documents"""
            # Validate files
            self.rag_service.validate_upload_files(files)
            
            # Read file content immediately while files are still open
            file_data = await self.rag_service.read_upload_files(files)
            
            # Start processing in background with file data (not file objects)
            background_tasks.add_task(self.rag_service.process_documents_from_data, file_data)
            
            return self.rag_service.start_document_processing(len(files))
    
    async def get_processing_status(self) -> DocumentStatus:
        """Get document processing status"""
        return self.rag_service.get_processing_status()
    
    async def query_rag_systems(self, request: QueryRequest) -> ComparisonResponse:
        """Query one or more RAG architectures"""
        return self.rag_service.query_multiple_architectures(request)
    
    async def get_available_architectures(self):
        """Get list of available RAG architectures"""
        return self.rag_service.get_architecture_info()
    
    async def clear_documents(self):
        """Clear all processed documents from RAG systems"""
        return self.rag_service.clear_all_documents()


# controllers/base_controller.py
from abc import ABC, abstractmethod
from fastapi import APIRouter

class BaseController(ABC):
    """Base controller class with common functionality"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    @abstractmethod
    def _setup_routes(self):
        """Setup routes - must be implemented by subclasses"""
        pass
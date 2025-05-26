# services/rag_service.py
import logging
import time
import os
import tempfile
from typing import Dict, Any, List
from fastapi import HTTPException, UploadFile

from models.rag_models import RAGSystemInterface, DocumentProcessor
from models.request_models import QueryRequest
from models.response_models import QueryResponse, ComparisonResponse, DocumentStatus, HealthResponse, ArchitectureInfo
from RAGs.RAGFactory import RAGSystemFactory

logger = logging.getLogger(__name__)

class RAGService:
    """Service class containing business logic for RAG operations"""
    
    def __init__(self):
        self.rag_systems: Dict[str, RAGSystemInterface] = {}
        self.document_processor = DocumentProcessor()
        self.available_architectures = ["simple", "reranking", "hyde"]
        self.architecture_descriptions = {
            "simple": "Basic RAG with retrieval and generation",
            "reranking": "RAG with semantic reranking for improved relevance", 
            "hyde": "RAG using Hypothetical Document Embeddings for enhanced retrieval"
        }
    
    def initialize_rag_systems(self) -> bool:
        """Initialize all RAG systems"""
        try:
            for arch in self.available_architectures:
                logger.info(f"Initializing {arch} RAG system...")
                self.rag_systems[arch] = RAGSystemFactory.create_rag_system(
                    rag_type=arch,
                    # Add your initialization parameters here
                    # vector_store_path=os.getenv("VECTOR_STORE_PATH", "./vector_store"),
                    # llm_model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
                    # embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
                )
            
            logger.info("All RAG systems initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing RAG systems: {str(e)}")
            return False
    
    def get_health_status(self) -> HealthResponse:
        """Get health status of the service"""
        from datetime import datetime
        return HealthResponse(
            status="healthy" if self.rag_systems else "unhealthy",
            timestamp=datetime.now().isoformat(),
            available_architectures=list(self.rag_systems.keys())
        )
    
    def validate_upload_files(self, files: List[UploadFile]) -> None:
        """Validate uploaded files"""
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type: {file.filename}. Only PDF files are supported."
                )
    
    def start_document_processing(self, file_count: int) -> DocumentStatus:
        """Start document processing"""
        self.document_processor.set_processing(file_count)
        return DocumentStatus(
            status="accepted",
            message=f"Started processing {file_count} documents. Check /status for updates."
        )
    
    async def read_upload_files(self, files: List[UploadFile]) -> List[Dict[str, Any]]:
        """Read uploaded files and return their content with metadata"""
        file_data = []
        
        for file in files:
            try:
                # Read file content immediately while file is still open
                content = await file.read()
                
                if not content:
                    raise ValueError(f"File {file.filename} is empty or could not be read")
                
                file_info = {
                    "filename": file.filename,
                    "content": content,
                    "content_type": file.content_type,
                    "size": len(content)
                }
                file_data.append(file_info)
                logger.info(f"Read {len(content)} bytes from {file.filename}")
                
            except Exception as e:
                logger.error(f"Error reading file {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Error reading file {file.filename}: {str(e)}"
                )
        
        return file_data
    
    async def process_documents_from_data(self, file_data: List[Dict[str, Any]]) -> None:
        """Process documents from pre-read file data"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing {len(file_data)} documents...")
            
            # Create temporary directory for files
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            # Save file data to temporary files
            for file_info in file_data:
                file_path = os.path.join(temp_dir, file_info["filename"])
                
                try:
                    # Write content to temporary file
                    with open(file_path, "wb") as buffer:
                        buffer.write(file_info["content"])
                    file_paths.append(file_path)
                    
                except Exception as file_error:
                    logger.error(f"Error saving file {file_info['filename']}: {str(file_error)}")
                    # Clean up any partial files
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise
            
            # Verify files were created successfully
            for file_path in file_paths:
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                    raise ValueError(f"Failed to create temporary file: {file_path}")
            
            # Process documents for each RAG system
            for arch_name, rag_system in self.rag_systems.items():
                logger.info(f"Processing documents for {arch_name} RAG system...")
                rag_system.index_document(file_paths)
            
            # Clean up temporary files
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
            processing_time = time.time() - start_time
            self.document_processor.set_completed(len(file_data), processing_time)
            
            logger.info(f"Document processing completed in {processing_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            self.document_processor.set_failed(str(e))
            # Clean up temporary directory if it exists
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                try:
                    for file_path in file_paths:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    os.rmdir(temp_dir)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary files: {str(cleanup_error)}")
            raise

    async def process_documents(self, files: List[UploadFile]) -> None:
        """Process uploaded documents - DEPRECATED: Use read_upload_files + process_documents_from_data instead"""
        # This method is kept for backward compatibility but should not be used
        # with background tasks due to file closure issues
        logger.warning("process_documents method is deprecated for background tasks. Use read_upload_files + process_documents_from_data instead.")
        
        # Read files first
        file_data = await self.read_upload_files(files)
        # Process from data
        await self.process_documents_from_data(file_data)
    
    def get_processing_status(self) -> DocumentStatus:
        """Get document processing status"""
        return DocumentStatus(**self.document_processor.to_dict())
    
    def validate_query_request(self, request: QueryRequest) -> None:
        """Validate query request"""
        if not self.rag_systems:
            raise HTTPException(status_code=503, detail="RAG systems not initialized")
        
        invalid_archs = [arch for arch in request.architectures if arch not in self.rag_systems]
        print(invalid_archs)
        if invalid_archs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid architectures: {invalid_archs}. Available: {list(self.rag_systems.keys())}"
            )
    
    def _extract_response_text(self, response: Any) -> str:
        """Extract text response from various response formats"""
        if isinstance(response, str):
            return response
        elif isinstance(response, dict):
            # Handle dictionary responses
            if 'response' in response:
                return str(response['response'])
            elif 'answer' in response:
                return str(response['answer'])
            elif 'result' in response:
                return str(response['result'])
            elif 'text' in response:
                return str(response['text'])
            else:
                # If it's a dict but doesn't have expected keys, convert to string
                return str(response)
        elif hasattr(response, 'content'):
            # Handle response objects with content attribute
            return str(response.content)
        else:
            # Fallback: convert to string
            return str(response)
    
    def query_architecture(self, architecture: str, request: QueryRequest) -> QueryResponse:
        """Query a specific architecture"""
        arch_start_time = time.time()
        
        try:
            rag_system = self.rag_systems[architecture]
            
            # Architecture-specific query logic
            if architecture == "simple":
                raw_response = rag_system.chat(
                    query=request.query,
                    show_context=False,
                    k=request.k
                )
                context_docs = rag_system.search(request.query, k=request.k)
                
            elif architecture == "reranking":
                raw_response = rag_system.chat(
                    query=request.query,
                    show_context=False,
                    show_scores=False,
                    k=request.k,
                    rerank_top_k=request.rerank_top_k,
                    use_reranking=True
                )
                context_docs = rag_system.search_with_reranking(
                    query=request.query,
                    k=request.k,
                    rerank_top_k=request.rerank_top_k,
                    use_reranking=True,
                    rerank_weight=request.rerank_weight
                )
                
            elif architecture == "hyde":
                raw_response = rag_system.chat(
                    query=request.query,
                    show_context=False,
                    show_hypothetical=False,
                    k=request.k,
                    use_original_query=request.use_original_query,
                    doc_length=request.hyde_doc_length
                )
                context_docs = rag_system.search_with_hyde(
                    query=request.query,
                    k=request.k,
                    use_original_query=request.use_original_query,
                    doc_length=request.hyde_doc_length
                )
            
            # Extract the actual text response from whatever format is returned
            response_text = self._extract_response_text(raw_response)
            
            processing_time = time.time() - arch_start_time
            
            # Prepare context for response
            context = self._prepare_context(context_docs, architecture, request.show_context)
            
            # Prepare metadata
            metadata = self._prepare_metadata(architecture, request, context_docs, processing_time)
            
            return QueryResponse(
                query=request.query,
                architecture=architecture,
                response=response_text,  # Now guaranteed to be a string
                context=context,
                metadata=metadata,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error querying {architecture}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error querying {architecture} architecture: {str(e)}"
            )
    
    def query_multiple_architectures(self, request: QueryRequest) -> ComparisonResponse:
        """Query multiple RAG architectures"""
        self.validate_query_request(request)
        
        start_time = time.time()
        results = []
        
        for architecture in request.architectures:
            result = self.query_architecture(architecture, request)
            results.append(result)
        
        total_processing_time = time.time() - start_time
        
        return ComparisonResponse(
            query=request.query,
            results=results,
            total_processing_time=total_processing_time
        )
    
    def get_architecture_info(self) -> ArchitectureInfo:
        """Get available architectures information"""
        return ArchitectureInfo(
            architectures=list(self.rag_systems.keys()),
            descriptions=self.architecture_descriptions
        )
    
    def clear_all_documents(self) -> Dict[str, str]:
        """Clear all documents from RAG systems"""
        try:
            for arch_name, rag_system in self.rag_systems.items():
                if hasattr(rag_system, 'clear_documents'):
                    rag_system.clear_documents()
                elif hasattr(rag_system, 'vector_store'):
                    if hasattr(rag_system.vector_store, 'delete_collection'):
                        rag_system.vector_store.delete_collection()
            
            self.document_processor.set_cleared()
            return {"message": "Documents cleared successfully"}
            
        except Exception as e:
            logger.error(f"Error clearing documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")
    
    def _prepare_context(self, context_docs: List[Dict[str, Any]], architecture: str, show_context: bool) -> List[Dict[str, Any]]:
        """Prepare context for response"""
        if not show_context:
            return []
        
        context = []
        for doc in context_docs:
            doc_context = {
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}),
                "score": doc.get("score"),
                "page": doc.get("metadata", {}).get("page"),
            }
            
            # Add architecture-specific fields
            if architecture == "reranking":
                doc_context.update({
                    "original_score": doc.get("original_score"),
                    "semantic_score": doc.get("semantic_score"),
                    "reranked": doc.get("reranked", False)
                })
            elif architecture == "hyde":
                doc_context.update({
                    "hypothetical_doc": doc.get("hypothetical_doc")
                })
            
            context.append(doc_context)
        
        return context
    
    def _prepare_metadata(self, architecture: str, request: QueryRequest, context_docs: List[Dict[str, Any]], processing_time: float) -> Dict[str, Any]:
        """Prepare metadata for response"""
        metadata = {
            "architecture": architecture,
            "parameters": {"k": request.k},
            "document_count": len(context_docs),
            "processing_time": processing_time
        }
        
        # Add architecture-specific parameters
        if architecture == "reranking":
            metadata["parameters"].update({
                "rerank_top_k": request.rerank_top_k,
                "rerank_weight": request.rerank_weight
            })
        elif architecture == "hyde":
            metadata["parameters"].update({
                "use_original_query": request.use_original_query
            })
            # Only add hyde_doc_length if it exists in the request
            if hasattr(request, 'hyde_doc_length'):
                metadata["parameters"]["hyde_doc_length"] = request.hyde_doc_length
        
        return metadata
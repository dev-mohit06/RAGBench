# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import uvicorn

from controllers.controller_factory import ControllerFactory
from services.rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure env variables
load_dotenv()

class RAGApplication:
    """Main application class that orchestrates the MVC components"""
    
    def __init__(self):
        self.app = FastAPI(
            title="RAG Comparison Playground API",
            description="API for comparing different RAG architectures",
            version="1.0.0"
        )
        self.rag_service = RAGService()
        self._setup_middleware()
        self._setup_controllers()
        self._setup_events()
    
    def _setup_middleware(self):
        """Setup application middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_controllers(self):
        """Setup controllers and their routes"""
        # Create RAG controller
        rag_controller = ControllerFactory.create_rag_controller()
        
        # Include controller routes
        self.app.include_router(
            rag_controller.router,
            prefix="/api/v1",
            tags=["RAG Operations"]
        )
        
        # Store reference to service for startup event
        self.rag_service = rag_controller.rag_service
    
    def _setup_events(self):
        """Setup application events"""
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize RAG systems on startup"""
            logger.info("Starting RAG Comparison API...")
            success = self.rag_service.initialize_rag_systems()
            if not success:
                logger.error("Failed to initialize RAG systems")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown"""
            logger.info("Shutting down RAG Comparison API...")

# Create application instance
rag_app = RAGApplication()
app = rag_app.app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
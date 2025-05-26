import os
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from sklearn.metrics.pairwise import cosine_similarity

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import JinaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseRAG(ABC):
    """
    Abstract base class for RAG systems.
    
    Provides common functionality for document indexing, vector storage setup,
    and basic operations that all RAG implementations need.
    """
    
    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        embedding_model: str = "jina-embeddings-v3",
        collection_name: str = "demo_collection",
        chunk_size: int = 500,
        chunk_overlap: int = 20,
        temperature: float = 0.5,
        use_memory_store: bool = True
    ):
        """
        Initialize the base RAG system.
        
        Args:
            model_name: The LLM model to use
            embedding_model: The embedding model to use
            collection_name: Name for the vector store collection
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            temperature: LLM temperature
            use_memory_store: Whether to use in-memory vector store
        """
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.temperature = temperature
        self.use_memory_store = use_memory_store
        
        # Initialize components
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.client = None
        
        # Document storage
        self.indexed_documents = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components."""
        try:
            # Initialize LLM
            logger.info("Initializing LLM...")
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature
            )
            
            # Initialize embeddings
            logger.info("Initializing embeddings...")
            jina_api_key = os.getenv("JINA_API_KEY")
            if not jina_api_key:
                raise ValueError("JINA_API_KEY not found in environment variables!")
                
            self.embeddings = JinaEmbeddings(
                jina_api_key=jina_api_key,
                model_name=self.embedding_model
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            
            # Initialize vector store
            self._setup_vector_store()
            
            logger.info("All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            raise
    
    def _setup_vector_store(self):
        """Setup the vector store with dynamic embedding dimensions."""
        try:
            logger.info("Setting up vector store...")
            
            if self.use_memory_store:
                self.client = QdrantClient(":memory:")
            else:
                self.client = QdrantClient(":memory:")
            
            # Get embedding dimension dynamically
            test_embedding = self.embeddings.embed_query("test")
            embedding_dim = len(test_embedding)
            logger.info(f"Embedding dimension: {embedding_dim}")
            
            # Create collection if it doesn't exist
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
                )
            except Exception:
                # Collection might already exist
                pass
            
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )
            
            logger.info("Vector store setup complete!")
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {str(e)}")
            raise
    
    def index_document(
        self,
        file_path: Union[str, List[str]],
        metadata: Dict[str, Any] = None,
        verbose: bool = True
    ) -> str:
        """
        Index a single document or multiple documents into the vector store.
        
        Args:
            file_path: Path to the document to index, or list of paths
            metadata: Additional metadata to store
            verbose: Whether to show progress
            
        Returns:
            Success message with indexing details
        """
        try:
            # Handle both single file and list of files
            if isinstance(file_path, list):
                # If it's a list, process each file
                results = []
                for single_path in file_path:
                    try:
                        result = self._index_single_document(single_path, metadata, verbose)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error indexing {single_path}: {str(e)}")
                        results.append(f"Failed to index {single_path}: {str(e)}")
                
                return f"Processed {len(file_path)} files. Results: " + "; ".join(results)
            else:
                # Single file
                return self._index_single_document(file_path, metadata, verbose)
                
        except Exception as e:
            error_msg = f"Error indexing document(s): {str(e)}"
            logger.error(error_msg)
            raise
    
    def _index_single_document(
        self,
        file_path: str,
        metadata: Dict[str, Any] = None,
        verbose: bool = True
    ) -> str:
        """
        Index a single document into the vector store.
        
        Args:
            file_path: Path to the document to index
            metadata: Additional metadata to store
            verbose: Whether to show progress
            
        Returns:
            Success message with indexing details
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logger.info(f"Loading document: {file_path}")
            
            # Load document
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()
            
            if not documents:
                raise ValueError("No documents loaded from PDF!")
            
            logger.info(f"Loaded {len(documents)} pages from PDF")
            
            # Split into chunks
            logger.info("Splitting documents into chunks...")
            chunks = self.text_splitter.split_documents(documents)
            
            if not chunks:
                raise ValueError("No chunks created!")
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Add metadata
            document_name = os.path.basename(file_path)
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'document_name': document_name,
                    'chunk_index': i,
                    'chunk_id': str(uuid.uuid4()),
                    'source_path': file_path
                })
                if metadata:
                    chunk.metadata.update(metadata)
            
            # Add to vector store
            logger.info("Adding documents to vector store...")
            self.vector_store.add_documents(chunks)
            
            # Store document info
            self.indexed_documents[document_name] = {
                'path': file_path,
                'chunks': len(chunks),
                'pages': len(documents),
                'metadata': metadata or {}
            }
            
            success_msg = f"Successfully indexed '{document_name}': {len(chunks)} chunks from {len(documents)} pages"
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            error_msg = f"Error indexing document {file_path}: {str(e)}"
            logger.error(error_msg)
            raise
    
    def index_documents(
        self,
        file_paths: List[str],
        metadata: Dict[str, Any] = None,
        verbose: bool = True
    ) -> List[str]:
        """
        Index multiple documents into the vector store.
        
        Args:
            file_paths: List of paths to documents to index
            metadata: Additional metadata to store
            verbose: Whether to show progress
            
        Returns:
            List of success/error messages for each document
        """
        results = []
        for file_path in file_paths:
            try:
                result = self._index_single_document(file_path, metadata, verbose)
                results.append(result)
            except Exception as e:
                error_msg = f"Failed to index {file_path}: {str(e)}"
                logger.error(error_msg)
                results.append(error_msg)
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the current RAG system state."""
        try:
            total_docs = len(self.indexed_documents)
            total_chunks = sum(doc['chunks'] for doc in self.indexed_documents.values())
            
            return {
                'indexed_documents': total_docs,
                'total_chunks': total_chunks,
                'collection_name': self.collection_name,
                'model_name': self.model_name,
                'embedding_model': self.embedding_model,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'documents': list(self.indexed_documents.keys()),
                'rag_type': self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            logger.info(f"Searching for: '{query}'")
            
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
            docs = retriever.get_relevant_documents(query)
            
            results = []
            for doc in docs:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': getattr(doc, 'score', None)
                })
            
            logger.info(f"Found {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
    
    def generate_response(
        self,
        query: str,
        context_docs: List[Dict[str, Any]] = None,
        custom_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Generate a response using retrieved context.
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            custom_prompt: Custom prompt template
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Retrieve context if not provided
            if context_docs is None:
                context_docs = self.search(query)
            
            if not context_docs:
                return {
                    'response': "I couldn't find relevant information to answer your question.",
                    'context_used': [],
                    'sources': []
                }
            
            # Prepare context
            context = "\n\n".join([doc['content'] for doc in context_docs])
            
            # Create prompt
            if custom_prompt is None:
                prompt_template = PromptTemplate(
                    input_variables=["context", "question"],
                    template="""
                    You are an AI assistant. Use the following context to answer the user's question accurately and concisely.

                    Context:
                    {context}

                    Question:
                    {question}

                    Answer based on the provided context. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing or limited.
                    """
                )
            else:
                prompt_template = PromptTemplate(
                    input_variables=["context", "question"],
                    template=custom_prompt
                )
            
            # Generate response
            final_prompt = prompt_template.format(context=context, question=query)
            response = self.llm.invoke(final_prompt)
            
            # Prepare sources
            sources = []
            for doc in context_docs:
                sources.append({
                    'document': doc['metadata'].get('document_name', 'Unknown'),
                    'chunk_index': doc['metadata'].get('chunk_index', 0),
                    'chunk_id': doc['metadata'].get('chunk_id', 'Unknown')
                })
            
            return {
                'response': response.content,
                'context_used': [doc['content'] for doc in context_docs],
                'sources': sources,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    @abstractmethod
    def chat(self, query: str, **kwargs) -> str:
        """
        Abstract method for chat interface.
        Each RAG implementation should provide its own chat method.
        """
        pass
    
    def interactive_chat(self):
        """Start an interactive chat session."""
        print(f"{self.__class__.__name__} Interactive Chat")
        print("Commands: 'quit', 'exit', 'info', 'help'")
        print("="*50)
        
        while True:
            try:
                query = input("\nEnter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                    
                if query.lower() == 'info':
                    info = self.get_system_info()
                    print(f"\nSystem Information:")
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                    continue
                    
                if query.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  - Type any question to get an answer")
                    print("  - 'info' - Show system information")
                    print("  - 'quit' or 'exit' - Exit the chat")
                    continue
                
                if not query:
                    print("Please enter a valid query.")
                    continue
                
                # Process query using the specific implementation
                response = self.chat(query, show_context=True)
                
                print(f"\nANSWER:")
                print(response)
                print("="*50)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
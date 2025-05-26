from RAGs.BaseRag import BaseRAG

class SimpleRAGSystem(BaseRAG):
    """
    Simple RAG implementation using basic retrieval and generation.
    
    This is the standard RAG approach: retrieve relevant documents
    and generate responses based on the retrieved context.
    """
    
    def chat(self, query: str, show_context: bool = False, k: int = 5) -> str:
        """
        Simple chat interface for querying the RAG system.
        
        Args:
            query: User query
            show_context: Whether to display retrieved context
            k: Number of documents to retrieve
            
        Returns:
            Generated response
        """
        try:
            # Search for relevant documents
            context_docs = self.search(query, k=k)
            
            if show_context and context_docs:
                print("\n" + "="*50)
                print("RETRIEVED CONTEXT (Simple RAG):")
                for i, doc in enumerate(context_docs, 1):
                    print(f"\n--- Document {i} ---")
                    print(f"Source: {doc['metadata'].get('document_name', 'Unknown')}")
                    print(f"Content: {doc['content'][:200]}...")
                print("="*50)
            
            # Generate response
            result = self.generate_response(query, context_docs)
            
            return result
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
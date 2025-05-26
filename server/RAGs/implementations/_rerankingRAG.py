from ..BaseRag import BaseRAG
from typing import List,Dict,Any
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RerankingRAGSystem(BaseRAG):
    """
    RAG system with semantic reranking.
    
    Enhances retrieval by reranking documents using semantic similarity
    between the query and document embeddings.
    """
    
    def semantic_rerank(
        self, 
        query: str, 
        retrieved_docs: List[Dict[str, Any]], 
        top_k: int = None,
        rerank_weight: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Semantic reranking function.
        
        Reranks retrieved documents using semantic similarity between query and document embeddings.
        Combines original retrieval scores with semantic similarity scores.
        
        Args:
            query: The user query
            retrieved_docs: List of documents from search() with 'content' and 'metadata' keys
            top_k: Number of top documents to return (None returns all)
            rerank_weight: Weight for semantic score vs original score (0.0-1.0)
            
        Returns:
            List of reranked documents with updated scores
        """
        try:
            if not retrieved_docs:
                logger.info("No documents to rerank")
                return retrieved_docs
            
            logger.info(f"Reranking {len(retrieved_docs)} documents using semantic similarity")
            
            # Get query embedding
            query_embedding = np.array(self.embeddings.embed_query(query))
            
            # Get document embeddings
            doc_texts = [doc['content'] for doc in retrieved_docs]
            doc_embeddings = np.array(self.embeddings.embed_documents(doc_texts))
            
            # Compute cosine similarities
            similarities = cosine_similarity([query_embedding], doc_embeddings).flatten()
            
            # Create reranked documents with combined scores
            reranked_docs = []
            for i, doc in enumerate(retrieved_docs):
                # Get original score (default to position-based if not available)
                original_score = doc.get('score', 1.0 - (i * 0.1))
                semantic_score = similarities[i]
                
                # Combine scores: weighted average
                final_score = (1 - rerank_weight) * original_score + rerank_weight * semantic_score
                
                # Create new document dict with updated score
                reranked_doc = doc.copy()
                reranked_doc.update({
                    'score': final_score,
                    'original_score': original_score,
                    'semantic_score': semantic_score,
                    'reranked': True
                })
                
                reranked_docs.append(reranked_doc)
            
            # Sort by final score (descending)
            reranked_docs.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top_k if specified
            if top_k:
                reranked_docs = reranked_docs[:top_k]
            
            logger.info(f"Reranking complete. Returning {len(reranked_docs)} documents")
            
            return reranked_docs
            
        except Exception as e:
            logger.warning(f"Semantic reranking failed: {str(e)}. Returning original order.")
            return retrieved_docs
    
    def search_with_reranking(
        self, 
        query: str, 
        k: int = 10, 
        rerank_top_k: int = 5,
        use_reranking: bool = True,
        rerank_weight: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Enhanced search function that includes semantic reranking.
        
        Args:
            query: Search query
            k: Number of documents to initially retrieve
            rerank_top_k: Number of top documents to return after reranking
            use_reranking: Whether to apply semantic reranking
            rerank_weight: Weight for semantic score in final ranking
            
        Returns:
            List of documents, optionally reranked
        """
        try:
            # Initial retrieval
            logger.info(f"Searching for: '{query}' (retrieving {k} documents)")
            
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
            docs = retriever.get_relevant_documents(query)
            
            if not docs:
                logger.info("No documents found")
                return []
            
            # Convert to dictionary format
            retrieved_docs = []
            for i, doc in enumerate(docs):
                retrieved_docs.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': getattr(doc, 'score', 1.0 - (i * 0.1))  # Fallback scoring
                })
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            # Apply semantic reranking if enabled
            if use_reranking:
                retrieved_docs = self.semantic_rerank(
                    query, 
                    retrieved_docs, 
                    top_k=rerank_top_k,
                    rerank_weight=rerank_weight
                )
            elif rerank_top_k:
                # Just limit results without reranking
                retrieved_docs = retrieved_docs[:rerank_top_k]
            
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error during search with reranking: {str(e)}")
            raise
    
    def chat(
        self, 
        query: str, 
        show_context: bool = False, 
        show_scores: bool = False,
        k: int = 10,
        rerank_top_k: int = 5,
        use_reranking: bool = True
    ) -> str:
        """
        Enhanced chat interface with semantic reranking.
        
        Args:
            query: User query
            show_context: Whether to display retrieved context
            show_scores: Whether to show reranking scores
            k: Initial retrieval count
            rerank_top_k: Documents to return after reranking
            use_reranking: Whether to apply semantic reranking
            
        Returns:
            Generated response string
        """
        try:
            # Get reranked documents
            context_docs = self.search_with_reranking(
                query, 
                k=k, 
                rerank_top_k=rerank_top_k,
                use_reranking=use_reranking
            )
            
            if show_context and context_docs:
                print("\n" + "="*60)
                print(f"RETRIEVED CONTEXT (Reranking: {'ON' if use_reranking else 'OFF'})")
                print("="*60)
                
                for i, doc in enumerate(context_docs, 1):
                    print(f"\n--- Document {i} ---")
                    print(f"Source: {doc['metadata'].get('document_name', 'Unknown')}")
                    
                    if show_scores and doc.get('reranked'):
                        print(f"Final Score: {doc['score']:.4f}")
                        print(f"Original Score: {doc.get('original_score', 0):.4f}")
                        print(f"Semantic Score: {doc.get('semantic_score', 0):.4f}")
                    elif show_scores:
                        print(f"Score: {doc.get('score', 0):.4f}")
                    
                    print(f"Content: {doc['content'][:200]}...")
                print("="*60)
            
            # Generate response
            result = self.generate_response(query, context_docs)
            
            return result['response']
        
        except Exception as e:
            return f"Error processing query: {str(e)}"

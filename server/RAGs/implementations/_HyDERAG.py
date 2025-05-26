from rags.BaseRag import BaseRAG
from langchain.prompts import PromptTemplate
from typing import List,Dict,Any

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HyDEragsystem(BaseRAG):
    """
    RAG system using Hypothetical Document Embeddings (HyDE).
    
    Enhances retrieval by first generating a hypothetical document
    that would answer the query, then using this document for retrieval.
    """
    
    def generate_hypothetical_document(self, query: str, doc_length: str = "medium") -> str:
        """
        Generate a hypothetical document that would answer the query.
        This is the core of HyDE - creating a fake document for better retrieval.
        """
        length_prompts = {
            "short": "Write a brief, concise answer (2-3 sentences)",
            "medium": "Write a comprehensive answer (1-2 paragraphs)", 
            "long": "Write a detailed, thorough answer (3-4 paragraphs)"
        }
        
        hyde_prompt = PromptTemplate(
            input_variables=["question", "length_instruction"],
            template="""
            You are an expert assistant. Given the following question, write a hypothetical document that would perfectly answer this question. 
            
            {length_instruction} that directly addresses the question as if you were writing content that would be found in a knowledge base or document collection.
            
            Question: {question}
            
            Hypothetical Document:
            """
        )
        
        prompt = hyde_prompt.format(
            question=query, 
            length_instruction=length_prompts[doc_length]
        )
        
        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def search_with_hyde(
        self, 
        query: str, 
        k: int = 5,
        use_original_query: bool = False,
        hyde_weight: float = 1.0,
        doc_length: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Search using HyDE approach - generate hypothetical document first.
        """
        try:
            # Generate hypothetical document
            logger.info(f"Generating hypothetical document for: '{query}'")
            hypothetical_doc = self.generate_hypothetical_document(query, doc_length)
            
            logger.info(f"Hypothetical document: {hypothetical_doc[:100]}...")
            
            if use_original_query:
                # Combine original query with hypothetical document
                search_text = f"{query}\n\n{hypothetical_doc}"
            else:
                # Use only hypothetical document for search
                search_text = hypothetical_doc
            
            # Perform retrieval using hypothetical document
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
            docs = retriever.get_relevant_documents(search_text)
            
            # Convert to dictionary format
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': getattr(doc, 'score', 1.0 - (i * 0.1)),
                    'retrieved_with': 'hyde',
                    'hypothetical_doc': hypothetical_doc
                })
            
            logger.info(f"HyDE search found {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error in HyDE search: {str(e)}")
            raise
    
    def chat(
        self,
        query: str,
        show_context: bool = False,
        show_hypothetical: bool = False,
        k: int = 5,
        use_original_query: bool = False,
        doc_length: str = "medium"
    ) -> str:
        """
        Chat interface using HyDE approach.
        
        Args:
            query: User query
            show_context: Whether to display retrieved context
            show_hypothetical: Whether to show the generated hypothetical document
            k: Number of documents to retrieve
            use_original_query: Whether to combine original query with hypothetical doc
            doc_length: Length of hypothetical document
            
        Returns:
            Generated response string
        """
        try:
            # Generate hypothetical document and search
            context_docs = self.search_with_hyde(
                query,
                k=k,
                use_original_query=use_original_query,
                doc_length=doc_length
            )
            
            # Show hypothetical document if requested
            if show_hypothetical and context_docs:
                hypothetical_doc = context_docs[0].get('hypothetical_doc', '')
                if hypothetical_doc:
                    print(f"\n{'='*60}")
                    print("GENERATED HYPOTHETICAL DOCUMENT:")
                    print(f"{'='*60}")
                    print(hypothetical_doc)
                    print(f"{'='*60}")
            
            # Show context if requested
            if show_context and context_docs:
                print("\n" + "="*60)
                print("RETRIEVED CONTEXT (HyDE RAG):")
                print("="*60)
                
                for i, doc in enumerate(context_docs, 1):
                    print(f"\n--- Document {i} ---")
                    print(f"Source: {doc['metadata'].get('document_name', 'Unknown')}")
                    print(f"Content: {doc['content'][:200]}...")
                print("="*60)
            
            # Generate response
            result = self.generate_response(query, context_docs)
            
            return result['response']
        
        except Exception as e:
            return f"Error processing query: {str(e)}"


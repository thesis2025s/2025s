"""
Vector store management for Finance Specialist AI.
Handles conversation memory, knowledge base storage, and semantic search.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

import chromadb
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config import settings

logger = logging.getLogger(__name__)


class FinancialVectorStore:
    """
    Vector store manager for financial AI system.
    Handles conversation memory, knowledge base, and document storage.
    """
    
    def __init__(self):
        """Initialize the vector store manager."""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.api_keys.openai_api_key,
            model=settings.model_config.embedding_model
        )
        
        # Initialize Chroma client
        self.chroma_client = chromadb.PersistentClient(
            path=settings.database_config.chroma_persist_directory
        )
        
        # Initialize collections
        self.conversation_store = self._init_conversation_store()
        self.knowledge_store = self._init_knowledge_store()
        self.document_store = self._init_document_store()
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        logger.info("FinancialVectorStore initialized successfully")
    
    def _init_conversation_store(self) -> Chroma:
        """Initialize conversation memory store."""
        try:
            collection_name = "financial_conversations"
            
            return Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            logger.error(f"Error initializing conversation store: {e}")
            raise
    
    def _init_knowledge_store(self) -> Chroma:
        """Initialize financial knowledge base store."""
        try:
            collection_name = "financial_knowledge"
            
            return Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            logger.error(f"Error initializing knowledge store: {e}")
            raise
    
    def _init_document_store(self) -> Chroma:
        """Initialize document store for uploaded files."""
        try:
            collection_name = "financial_documents"
            
            return Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            logger.error(f"Error initializing document store: {e}")
            raise
    
    def store_conversation(
        self, 
        user_query: str, 
        ai_response: str, 
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store conversation exchange in vector store."""
        try:
            # Create conversation document
            conversation_text = f"User: {user_query}\n\nAssistant: {ai_response}"
            
            # Prepare metadata
            conv_metadata = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query,
                "ai_response": ai_response,
                "type": "conversation"
            }
            
            if metadata:
                conv_metadata.update(metadata)
            
            # Create document
            document = Document(
                page_content=conversation_text,
                metadata=conv_metadata
            )
            
            # Store in conversation store
            self.conversation_store.add_documents([document])
            
            logger.info(f"Stored conversation for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    def retrieve_relevant_conversations(
        self, 
        query: str, 
        session_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant past conversations."""
        try:
            # Build filter
            filter_dict = {"type": {"$eq": "conversation"}}
            if session_id:
                filter_dict["session_id"] = {"$eq": session_id}
            
            # Search for relevant conversations
            results = self.conversation_store.similarity_search(
                query,
                k=limit,
                filter=filter_dict
            )
            
            # Format results
            conversations = []
            for doc in results:
                conversations.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error retrieving conversations: {e}")
            return []
    
    def store_knowledge(self, content: str, category: str, metadata: Optional[Dict] = None) -> None:
        """Store financial knowledge or insights."""
        try:
            # Prepare metadata
            knowledge_metadata = {
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "type": "knowledge"
            }
            
            if metadata:
                knowledge_metadata.update(metadata)
            
            # Create document
            document = Document(
                page_content=content,
                metadata=knowledge_metadata
            )
            
            # Store in knowledge store
            self.knowledge_store.add_documents([document])
            
            logger.info(f"Stored knowledge in category: {category}")
            
        except Exception as e:
            logger.error(f"Error storing knowledge: {e}")
    
    def search_knowledge(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search financial knowledge base."""
        try:
            # Build filter
            filter_dict = {"type": {"$eq": "knowledge"}}
            if category:
                filter_dict["category"] = {"$eq": category}
            
            # Search knowledge base
            results = self.knowledge_store.similarity_search(
                query,
                k=limit,
                filter=filter_dict
            )
            
            # Format results
            knowledge_items = []
            for doc in results:
                knowledge_items.append({
                    "content": doc.page_content,
                    "category": doc.metadata.get("category", "general"),
                    "metadata": doc.metadata
                })
            
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []
    
    def store_document(self, file_content: str, filename: str, file_type: str) -> None:
        """Store and process uploaded documents."""
        try:
            # Split document into chunks
            chunks = self.text_splitter.split_text(file_content)
            
            # Create documents for each chunk
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                    "type": "document"
                }
                
                document = Document(
                    page_content=chunk,
                    metadata=doc_metadata
                )
                documents.append(document)
            
            # Store all chunks
            self.document_store.add_documents(documents)
            
            logger.info(f"Stored document {filename} in {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error storing document: {e}")
    
    def search_documents(self, query: str, filename: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search uploaded documents."""
        try:
            # Build filter
            filter_dict = {"type": {"$eq": "document"}}
            if filename:
                filter_dict["filename"] = {"$eq": filename}
            
            # Search documents
            results = self.document_store.similarity_search(
                query,
                k=limit,
                filter=filter_dict
            )
            
            # Format results
            document_chunks = []
            for doc in results:
                document_chunks.append({
                    "content": doc.page_content,
                    "filename": doc.metadata.get("filename", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "metadata": doc.metadata
                })
            
            return document_chunks
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get recent conversation history for a session."""
        try:
            filter_dict = {
                "session_id": {"$eq": session_id},
                "type": {"$eq": "conversation"}
            }
            
            # Get all conversations for session
            all_results = self.conversation_store.get(
                where=filter_dict,
                limit=limit
            )
            
            # Sort by timestamp and format
            conversations = []
            if all_results and all_results['documents']:
                for i, doc in enumerate(all_results['documents']):
                    metadata = all_results['metadatas'][i] if all_results['metadatas'] else {}
                    conversations.append({
                        "content": doc,
                        "timestamp": metadata.get("timestamp", ""),
                        "metadata": metadata
                    })
                
                # Sort by timestamp (newest first)
                conversations.sort(
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True
                )
            
            return conversations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def clear_session_data(self, session_id: str) -> None:
        """Clear all data for a specific session."""
        try:
            # Delete conversations for this session
            self.conversation_store.delete(
                where={"session_id": {"$eq": session_id}}
            )
            
            logger.info(f"Cleared session data for {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session data: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            stats = {}
            
            # Get conversation count
            conv_count = self.conversation_store._collection.count()
            stats["conversations"] = conv_count
            
            # Get knowledge count
            knowledge_count = self.knowledge_store._collection.count()
            stats["knowledge_items"] = knowledge_count
            
            # Get document count
            doc_count = self.document_store._collection.count()
            stats["document_chunks"] = doc_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# Global vector store instance
vector_store = None

def get_vector_store() -> FinancialVectorStore:
    """Get or create global vector store instance."""
    global vector_store
    if vector_store is None:
        vector_store = FinancialVectorStore()
    return vector_store
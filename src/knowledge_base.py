"""
Financial Knowledge Base with RAG (Retrieval Augmented Generation)
Provides contextual financial information to enhance AI responses
"""
import os
import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid

from config import settings

logger = logging.getLogger(__name__)

class FinancialKnowledgeBase:
    """Financial knowledge base for RAG implementation"""
    
    def __init__(self):
        """Initialize the knowledge base"""
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("financial_knowledge")
        except:
            self.collection = self.client.create_collection("financial_knowledge")
            self._populate_initial_knowledge()
    
    def _populate_initial_knowledge(self):
        """Populate the knowledge base with initial financial concepts"""
        
        financial_concepts = [
            {
                "id": "pe_ratio",
                "title": "Price-to-Earnings Ratio (P/E)",
                "content": """The Price-to-Earnings ratio (P/E) is a valuation metric that compares a company's current share price to its earnings per share (EPS). It's calculated as: P/E = Market Price per Share / Earnings per Share. A high P/E might indicate that investors expect higher earnings growth in the future compared to companies with a lower P/E. However, it could also suggest the stock is overvalued. Generally, P/E ratios between 15-25 are considered reasonable for most industries.""",
                "category": "valuation"
            },
            {
                "id": "dcf_analysis",
                "title": "Discounted Cash Flow (DCF) Analysis",
                "content": """DCF analysis is a valuation method that estimates the value of an investment based on its expected future cash flows. The analysis discounts future cash flows back to present value using a discount rate (usually the weighted average cost of capital). DCF is considered one of the most fundamental valuation methods as it's based on the intrinsic value of cash flows rather than market comparisons.""",
                "category": "valuation"
            },
            {
                "id": "risk_management",
                "title": "Portfolio Risk Management",
                "content": """Risk management involves identifying, analyzing, and mitigating potential losses in investment portfolios. Key principles include diversification across asset classes, sectors, and geographies; position sizing to limit exposure to any single investment; stop-loss orders to limit downside; and regular portfolio rebalancing. The risk-return tradeoff is fundamental - higher potential returns typically come with higher risk.""",
                "category": "risk_management"
            },
            {
                "id": "technical_analysis",
                "title": "Technical Analysis Basics",
                "content": """Technical analysis involves studying price charts and trading patterns to make investment decisions. Key concepts include support and resistance levels, moving averages (SMA, EMA), relative strength index (RSI), MACD, and volume analysis. Technical analysts believe that historical price movements and patterns tend to repeat, making them useful for predicting future price movements.""",
                "category": "technical_analysis"
            },
            {
                "id": "fundamental_analysis",
                "title": "Fundamental Analysis",
                "content": """Fundamental analysis evaluates a security's intrinsic value by examining related economic, financial, and other qualitative and quantitative factors. For stocks, this includes analyzing financial statements (income statement, balance sheet, cash flow), industry trends, competitive position, management quality, and economic conditions. The goal is to determine if a stock is overvalued, undervalued, or fairly valued.""",
                "category": "fundamental_analysis"
            },
            {
                "id": "market_cycles",
                "title": "Market Cycles and Economic Indicators",
                "content": """Markets move in cycles influenced by economic conditions, investor sentiment, and monetary policy. Key economic indicators include GDP growth, unemployment rates, inflation (CPI), interest rates, and yield curves. Bull markets are characterized by rising prices and optimism, while bear markets feature declining prices and pessimism. Understanding these cycles helps in timing investment decisions.""",
                "category": "market_analysis"
            },
            {
                "id": "options_basics",
                "title": "Options Trading Fundamentals",
                "content": """Options are financial derivatives that give the holder the right (but not obligation) to buy or sell an underlying asset at a specific price (strike price) before expiration. Call options profit when the underlying rises above the strike price, while put options profit when it falls below. Options can be used for speculation, hedging, or income generation through strategies like covered calls.""",
                "category": "derivatives"
            },
            {
                "id": "bond_analysis",
                "title": "Bond Investment Analysis",
                "content": """Bonds are debt securities that pay regular interest and return principal at maturity. Key factors in bond analysis include credit quality (credit ratings), duration (interest rate sensitivity), yield to maturity, and the yield curve. Interest rate risk is primary - when rates rise, bond prices fall. Credit risk involves the possibility of default by the issuer.""",
                "category": "fixed_income"
            },
            {
                "id": "portfolio_theory",
                "title": "Modern Portfolio Theory",
                "content": """Modern Portfolio Theory, developed by Harry Markowitz, suggests that investors can construct portfolios to maximize expected return for a given level of risk. Key concepts include diversification benefits, efficient frontier, correlation between assets, and the capital asset pricing model (CAPM). The theory emphasizes that risk can be reduced through proper diversification without necessarily reducing expected returns.""",
                "category": "portfolio_theory"
            },
            {
                "id": "financial_statements",
                "title": "Financial Statement Analysis",
                "content": """The three main financial statements are the income statement (shows revenue, expenses, and profit), balance sheet (shows assets, liabilities, and equity at a point in time), and cash flow statement (shows cash inflows and outflows). Key ratios include profitability ratios (ROE, ROA), liquidity ratios (current ratio, quick ratio), and leverage ratios (debt-to-equity, interest coverage).""",
                "category": "financial_analysis"
            }
        ]
        
        # Add documents to the collection
        for concept in financial_concepts:
            self.add_knowledge(
                content=concept["content"],
                metadata={
                    "title": concept["title"],
                    "category": concept["category"],
                    "id": concept["id"]
                }
            )
        
        logger.info("Populated knowledge base with initial financial concepts")
    
    def add_knowledge(self, content: str, metadata: Dict = None) -> str:
        """
        Add new knowledge to the knowledge base
        
        Args:
            content: The knowledge content
            metadata: Optional metadata for the content
            
        Returns:
            The document ID
        """
        try:
            doc_id = str(uuid.uuid4())
            
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Add to collection
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            logger.info(f"Added knowledge document with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            return ""
    
    def search(self, query: str, n_results: int = 3) -> str:
        """
        Search the knowledge base for relevant information
        
        Args:
            query: The search query
            n_results: Number of results to return
            
        Returns:
            Relevant knowledge context
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'][0]:
                return ""
            
            # Format results
            context_parts = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                if distance < 0.8:  # Only include relevant results
                    title = metadata.get('title', f'Knowledge {i+1}')
                    context_parts.append(f"**{title}**: {doc}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return ""
    
    def get_knowledge_by_category(self, category: str) -> List[Dict]:
        """
        Get all knowledge items in a specific category
        
        Args:
            category: The category to filter by
            
        Returns:
            List of knowledge items
        """
        try:
            # ChromaDB doesn't have direct category filtering in community version
            # So we'll search with a category-specific query
            results = self.collection.query(
                query_texts=[category],
                n_results=50,  # Get more results to filter
                include=["documents", "metadatas"]
            )
            
            filtered_results = []
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                if metadata.get('category') == category:
                    filtered_results.append({
                        'content': doc,
                        'metadata': metadata
                    })
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error getting knowledge by category: {e}")
            return []
    
    def update_knowledge(self, doc_id: str, content: str, metadata: Dict = None):
        """
        Update existing knowledge in the knowledge base
        
        Args:
            doc_id: Document ID to update
            content: New content
            metadata: New metadata
        """
        try:
            # Generate new embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Update the document
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"Updated knowledge document with ID: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error updating knowledge: {e}")
    
    def delete_knowledge(self, doc_id: str):
        """
        Delete knowledge from the knowledge base
        
        Args:
            doc_id: Document ID to delete
        """
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted knowledge document with ID: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error deleting knowledge: {e}")
    
    def get_all_categories(self) -> List[str]:
        """
        Get all available categories in the knowledge base
        
        Returns:
            List of category names
        """
        try:
            # Get all documents
            results = self.collection.get(include=["metadatas"])
            
            categories = set()
            for metadata in results['metadatas']:
                if 'category' in metadata:
                    categories.add(metadata['category'])
            
            return sorted(list(categories))
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get knowledge base statistics
        
        Returns:
            Dictionary with stats
        """
        try:
            count = self.collection.count()
            categories = self.get_all_categories()
            
            return {
                'total_documents': count,
                'categories': categories,
                'category_count': len(categories)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

# Global knowledge base instance
knowledge_base = FinancialKnowledgeBase()
import chromadb
from chromadb.config import Settings
import os

class VectorMemory:
    """
    A simple vector database wrapper using ChromaDB to store and retrieve agent's thoughts and facts.
    We use it to give our agent 'Long-Term Memory'.
    """
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "agent_memory"):
        # Ensure the directory exists
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize chroma client specifically for local persistent storage
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create our memory collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def save(self, text: str, metadata: dict = None):
        """Saves a string fact into memory."""
        # Generate a simple unique ID based on the content hash
        doc_id = str(hash(text))
        
        self.collection.upsert(
            documents=[text],
            metadatas=[metadata or {"source": "agent_insight"}],
            ids=[doc_id]
        )
        return f"Saved to memory: '{text[:50]}...'"
        
    def search(self, query: str, n_results: int = 3) -> str:
        """Searches the memory for facts related to the query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        documents = results.get("documents", [[]])[0]
        if not documents:
            return "No relevant memories found."
            
        formatted = "Recalled from memory:\n"
        for i, doc in enumerate(documents, 1):
            formatted += f"{i}. {doc}\n"
        return formatted

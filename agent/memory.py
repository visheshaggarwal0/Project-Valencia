import os
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions

class Memory:
    def __init__(self, storage_dir: str = "data/chroma_db"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        # Initialize an embedded persistent Chroma DB
        self.client = chromadb.PersistentClient(path=self.storage_dir)
        
        # Use default MiniLM for fast local embeddings
        embed_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="viora_conversations",
            embedding_function=embed_fn
        )

    def log_interaction(self, user_input: str, agent_response: str):
        # Prevent logging overly short generic greetings to save space
        if user_input.lower().strip() in ["hi", "hello", "hey"]:
            return

        timestamp = datetime.now().isoformat()
        doc_id = f"log_{timestamp}"
        text = f"User Request: {user_input}\nViora Response: {agent_response}"
        
        self.collection.add(
            documents=[text],
            metadatas=[{"timestamp": timestamp, "type": "interaction"}],
            ids=[doc_id]
        )

    def get_relevant_context(self, query: str, n_results: int = 4) -> str:
        """Fetch the most semantically relevant conversation history chunks."""
        try:
            count = self.collection.count()
            if count == 0:
                return ""
            
            # Bound n_results to actual count
            fetch_count = min(n_results, count)
            
            results = self.collection.query(
                query_texts=[query],
                n_results=fetch_count
            )
            
            if results and 'documents' in results and results['documents']:
                docs = results['documents'][0]
                if docs:
                    return "Here is relevant past context from our conversations:\n" + "\n---\n".join(docs) + "\n"
            return ""
        except Exception:
            return ""

    def add_note(self, content: str):
        # Stub for older code
        pass

    def get_notes(self):
        return []

import os
import json
from datetime import datetime, timedelta
import chromadb
from chromadb.utils import embedding_functions
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

class Memory:
    def __init__(self, storage_dir: str = "data/chroma_db"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        # Initialize an embedded persistent Chroma DB
        self.client = chromadb.PersistentClient(path=self.storage_dir)
        
        # Use default MiniLM for fast local embeddings
        embed_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # New Fact Extraction Collection
        self.facts_collection = self.client.get_or_create_collection(
            name="viora_facts",
            embedding_function=embed_fn
        )
        
        # New Semantic Routine Cache
        self.routines_collection = self.client.get_or_create_collection(
            name="viora_routines",
            embedding_function=embed_fn
        )
        
        self.extractor_llm = ChatOllama(model="gemma3:1b", temperature=0)

    # --- FACT EXTRACTION MEMORY ---

    def log_interaction(self, user_input: str, agent_response: str):
        if user_input.lower().strip() in ["hi", "hello", "hey"]:
            return

        prompt = f"""You are a precise background memory extractor.
Analyze this interaction:
User: {user_input}
Agent: {agent_response}

Extract ONLY permanent user facts, names, or strict preferences. 
Do NOT extract transient actions like "open notepad", "what is the time", or "close chrome".
Output just the facts as a clean string statement. If there are NO permanent facts to remember about the user, output exactly the word NONE.
"""
        try:
            extraction = self.extractor_llm.invoke([SystemMessage(content=prompt)]).content.strip()
            
            # If Ollama found a fact
            if extraction.upper() != "NONE" and "NONE" not in extraction.upper() and len(extraction) > 5:
                timestamp = datetime.now().isoformat()
                doc_id = f"fact_{timestamp}"
                
                self.facts_collection.add(
                    documents=[extraction],
                    metadatas=[{"timestamp": timestamp, "type": "fact"}],
                    ids=[doc_id]
                )
        except Exception:
            pass # Silent fail to prevent UI disruption

    def get_relevant_context(self, query: str, n_results: int = 4) -> str:
        """Fetch strictly curated facts."""
        try:
            count = self.facts_collection.count()
            if count == 0: return ""
            
            fetch_count = min(n_results, count)
            results = self.facts_collection.query(
                query_texts=[query],
                n_results=fetch_count
            )
            
            if results and 'documents' in results and results['documents']:
                docs = results['documents'][0]
                if docs:
                    return "Database Facts regarding the User:\n" + "\n".join(docs) + "\n"
            return ""
        except Exception:
            return ""

    # --- SEMANTIC ROUTINE CACHE ---

    def save_routine_cache(self, user_input: str, tool_calls: list):
        """Saves a successfully run LangGraph tool payload as a cache vector."""
        if not tool_calls: return
        
        timestamp = datetime.now().isoformat()
        doc_id = f"routine_{hash(user_input)}_{datetime.now().timestamp()}"
        
        # Save the physical dict array as a string so it can be re-loaded as JSON
        payload = json.dumps(tool_calls)
        
        self.routines_collection.add(
            documents=[user_input],
            metadatas=[{"timestamp": timestamp, "payload": payload}],
            ids=[doc_id]
        )

    def check_routine_cache(self, user_input: str) -> list:
        """Checks for identical routines run in the last 14 days >0.95 similarity."""
        try:
            count = self.routines_collection.count()
            if count == 0: return None
            
            # Note: Default embedding function is L2 distance, not cosine similarity
            # L2 distance is smaller = more similar. Typically < 0.15 is extremely identical.
            results = self.routines_collection.query(
                query_texts=[user_input],
                n_results=1,
                include=["metadatas", "distances"]
            )
            
            if results and results["distances"] and results["distances"][0]:
                distance = results["distances"][0][0]
                if distance < 0.15: # Highly strict exact match
                    metadata = results["metadatas"][0][0]
                    cache_time = datetime.fromisoformat(metadata["timestamp"])
                    
                    # 14 Day Sliding TTL Window check
                    if datetime.now() - cache_time < timedelta(days=14):
                        payload_str = metadata.get("payload")
                        if payload_str:
                            return json.loads(payload_str)
            return None
        except Exception:
            return None

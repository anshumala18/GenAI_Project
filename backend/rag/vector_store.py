import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

class VectorStoreService:
    def __init__(self, index_path="vector_index"):
        # Ensure path is absolute for reliability
        self.index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", index_path))
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None

    def create_index(self, chunks: list):
        """
        Creates a FAISS index from document chunks and saves it locally.
        """
        if not chunks:
            print("❌ Warning: No chunks provided to create_index. Index will not be built.")
            return None
        
        print(f"🚀 Creating FAISS index for {len(chunks)} chunks...")
        print(f"🔍 Using model: sentence-transformers/all-MiniLM-L6-v2")
        
        try:
            self.vector_store = FAISS.from_texts(chunks, self.embeddings)
            
            # Ensure the parent directory exists
            parent_dir = os.path.dirname(self.index_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                
            self.vector_store.save_local(self.index_path)
            print(f"✅ Success: FAISS index saved at: {self.index_path}")
            return self.vector_store
        except Exception as e:
            print(f"❌ Error during index creation: {e}")
            return None

    def load_index(self):
        """
        Loads the FAISS index from the local disk.
        """
        if os.path.exists(self.index_path):
            print(f"📂 Loading existing FAISS index from {self.index_path}...")
            try:
                # allow_dangerous_deserialization is required for loading local FAISS pickels
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("✅ Index loaded successfully.")
                return self.vector_store
            except Exception as e:
                print(f"❌ Error loading index: {e}")
                return None
        else:
            print(f"ℹ️ No index found at {self.index_path}. It might need to be created during analysis.")
            return None

    def similarity_search(self, query: str, k: int = 4):
        """
        Performs a similarity search on the FAISS index.
        Returns the top k relevant chunks.
        """
        if not self.vector_store:
            self.load_index()
            
        if not self.vector_store:
            print("Error: Vector store is not initialized or loaded.")
            return []
            
        print(f"Performing similarity search for: '{query}'")
        docs = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

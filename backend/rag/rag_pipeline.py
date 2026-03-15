import logging
from rag.vector_store import VectorStoreService
from engine import IntelligenceEngine

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, vector_store=None):
        self.vector_store = vector_store or VectorStoreService()
        self.engine = IntelligenceEngine()

    def answer_question(self, question: str):
        """
        Orchestrates the RAG flow:
        1. Retrieve context from FAISS.
        2. Construct prompt.
        3. Get response from LLM.
        """
        if not question:
            return "Please provide a valid question."

        # 1. Retrieve relevant chunks
        context_chunks = self.vector_store.similarity_search(question, k=5)
        
        if not context_chunks:
            return "I couldn't find any relevant information in the document to answer your question."

        context_text = "\n\n".join(context_chunks)
        
        # 2. Construct the RAG prompt
        prompt = f"""You are DocAI, an intelligent assistant. Use the provided document context to answer the user's question accurately.
If the answer is not in the context, say that you don't know based on the provided document.

DOCUMENT CONTEXT:
{context_text}

USER QUESTION:
{question}

ANSWER:"""

        # 3. Call LLM via IntelligenceEngine's client
        try:
            if not self.engine.client:
                return "Intelligence Engine is not properly initialized."

            logger.info(f"Generating RAG answer for question: {question}")
            
            response = self.engine.client.chat.completions.create(
                model=self.engine.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on document context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1000,
            )
            
            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return f"An error occurred while processing your question: {str(e)}"

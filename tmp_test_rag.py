import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from rag.chunking import ChunkingService
from rag.vector_store import VectorStoreService
from rag.rag_pipeline import RAGPipeline

class TestRAGBackend(unittest.TestCase):
    def test_chunking(self):
        service = ChunkingService()
        test_text = "This is a long document about AI. " * 100
        chunks = service.create_chunks(test_text)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        print(f"✓ Chunking generated {len(chunks)} chunks")

    @patch('rag.vector_store.OpenAIEmbeddings')
    @patch('rag.vector_store.FAISS')
    def test_vector_store(self, mock_faiss, mock_embeddings):
        service = VectorStoreService(index_path="tmp_index")
        mock_index = MagicMock()
        mock_faiss.from_texts.return_value = mock_index
        
        chunks = ["AI is great", "DocAI is better"]
        service.create_index(chunks)
        
        mock_faiss.from_texts.assert_called_once()
        mock_index.save_local.assert_called_once()
        print("✓ Vector store index creation mocked and verified")

    @patch('rag.rag_pipeline.VectorStoreService')
    @patch('rag.rag_pipeline.IntelligenceEngine')
    def test_rag_pipeline(self, mock_engine, mock_vs):
        pipeline = RAGPipeline()
        mock_vs_instance = mock_vs.return_value
        mock_vs_instance.similarity_search.return_value = ["Context chunk 1"]
        
        mock_engine_instance = mock_engine.return_value
        mock_engine_instance.client.chat.completions.create.return_value.choices[0].message.content = "Sample Answer"
        mock_engine_instance.model_name = "test-model"

        answer = pipeline.answer_question("What is AI?")
        self.assertEqual(answer, "Sample Answer")
        print("✓ RAG Pipeline orchestration verified")

if __name__ == '__main__':
    unittest.main()

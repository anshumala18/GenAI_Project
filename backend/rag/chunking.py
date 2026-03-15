from processor import DocumentProcessor

class ChunkingService:
    def __init__(self):
        self.processor = DocumentProcessor()

    def create_chunks(self, raw_text: str):
        """
        Input: raw_text (str)
        Output: list of chunks (list[str])
        """
        if not raw_text:
            return []
        
        # Clean the text using existing logic
        cleaned_text = self.processor.clean_text(raw_text)
        
        # Split into chunks using existing logic
        chunks = self.processor.get_chunks(cleaned_text)
        
        return chunks

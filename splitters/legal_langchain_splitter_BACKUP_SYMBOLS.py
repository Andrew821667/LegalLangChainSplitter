import re
from typing import Dict, List
import tiktoken
from datetime import datetime
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from app_chunks.splitters.base import BaseSplitter


class LegalLangChainSplitter(BaseSplitter):
    config_schema = {
        "encoding_name": {
            "type": str,
            "label": "Модель токенизации",
            "help_text": "cl100k_base для GPT-4/3.5, p50k_base для старых моделей"
        },
        "min_chunk_size": {
            "type": int,
            "label": "Минимальный размер чанка (символы)",
            "help_text": "Базовый минимум, адаптируется к типу документа"
        },
        "max_chunk_size": {
            "type": int,
            "label": "Максимальный размер чанка (символы)",
            "help_text": "Базовый максимум, адаптируется к типу документа"
        },
        "chunk_overlap": {
            "type": int,
            "label": "Перекрытие чанков (символы)",
            "help_text": "Размер перекрытия для связности контекста"
        }
    }
    
    name = "LangChain Legal"
    help_text = "Адаптивный LangChain чанкер для правовых документов"
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.min_chars = config.get("min_chunk_size", 500)
        self.max_chars = config.get("max_chunk_size", 1200)
        self.chunk_overlap = config.get("chunk_overlap", 100)
        
        encoding_name = config.get("encoding_name", "cl100k_base")
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_name)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"), 
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
        
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_chars,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n\n", "\n\n", "\n", ".", " ", ""],
            add_start_index=False,
        )
    
    def split(self, metadata: dict, text_to_split: str) -> List[Document]:
        strategy = self._analyze_document_structure(text_to_split)
        
        if strategy == "markdown":
            chunks = self._chunk_with_markdown_splitter(text_to_split, metadata)
        else:
            chunks = self._chunk_with_recursive_splitter(text_to_split, metadata)
        
        if not chunks or len(chunks) < 2:
            chunks = self._adaptive_chunking(text_to_split, metadata)
        
        return chunks
    
    def _analyze_document_structure(self, text: str) -> str:
        headers = len(re.findall(r'^#{1,4}\s+', text, re.MULTILINE))
        lists = len(re.findall(r'^\d+\.\s+|^[-*]\s+', text, re.MULTILINE))
        
        if headers >= 3 or (headers >= 1 and lists >= 2):
            return "markdown"
        else:
            return "recursive"
    
    def _chunk_with_markdown_splitter(self, text: str, base_metadata: dict) -> List[Document]:
        try:
            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=self.headers_to_split_on,
                strip_headers=False
            )
            
            header_splits = markdown_splitter.split_text(text)
            final_chunks = []
            
            for doc in header_splits:
                content = doc.page_content
                if len(content) <= self.max_chars:
                    final_chunks.append(content)
                else:
                    sub_chunks = self.recursive_splitter.split_text(content)
                    final_chunks.extend(sub_chunks)
            
            return self._convert_to_documents(final_chunks, base_metadata)
            
        except Exception:
            return self._chunk_with_recursive_splitter(text, base_metadata)
    
    def _chunk_with_recursive_splitter(self, text: str, base_metadata: dict) -> List[Document]:
        try:
            chunks = self.recursive_splitter.split_text(text)
            return self._convert_to_documents(chunks, base_metadata)
        except Exception:
            return self._adaptive_chunking(text, base_metadata)
    
    def _adaptive_chunking(self, text: str, base_metadata: dict) -> List[Document]:
        if len(text) < 2000:
            adaptive_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", ".", " ", ""],
            )
        else:
            adaptive_splitter = self.recursive_splitter
        
        chunks = adaptive_splitter.split_text(text)
        return self._convert_to_documents(chunks, base_metadata)
    
    def _convert_to_documents(self, chunks: list, base_metadata: dict) -> List[Document]:
        documents = []
        
        for i, chunk_text in enumerate(chunks, 1):
            if len(chunk_text.strip()) < 50:
                continue
            
            char_count = len(chunk_text)
            token_count = len(self.tokenizer.encode(chunk_text))
            ratio = char_count / token_count if token_count > 0 else 0
            
            russian_chars = len(re.findall(r'[А-Яа-яё]', chunk_text))
            russian_pct = (russian_chars / char_count) * 100 if char_count > 0 else 0
            artifacts = len(re.findall(r'#{1,6}|\*\*|\(\)|\[\]', chunk_text))
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_number": i,
                "char_count": char_count,
                "token_count": token_count,
                "char_token_ratio": ratio,
                "processing_date": datetime.now().isoformat(),
                "in_target_range": self.min_chars <= char_count <= self.max_chars,
                "ratio_in_target": 1.8 <= ratio <= 4.0,
                "russian_percentage": russian_pct,
                "artifact_count": artifacts,
                "high_quality": russian_pct >= 70 and artifacts <= 2,
                "splitter_type": "langchain_legal",
                "size_in_tokens": str(token_count)
            })
            
            document = Document(
                page_content=chunk_text.strip(),
                metadata=chunk_metadata
            )
            documents.append(document)
        
        return documents

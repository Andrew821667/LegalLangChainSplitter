from typing import List, Dict


class AdaptiveQualityValidator:
    def validate_chunks(self, chunks: list) -> dict:
        if not chunks:
            return {"valid": False, "quality_score": 0, "total_chunks": 0}
        
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        
        if total_chars < 5000:
            min_size, max_size, quality_threshold = 200, 1500, 40
            doc_type = "short"
        elif total_chars < 20000:
            min_size, max_size, quality_threshold = 400, 1200, 60  
            doc_type = "medium"
        else:
            min_size, max_size, quality_threshold = 500, 1200, 70
            doc_type = "long"
        
        size_valid = sum(1 for chunk in chunks 
                        if min_size <= len(chunk.page_content) <= max_size)
        
        ratio_valid = sum(1 for chunk in chunks 
                         if hasattr(chunk, 'metadata') and 
                            1.5 <= chunk.metadata.get('char_token_ratio', 0) <= 4.5)
        
        high_quality = sum(1 for chunk in chunks 
                          if hasattr(chunk, 'metadata') and 
                             chunk.metadata.get('high_quality', False))
        
        size_score = (size_valid / len(chunks)) * 100
        ratio_score = (ratio_valid / len(chunks)) * 100
        hq_score = (high_quality / len(chunks)) * 100
        
        overall_score = (size_score * 0.6 + ratio_score * 0.3 + hq_score * 0.1)
        
        return {
            "valid": overall_score >= quality_threshold,
            "quality_score": overall_score,
            "size_score": size_score,
            "ratio_score": ratio_score,
            "high_quality_score": hq_score,
            "total_chunks": len(chunks),
            "threshold": quality_threshold,
            "document_type": doc_type,
            "adaptive_criteria": f"{min_size}-{max_size} символов",
            "validator_type": "adaptive_legal"
        }

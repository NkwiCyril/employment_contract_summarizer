import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    pipeline
)
import os
import re
from typing import Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelHandler:
    def __init__(self, model_path: str = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"🔧 Using device: {self.device}")
        
        self.summarizer = None
        self.model_path = model_path
        
        # Initialize model
        self._load_model()
    
    def _load_model(self):
        """Load the AI model for summarization"""
        try:
            logger.info("🚀 Loading AI summarization model...")
            
            # Use BART model (doesn't require SentencePiece)
            model_name = "facebook/bart-large"
            
            logger.info(f"📚 Loading BART model: {model_name}")
            
            # Use pipeline for easier setup
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1,
                framework="pt"
            )
            
            logger.info("✅ BART model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading BART model: {e}")
            logger.info("🔄 Trying smaller model...")
            
            try:
                # Try smaller BART model
                model_name = "facebook/bart-base"
                self.summarizer = pipeline(
                    "summarization",
                    model=model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✅ BART-base model loaded successfully!")
                
            except Exception as e2:
                logger.error(f"❌ Error loading BART-base: {e2}")
                logger.info("🔄 Using DistilBART...")
                
                try:
                    # Try DistilBART (smallest)
                    model_name = "sshleifer/distilbart-cnn-12-6"
                    self.summarizer = pipeline(
                        "summarization",
                        model=model_name,
                        device=0 if torch.cuda.is_available() else -1
                    )
                    logger.info("✅ DistilBART model loaded successfully!")
                    
                except Exception as e3:
                    logger.error(f"❌ All models failed: {e3}")
                    self.summarizer = None
    
    def _preprocess_contract(self, text: str) -> str:
        """Preprocess employment contract text"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove excessive formatting
        text = re.sub(r'-{3,}', '', text)
        text = re.sub(r'_{3,}', '', text)
        
        # Limit length for BART (max 1024 tokens)
        words = text.split()
        if len(words) > 800:  # Conservative limit
            text = ' '.join(words[:800])
        
        return text.strip()
    
    def _postprocess_summary(self, summary: str, summary_type: str) -> str:
        """Post-process the generated summary"""
        summary = summary.strip()
        
        # Ensure proper capitalization
        if not summary[0].isupper():
            summary = summary.capitalize()
        
        # Add employment context if missing
        employment_terms = ['employee', 'employer', 'contract', 'position', 'salary']
        if not any(term in summary.lower() for term in employment_terms):
            summary = f"Employment Agreement: {summary}"
        
        return summary
    
    def generate_summary(self, text: str, max_length: int = 250) -> Dict:
        """Generate AI-powered summary using BART"""
        try:
            # Preprocess the text
            processed_text = self._preprocess_contract(text)
            
            # Determine parameters based on max_length
            if max_length <= 150:
                summary_type = 'brief'
                min_length = 30
                max_gen_length = 100
            elif max_length <= 300:
                summary_type = 'standard'
                min_length = 50
                max_gen_length = 200
            else:
                summary_type = 'detailed'
                min_length = 80
                max_gen_length = 350
            
            logger.info(f"📝 Generating {summary_type} summary...")
            
            if self.summarizer:
                # Generate summary using BART
                result = self.summarizer(
                    processed_text,
                    max_length=max_gen_length,
                    min_length=min_length,
                    do_sample=False,  # Use beam search
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
                
                summary = result[0]['summary_text']
                model_used = "bart-transformer"
                confidence = self._calculate_confidence(summary, processed_text)
                
            else:
                # Fallback to extractive summarization
                summary = self._extractive_fallback(processed_text, max_length)
                model_used = "extractive-fallback"
                confidence = 0.6
            
            # Post-process
            final_summary = self._postprocess_summary(summary, summary_type)
            
            logger.info(f"✅ Summary generated! Length: {len(final_summary.split())} words")
            
            return {
                'summary': final_summary,
                'confidence': confidence,
                'model_used': model_used,
                'summary_type': summary_type,
                'word_count': len(final_summary.split())
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating summary: {e}")
            # Emergency fallback
            words = text.split()[:max_length//2]
            return {
                'summary': ' '.join(words) + '...',
                'confidence': 0.3,
                'model_used': 'emergency-fallback',
                'error': str(e)
            }
    
    def _extractive_fallback(self, text: str, max_length: int) -> str:
        """Extractive summarization fallback"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Score sentences by employment keywords
        employment_keywords = [
            'salary', 'compensation', 'position', 'job', 'responsibilities', 
            'benefits', 'insurance', 'termination', 'notice', 'employee', 
            'employer', 'contract', 'employment', 'work', 'duties'
        ]
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = sum(1 for keyword in employment_keywords 
                       if keyword.lower() in sentence.lower())
            # Boost score for sentences with numbers (likely salary/dates)
            if re.search(r'\d+', sentence):
                score += 1
            scored_sentences.append((score, i, sentence))
        
        # Select top sentences
        scored_sentences.sort(reverse=True)
        num_sentences = min(5, max(2, len(sentences) // 4))
        top_sentences = sorted(scored_sentences[:num_sentences], key=lambda x: x[1])
        
        summary = '. '.join([sent[2] for sent in top_sentences])
        
        # Trim to max length
        words = summary.split()
        if len(words) > max_length:
            summary = ' '.join(words[:max_length]) + '...'
        
        return summary
    
    def _calculate_confidence(self, summary: str, original_text: str) -> float:
        """Calculate confidence score"""
        try:
            # Employment keyword presence
            employment_keywords = [
                'salary', 'position', 'responsibilities', 'benefits', 
                'employee', 'employer', 'contract', 'employment'
            ]
            
            summary_lower = summary.lower()
            keyword_count = sum(1 for kw in employment_keywords if kw in summary_lower)
            keyword_ratio = keyword_count / len(employment_keywords)
            
            # Length appropriateness
            summary_words = len(summary.split())
            original_words = len(original_text.split())
            compression_ratio = summary_words / original_words
            
            # Good compression is between 0.1 and 0.3
            if 0.1 <= compression_ratio <= 0.3:
                length_score = 1.0
            else:
                length_score = 0.7
            
            # Combine scores
            confidence = (keyword_ratio * 0.6 + length_score * 0.4)
            
            # Ensure reasonable bounds
            confidence = max(0.5, min(0.95, confidence))
            
            return round(confidence, 2)
            
        except Exception:
            return 0.75
    
    def is_model_loaded(self) -> bool:
        """Check if AI model is loaded"""
        return self.summarizer is not None
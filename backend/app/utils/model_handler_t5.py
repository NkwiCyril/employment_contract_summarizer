import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    pipeline,
    T5Tokenizer,
    T5ForConditionalGeneration
)
import os
import re
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelHandler:
    def __init__(self, model_path: str = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"🔧 Using device: {self.device}")
        
        self.model = None
        self.tokenizer = None
        self.summarizer = None
        self.model_path = model_path
        
        # Initialize model
        self._load_model()
    
    def _load_model(self):
        """Load the AI model for summarization"""
        try:
            logger.info("🚀 Loading AI summarization model...")
            
            # Option 1: Use fine-tuned model if available
            if self.model_path and os.path.exists(self.model_path):
                logger.info(f"📂 Loading custom model from {self.model_path}")
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
            
            # Option 2: Use pre-trained T5 model optimized for summarization
            else:
                logger.info("📚 Loading pre-trained T5 model...")
                model_name = "t5-small"  # Start with small for faster loading
                
                self.tokenizer = T5Tokenizer.from_pretrained(model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(model_name)
                
                # Alternative: Use summarization pipeline (easier but less control)
                # self.summarizer = pipeline(
                #     "summarization",
                #     model="facebook/bart-large-cnn",
                #     device=0 if torch.cuda.is_available() else -1
                # )
            
            if self.model:
                self.model.to(self.device)
                self.model.eval()
                logger.info("✅ Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            logger.info("🔄 Falling back to basic summarization...")
            self._use_fallback = True
    
    def _preprocess_contract(self, text: str) -> str:
        """Preprocess employment contract text for better summarization"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'\n+', '\n', text)  # Normalize line breaks
        
        # Remove excessive formatting
        text = re.sub(r'-{3,}', '', text)  # Remove long dashes
        text = re.sub(r'_{3,}', '', text)  # Remove long underscores
        
        # Ensure key employment sections are emphasized
        employment_patterns = [
            (r'(salary|compensation|remuneration)', r'SALARY'),
            (r'(position|job title|role)', r'POSITION'),
            (r'(responsibilities|duties)', r'RESPONSIBILITIES'),
            (r'(benefits|insurance|allowance)', r'BENEFITS'),
            (r'(termination|notice)', r'TERMINATION'),
            (r'(working hours|schedule)', r'WORKING_CONDITIONS')
        ]
        
        for pattern, replacement in employment_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _postprocess_summary(self, summary: str, summary_type: str) -> str:
        """Post-process the generated summary"""
        # Clean up the summary
        summary = summary.strip()
        
        # Ensure proper capitalization
        sentences = summary.split('. ')
        sentences = [s.capitalize() if s else s for s in sentences]
        summary = '. '.join(sentences)
        
        # Add structure based on summary type
        if summary_type == 'detailed' and len(summary.split()) > 50:
            # For detailed summaries, try to add section headers
            paragraphs = summary.split('\n\n')
            if len(paragraphs) == 1:
                # Split into logical sections
                words = summary.split()
                mid_point = len(words) // 2
                
                first_half = ' '.join(words[:mid_point])
                second_half = ' '.join(words[mid_point:])
                
                summary = f"Employment Overview: {first_half}\n\nKey Terms: {second_half}"
        
        return summary
    
    def generate_summary(self, text: str, max_length: int = 250) -> Dict:
        """Generate AI-powered summary of employment contract"""
        try:
            # Preprocess the text
            processed_text = self._preprocess_contract(text)
            
            # Determine summary type based on max_length
            if max_length <= 150:
                summary_type = 'brief'
                min_length = 50
                max_gen_length = 100
            elif max_length <= 300:
                summary_type = 'standard' 
                min_length = 80
                max_gen_length = 200
            else:
                summary_type = 'detailed'
                min_length = 120
                max_gen_length = 350
            
            logger.info(f"📝 Generating {summary_type} summary...")
            
            # Generate summary using T5 model
            if self.model and self.tokenizer:
                summary = self._generate_with_t5(processed_text, max_gen_length, min_length)
                model_used = "t5-transformer"
                confidence = self._calculate_confidence(summary, processed_text)
                
            # Fallback to pipeline if available
            elif self.summarizer:
                summary = self._generate_with_pipeline(processed_text, max_gen_length, min_length)
                model_used = "bart-transformer"
                confidence = 0.8  # Default confidence for pipeline
                
            else:
                # Last resort: extractive summarization
                summary = self._extractive_fallback(processed_text, max_length)
                model_used = "extractive-fallback"
                confidence = 0.6
            
            # Post-process the summary
            final_summary = self._postprocess_summary(summary, summary_type)
            
            logger.info(f"✅ Summary generated successfully! Length: {len(final_summary.split())} words")
            
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
    
    def _generate_with_t5(self, text: str, max_length: int, min_length: int) -> str:
        """Generate summary using T5 model"""
        # Prepare input for T5 (text-to-text format)
        input_text = f"summarize: {text}"
        
        # Tokenize input
        inputs = self.tokenizer.encode(
            input_text, 
            return_tensors='pt', 
            max_length=512,  # T5 input limit
            truncation=True
        ).to(self.device)
        
        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=min_length,
                length_penalty=2.0,  # Encourage proper length
                num_beams=4,  # Beam search for better quality
                early_stopping=True,
                temperature=0.7,  # Slight randomness for natural text
                do_sample=False,  # Use beam search, not sampling
                repetition_penalty=1.2  # Avoid repetition
            )
        
        # Decode the output
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return summary
    
    def _generate_with_pipeline(self, text: str, max_length: int, min_length: int) -> str:
        """Generate summary using Hugging Face pipeline"""
        result = self.summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            temperature=0.7
        )
        
        return result[0]['summary_text']
    
    def _extractive_fallback(self, text: str, max_length: int) -> str:
        """Simple extractive summarization as last resort"""
        sentences = text.split('. ')
        
        # Score sentences by keyword presence
        employment_keywords = [
            'salary', 'compensation', 'position', 'responsibilities', 
            'benefits', 'termination', 'notice', 'employee', 'employer'
        ]
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = sum(1 for keyword in employment_keywords if keyword.lower() in sentence.lower())
            scored_sentences.append((score, i, sentence))
        
        # Select top sentences
        scored_sentences.sort(reverse=True)
        top_sentences = sorted(scored_sentences[:5], key=lambda x: x[1])  # Maintain order
        
        summary = '. '.join([sent[2] for sent in top_sentences])
        
        # Trim to max length
        words = summary.split()
        if len(words) > max_length:
            summary = ' '.join(words[:max_length]) + '...'
        
        return summary
    
    def _calculate_confidence(self, summary: str, original_text: str) -> float:
        """Calculate confidence score for the generated summary"""
        try:
            # Basic metrics for confidence
            summary_words = set(summary.lower().split())
            original_words = set(original_text.lower().split())
            
            # Word overlap ratio
            overlap = len(summary_words.intersection(original_words))
            overlap_ratio = overlap / len(summary_words) if summary_words else 0
            
            # Length ratio (good summaries have reasonable compression)
            length_ratio = len(summary.split()) / len(original_text.split())
            optimal_ratio = 0.1 if length_ratio < 0.05 else (0.9 if length_ratio > 0.3 else 1.0)
            
            # Employment keyword presence
            employment_keywords = [
                'salary', 'position', 'responsibilities', 'benefits', 
                'employee', 'employer', 'contract', 'employment'
            ]
            keyword_score = sum(1 for kw in employment_keywords if kw in summary.lower())
            keyword_ratio = keyword_score / len(employment_keywords)
            
            # Combine metrics
            confidence = (overlap_ratio * 0.3 + optimal_ratio * 0.3 + keyword_ratio * 0.4)
            
            # Ensure confidence is between 0.5 and 0.95
            confidence = max(0.5, min(0.95, confidence))
            
            return round(confidence, 2)
            
        except Exception:
            return 0.75  # Default confidence if calculation fails
    
    def is_model_loaded(self) -> bool:
        """Check if AI model is properly loaded"""
        return self.model is not None or self.summarizer is not None
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    BartTokenizer,
    BartForConditionalGeneration,
)
import os
import re
from typing import Dict, List
import logging
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelHandler:
    def __init__(self, model_path: str = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"🔧 Using device: {self.device}")
        self.model = None
        self.tokenizer = None
        self.model_name = None
        self.max_input_length = 1024
        self.model_path = model_path
        # Initialize model
        self._load_model()

    def _load_model(self):
        """Load the prioritized Cyrix model with optimizations"""
        # Prioritize the Cyrix model
        primary_model = "cyrix237/237LegalModel"
        fallback_models = [
            ("facebook/bart-large-cnn", "BART-large-CNN"),
            ("sshleifer/distilbart-cnn-12-6", "DistilBART-CNN"),
            ("philschmid/bart-large-cnn-samsum", "SamSum Fine-tuned BART"),
        ]
        
        # Try to load the primary Cyrix model first
        try:
            logger.info(f"🚀 Loading prioritized Cyrix Legal Model...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                primary_model, 
                use_fast=True,
                cache_dir="./model_cache"
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                primary_model,
                cache_dir="./model_cache",
                torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            
            # Enable evaluation mode and optimization
            self.model.eval()
            if hasattr(self.model, 'half') and self.device.type == 'cuda':
                self.model = self.model.half()
                
            logger.info(f"✅ Cyrix Legal Model loaded successfully!")
            self.model_name = primary_model
            return
            
        except Exception as e:
            logger.error(f"❌ Failed to load Cyrix Legal Model: {str(e)}")
            logger.info("🔄 Falling back to alternative models...")
            
        # Fallback to other models if Cyrix fails
        for model_name, display_name in fallback_models:
            try:
                logger.info(f"🚀 Attempting to load {display_name}...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32,
                    low_cpu_mem_usage=True
                ).to(self.device)
                
                self.model.eval()
                if hasattr(self.model, 'half') and self.device.type == 'cuda':
                    self.model = self.model.half()
                    
                logger.info(f"✅ {display_name} loaded successfully!")
                self.model_name = model_name
                return
            except Exception as e:
                logger.error(f"❌ Failed to load {display_name}: {str(e)}")
                continue

        logger.warning("⚠️ No AI model could be loaded; fallback to extractive summarization")

    def _safe_tokenize(self, text: str, max_length: int = None) -> Dict:
        """Safely tokenize input text with optimizations"""
        if max_length is None:
            max_length = self.max_input_length
        try:
            inputs = self.tokenizer(
                text,
                max_length=max_length,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            ).to(self.device)
            return inputs
        except Exception as e:
            logger.error(f"Tokenization error: {e}")
            raise

    def _safe_generate(self, inputs: Dict, max_length: int = 512, min_length: int = 100) -> str:
        """Generate summary from model output with optimized parameters"""
        try:
            with torch.no_grad():  # Disable gradient computation for inference
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs.get("attention_mask", None),
                    max_length=min(max_length, 512),
                    min_length=min(min_length, 50),  # Reduced min_length for faster generation
                    num_beams=3,  # Reduced from 5 for speed
                    length_penalty=1.1,  # Slightly reduced
                    repetition_penalty=1.3,  # Slightly reduced
                    early_stopping=True,
                    no_repeat_ngram_size=2,  # Reduced from 3
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    do_sample=False,  # Greedy decoding for consistency
                )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True).strip()
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return ""

    def _smart_chunk_by_sentences(self, text: str, max_chunk_size: int = 800) -> List[str]:
        """Optimized chunking by sentences instead of complex section parsing"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed max size, start new chunk
            if current_size + sentence_words > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_size = sentence_words
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_size += sentence_words
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def _chunk_text_optimized(self, text: str) -> List[str]:
        """Optimized text chunking for better performance"""
        # Quick section detection - if we find clear section markers, use them
        section_markers = [
            r'\b(?:ARTICLE|SECTION|CLAUSE)\s+\d+',
            r'\b\d+\.\s*[A-Z][a-z]+',
            r'\b(?:Parties|Position|Compensation|Benefits|Responsibilities|Termination|Confidentiality|Non-compete|Governing Law)\b'
        ]
        
        # Check if document has clear section structure
        section_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in section_markers)
        
        if section_count >= 3:  # Document seems well-structured
            logger.info("📋 Detected structured document, using section-based chunking")
            return self._quick_section_split(text)
        else:
            logger.info("📋 Using optimized sentence-based chunking")
            return self._smart_chunk_by_sentences(text)

    def _quick_section_split(self, text: str) -> List[str]:
        """Quick section splitting without complex regex"""
        # Simple split on common section indicators
        patterns = [
            r'\n\s*(?:ARTICLE|SECTION|CLAUSE)\s+\d+',
            r'\n\s*\d+\.\s*[A-Z]',
            r'\n\s*(?:Parties|Position|Compensation|Benefits|Responsibilities|Termination|Confidentiality|Non-compete|Governing Law)'
        ]
        
        for pattern in patterns:
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 2:  # Found meaningful splits
                # Clean and filter non-empty parts
                sections = [part.strip() for part in parts if part.strip() and len(part.strip()) > 50]
                return sections[:10]  # Limit to 10 sections max for performance
        
        # Fallback to sentence chunking
        return self._smart_chunk_by_sentences(text)

    def _summarize_chunk(self, chunk: str, target_length: int = 150) -> str:
        """Summarize a single chunk with optimized parameters"""
        if not self.model or not self.tokenizer:
            return self._extractive_summary(chunk, target_length)
        
        try:
            # Skip very short chunks
            if len(chunk.split()) < 30:
                return self._extractive_summary(chunk, min(target_length, 50))
            
            inputs = self._safe_tokenize(chunk, max_length=1024)
            summary = self._safe_generate(inputs, max_length=target_length, min_length=max(30, target_length//3))
            
            if not summary or len(summary.split()) < 10:
                summary = self._extractive_summary(chunk, target_length)
                
            return summary
        except Exception as e:
            logger.error(f"Chunk summarization failed: {e}")
            return self._extractive_summary(chunk, target_length)
        
    def _format_summary_to_markdown(self, summary: str) -> str:
        """Optimized markdown formatting"""
        # Define section headers and matching keywords
        sections = {
            "🏢 Parties": ["parties", "employer", "employee", "company", "organization"],
            "💼 Position": ["position", "role", "title", "job", "duties"],
            "💰 Compensation": ["salary", "compensation", "pay", "wage", "$", "amount"],
            "🎁 Benefits": ["benefits", "insurance", "vacation", "leave", "pto", "health"],
            "📋 Responsibilities": ["responsibilities", "duties", "obligations", "tasks"],
            "🚪 Termination": ["termination", "end", "notice", "resignation", "dismissal"],
            "🔒 Confidentiality": ["confidentiality", "nda", "confidential", "secrets"],
            "🚫 Non-Compete": ["non-compete", "competition", "restrictions", "covenant"],
            "⚖️ Governing Law": ["governing law", "jurisdiction", "legal", "court"]
        }

        # Split summary into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', summary) if s.strip()]
        
        # Group sentences by section
        grouped_content = {section: [] for section in sections}
        unmatched = []

        for sentence in sentences:
            matched = False
            sentence_lower = sentence.lower()
            
            for section_name, keywords in sections.items():
                if any(keyword in sentence_lower for keyword in keywords):
                    grouped_content[section_name].append(f"• {sentence}")
                    matched = True
                    break
            
            if not matched:
                unmatched.append(f"• {sentence}")

        # Build markdown output
        markdown_output = ""
        
        for section_name, content in grouped_content.items():
            if content:
                markdown_output += f"## {section_name}\n"
                markdown_output += "\n".join(content) + "\n\n"
        
        # Add unmatched content as general section
        if unmatched:
            markdown_output += "## 📄 General Information\n"
            markdown_output += "\n".join(unmatched) + "\n\n"

        return markdown_output.strip()

    def generate_summary(self, text: str, summary_type: str = 'standard') -> Dict:
        """Optimized main summarization function"""
        try:
            logger.info("📝 Starting optimized summarization process...")
            processed_text = self._preprocess_contract(text)

            # Determine summary parameters
            if summary_type == 'brief':
                target_words = 250
                max_chunks = 5
            elif summary_type == 'detailed':
                target_words = 700
                max_chunks = 10
            else:
                target_words = 400
                max_chunks = 8

            logger.info(f"📄 Target: ~{target_words} words, max {max_chunks} chunks")

            if not self.model or not self.tokenizer:
                logger.warning("No model available, using extractive method")
                return self._extractive_fallback(processed_text, target_words)

            # Optimized chunking
            chunks = self._chunk_text_optimized(processed_text)
            
            # Limit chunks for performance
            if len(chunks) > max_chunks:
                logger.info(f"🔄 Limiting to {max_chunks} most important chunks")
                chunks = self._select_important_chunks(chunks, max_chunks)
            
            # logger.info(f"📄 Processing {len(chunks)} chunks")

            # Process chunks with progress tracking
            summarized_sections = []
            chunk_target = target_words // len(chunks) if chunks else target_words
            
            for i, chunk in enumerate(chunks):
                logger.info(f"🧠 Processing chunk {i+1}/{len(chunks)}")
                summary = self._summarize_chunk(chunk, chunk_target)
                if summary:
                    summarized_sections.append(summary)

            # Combine summaries
            full_summary = " ".join(summarized_sections)

            # Final condensation if needed
            if len(full_summary.split()) > target_words * 1.2:
                logger.info("🔁 Final condensation pass")
                inputs = self._safe_tokenize(full_summary, max_length=1024)
                full_summary = self._safe_generate(inputs, max_length=target_words, min_length=int(target_words * 0.6))

            # Post-process and format
            full_summary = self._postprocess_summary(full_summary)
            formatted_summary = self._format_summary_to_markdown(full_summary)
            confidence = self._calculate_confidence(full_summary, processed_text)

            return {
                'summary': formatted_summary,
                'raw_summary': full_summary,
                "confidence": confidence,
                "model_used": self.model_name or "extractive",
                "summary_type": summary_type,
                "word_count": len(full_summary.split()),
                "chunks_processed": len(chunks),
                "target_words": target_words
            }

        except Exception as e:
            logger.error(f"❌ Critical error during summarization: {e}")
            return self._extractive_fallback(text, target_words)

    def _select_important_chunks(self, chunks: List[str], max_chunks: int) -> List[str]:
        """Select most important chunks based on keyword density"""
        important_keywords = [
            'salary', 'compensation', 'position', 'benefits', 'termination',
            'responsibilities', 'employee', 'employer', 'contract', 'agreement'
        ]
        
        scored_chunks = []
        for chunk in chunks:
            score = sum(chunk.lower().count(keyword) for keyword in important_keywords)
            score += len(re.findall(r'\$\d+|\d+%', chunk)) * 2  # Financial info bonus
            scored_chunks.append((score, chunk))
        
        # Sort by score and take top chunks
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in scored_chunks[:max_chunks]]

    def _preprocess_contract(self, text: str) -> str:
        """Optimized text preprocessing"""
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[-_=]{3,}', '', text)  # Remove separator lines
        text = re.sub(r'\.{2,}', '.', text)   # Fix multiple periods
        text = re.sub(r',{2,}', ',', text)    # Fix multiple commas
        return text.strip()

    def _postprocess_summary(self, summary: str) -> str:
        """Optimized post-processing"""
        summary = re.sub(r'\s+', ' ', summary).strip()
        if summary and not summary.endswith('.'):
            summary += '.'
        return summary

    def _extractive_summary(self, text: str, max_words: int) -> str:
        """Optimized extractive summarization"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if not sentences:
            return text[:max_words*5]  # Rough word estimate
        
        # Score sentences
        keywords = ['salary', 'compensation', 'position', 'benefits', 'termination',
                   'responsibilities', 'employee', 'employer', '$', '%']
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) < 5:  # Skip very short sentences
                continue
                
            score = sum(1 for keyword in keywords if keyword.lower() in sentence.lower())
            score += 2 if re.search(r'\$\d+|\d+%', sentence) else 0  # Financial info
            score += 1 / (i + 1)  # Position bonus (earlier = better)
            
            if score > 0:
                scored_sentences.append((score, sentence))

        # Select top sentences
        scored_sentences.sort(reverse=True)
        num_sentences = min(5, len(scored_sentences))
        selected = [s[1] for s in scored_sentences[:num_sentences]]
        
        summary = ". ".join(selected)
        words = summary.split()
        if len(words) > max_words:
            summary = " ".join(words[:max_words]) + "..."
            
        return summary + "." if not summary.endswith('.') else summary

    def _extractive_fallback(self, text: str, max_words: int) -> Dict:
        """Optimized extractive fallback"""
        logger.info("🔄 Using optimized extractive summarization")
        summary = self._extractive_summary(text, max_words)
        formatted_summary = self._format_summary_to_markdown(summary)
        
        return {
            "summary": formatted_summary,
            "raw_summary": summary,
            "confidence": 0.7,
            "model_used": "extractive",
            "summary_type": "fallback",
            "word_count": len(summary.split()),
            "target_words": max_words,
            "chunks_processed": 1
        }

    def _calculate_confidence(self, summary: str, original_text: str) -> float:
        """Optimized confidence calculation"""
        key_terms = ['salary', 'position', 'compensation', 'benefits', 'termination']
        
        original_lower = original_text.lower()
        summary_lower = summary.lower()
        
        present_in_original = sum(1 for term in key_terms if term in original_lower)
        covered_in_summary = sum(1 for term in key_terms if term in summary_lower)
        
        coverage_score = covered_in_summary / present_in_original if present_in_original > 0 else 0.5
        
        # Length ratio (not too short, not too long)
        word_ratio = len(summary.split()) / len(original_text.split())
        length_score = min(word_ratio * 3, 1.0)  # Optimal around 0.33 ratio
        
        confidence = 0.6 * coverage_score + 0.4 * length_score
        return round(min(confidence, 0.95), 2)  # Cap at 95%

    def is_model_loaded(self) -> bool:
        """Check if model is ready for inference"""
        return self.model is not None and self.tokenizer is not None
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "is_loaded": self.is_model_loaded(),
            "max_input_length": self.max_input_length
        }
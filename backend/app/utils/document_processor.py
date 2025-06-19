import fitz  # PyMuPDF
import docx
from langdetect import detect
import spacy
import re
from typing import Dict, List, Optional


class DocumentProcessor:
    def __init__(self):
        # Load spaCy models for English and French
        try:
            self.nlp_en = spacy.load('en_core_web_sm')
        except IOError:
            self.nlp_en = None

        try:
            self.nlp_fr = spacy.load('fr_core_news_sm')
        except IOError:
            self.nlp_fr = None

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    def detect_language(self, text: str) -> str:
        """Detect document language using langdetect"""
        try:
            lang = detect(text)
            return 'fr' if lang == 'fr' else 'en'
        except:
            return 'en'  # Default to English

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+/\d+', '', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def extract_employment_entities(self, text: str, language: str) -> List[Dict]:
        """Extract employment-specific entities"""
        entities = []

        nlp = self.nlp_en if language == 'en' else self.nlp_fr
        if not nlp:
            return entities

        doc = nlp(text)

        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'MONEY', 'DATE']:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'confidence': 0.9
                })

        # Custom salary patterns
        salary_patterns = [
            r'salary[:\s]+([\d\s.,]+)\s*(fcfa|euros?|dollars?)',
            r'([\d\s.,]+)\s*(fcfa|euros?|dollars?)\s*(?:per|\/)\s*month'
        ]

        for pattern in salary_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'label': 'SALARY',
                    'confidence': 0.8
                })

        return entities

    def identify_contract_sections(self, text: str) -> Dict[str, str]:
        """Identify main sections of employment contract"""
        sections = {}

        section_patterns = {
            'job_description': r'(job description|duties|responsibilities)',
            'compensation': r'(salary|compensation|remuneration|benefits)',
            'working_conditions': r'(working hours|work schedule|location)',
            'termination': r'(termination|notice|resignation)',
            'confidentiality': r'(confidential|non-disclosure|proprietary)'
        }

        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 500)
                sections[section_name] = text[start:end]

        return sections

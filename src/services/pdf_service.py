import pdfplumber
import os
import logging
from typing import Dict, List, Union, Optional

# setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return ""
        
        full_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n\n"
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
        return full_text.strip()
    
    @staticmethod
    def extract_text_by_pages(pdf_path: str) -> Dict[int, str]:
        pages = {}
        
        if not os.path.isfile(pdf_path):
            logger.error(f"Cannot find PDF file at: {pdf_path}")
            return pages
            
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages[i] = text.strip()
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            
        return pages
    
    @staticmethod
    def extract_content(
        pdf_path: str, 
        extract_text: bool = True, 
        extract_images: bool = False,
        extract_tables: bool = False
    ) -> Dict[int, Dict[str, Union[str, List]]]:
        result = {}
        
        if not os.path.isfile(pdf_path):
            logger.error(f"PDF not found at path: {pdf_path}")
            return result
            
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    page_content = {}
                    
                    if extract_text:
                        text = page.extract_text()
                        if text:
                            page_content["text"] = text
                    
                    if extract_images and page.images:
                        page_content["images"] = [img for img in page.images]
                    
                    if extract_tables:
                        tables = page.extract_tables()
                        if tables:
                            page_content["tables"] = tables
                    
                    if page_content:
                        result[i] = page_content
                        
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            
        return result
    
    @staticmethod
    def extract_metadata(pdf_path: str) -> Dict:
        """Extract metadata from the PDF."""
        if not os.path.exists(pdf_path):
            logger.error(f"Can't find PDF at: {pdf_path}")
            return {}
            
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return pdf.metadata or {}
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    @staticmethod
    def get_pdf_info(pdf_path: str) -> Dict:
        """Get basic information about the PDF."""
        if not os.path.isfile(pdf_path):
            logger.error(f"PDF file missing: {pdf_path}")
            return {}
            
        try:
            with pdfplumber.open(pdf_path) as pdf:
                info = {
                    "pages": len(pdf.pages),
                    "metadata": pdf.metadata or {},
                    "size_bytes": os.path.getsize(pdf_path),
                }
                return info
        except Exception as e:
            logger.error(f"Failed to get PDF info: {e}")
            return {}
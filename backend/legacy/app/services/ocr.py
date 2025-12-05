"""
OCR service for document text extraction and processing
"""
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract OCR not available. Install pytesseract and Pillow for OCR support.")

try:
    import pdf2image

    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logger.warning("pdf2image not available. PDF OCR will be limited.")


class OCRService:
    """Service for Optical Character Recognition"""

    @staticmethod
    def is_available() -> bool:
        """Check if OCR is available"""
        return TESSERACT_AVAILABLE

    @staticmethod
    def extract_text_from_image(image_path: str, language: str = "eng") -> str:
        """
        Extract text from an image file using Tesseract OCR

        Args:
            image_path: Path to the image file
            language: Language code for OCR (default: 'eng')

        Returns:
            Extracted text string
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract OCR is not available. Install pytesseract and Pillow.")

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=language)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image {image_path}: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_pdf(pdf_path: str, language: str = "eng") -> str:
        """
        Extract text from a PDF file using Tesseract OCR

        Args:
            pdf_path: Path to the PDF file
            language: Language code for OCR (default: 'eng')

        Returns:
            Extracted text string
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract OCR is not available.")

        if not PDF2IMAGE_AVAILABLE:
            logger.warning("pdf2image not available. PDF OCR may not work properly.")
            return ""

        try:
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(pdf_path)

            # Extract text from each page
            all_text = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image, lang=language)
                if text.strip():
                    all_text.append(f"--- Page {i + 1} ---\n{text}")

            return "\n\n".join(all_text).strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_file(file_path: str, mime_type: str, language: str = "eng") -> str:
        """
        Extract text from a file based on its MIME type

        Args:
            file_path: Path to the file
            mime_type: MIME type of the file
            language: Language code for OCR (default: 'eng')

        Returns:
            Extracted text string
        """
        if not OCRService.is_available():
            return ""

        file_ext = Path(file_path).suffix.lower()

        # Handle text files directly
        if mime_type == "text/plain" or file_ext == ".txt":
            try:
                with open(file_path, encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {str(e)}")
                return ""

        # Handle images
        if mime_type.startswith("image/"):
            return OCRService.extract_text_from_image(file_path, language)

        # Handle PDFs
        if mime_type == "application/pdf" or file_ext == ".pdf":
            return OCRService.extract_text_from_pdf(file_path, language)

        # For other file types, try OCR if it's an image-like format
        if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
            return OCRService.extract_text_from_image(file_path, language)

        logger.warning(f"OCR not supported for file type: {mime_type}")
        return ""

    @staticmethod
    def extract_metadata_from_text(text: str) -> dict[str, Any]:
        """
        Extract structured metadata from OCR text

        Args:
            text: Extracted text from OCR

        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            "text_length": len(text),
            "word_count": len(text.split()) if text else 0,
            "has_dates": False,
            "has_numbers": False,
            "has_email": False,
            "extracted_dates": [],
            "extracted_numbers": [],
            "extracted_emails": [],
        }

        if not text:
            return metadata

        import re

        # Extract dates (various formats)
        date_patterns = [
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",  # MM/DD/YYYY or DD/MM/YYYY
            r"\d{4}[/-]\d{1,2}[/-]\d{1,2}",  # YYYY/MM/DD
            r"\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b",  # DD Mon YYYY
        ]

        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            if dates:
                metadata["has_dates"] = True
                metadata["extracted_dates"].extend(dates)

        # Extract email addresses
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            metadata["has_email"] = True
            metadata["extracted_emails"] = list(set(emails))

        # Extract phone numbers (various formats)
        phone_patterns = [
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # US/Canada format
            r"\b\+?\d{1,3}[-.]?\d{1,4}[-.]?\d{1,4}[-.]?\d{1,9}\b",  # International
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                metadata["has_numbers"] = True
                metadata["extracted_numbers"].extend(phones)

        # Extract passport numbers (common patterns)
        passport_pattern = r"\b[A-Z]{1,2}\d{6,9}\b"
        passports = re.findall(passport_pattern, text)
        if passports:
            metadata["passport_numbers"] = list(set(passports))

        return metadata

    @staticmethod
    def process_document(file_path: str, mime_type: str, language: str = "eng") -> dict[str, Any]:
        """
        Process a document: extract text and metadata

        Args:
            file_path: Path to the document file
            mime_type: MIME type of the file
            language: Language code for OCR (default: 'eng')

        Returns:
            Dictionary with extracted text and metadata
        """
        result = {"text": "", "metadata": {}, "success": False, "error": None}

        try:
            # Extract text
            text = OCRService.extract_text_from_file(file_path, mime_type, language)
            result["text"] = text

            # Extract metadata
            if text:
                result["metadata"] = OCRService.extract_metadata_from_text(text)

            result["success"] = True
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            result["error"] = str(e)

        return result

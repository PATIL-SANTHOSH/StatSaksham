import os
import re
from typing import List, Dict, Any, Optional

def clean_text(text: str) -> str:
    """
    Clean extracted text while preserving structural markers (headings, bullet points, line breaks).
    """
    if not text:
        return ""
    
    # Replace non-breaking spaces and other Unicode spaces with standard space
    text = text.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    
    # Normalize horizontal whitespace within lines (multiple spaces/tabs -> single space)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove leading/trailing spaces on individual lines
    lines = [line.strip() for line in text.splitlines()]
    
    # Collapse 3+ consecutive newlines into 2
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if not line:
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line)
            
    return "\n".join(cleaned_lines).strip()


class DocumentExtractor:
    """
    Extracts text from PDF, PPTX, DOCX, and TXT files, preserving page/slide metadata.
    """
    
    SUPPORTED_EXTENSIONS = {".pdf", ".pptx", ".ppt", ".docx", ".doc", ".txt", ".md", ".csv"}

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        ext = os.path.splitext(filename)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def extract_document_pages(
        cls, 
        file_path: str, 
        filename: str, 
        mime_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract page/slide structured text blocks from a file.
        Returns: List[{"page": int, "text": str, "source": str, "type": str}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("The uploaded file is completely empty (0 bytes).")

        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return cls._extract_pdf(file_path, filename)
        elif ext in [".pptx", ".ppt"]:
            return cls._extract_pptx(file_path, filename)
        elif ext in [".docx", ".doc"]:
            return cls._extract_docx(file_path, filename)
        elif ext in [".txt", ".md", ".csv"]:
            return cls._extract_txt(file_path, filename)
        else:
            # Fallback text attempt
            return cls._extract_txt(file_path, filename)

    @classmethod
    def _extract_pdf(cls, file_path: str, filename: str) -> List[Dict[str, Any]]:
        pages = []
        
        # 1. Try PyMuPDF (fitz) first - fastest & most accurate layout extraction
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            for page_idx in range(page_count):
                page = doc[page_idx]
                page_text = page.get_text("text") or ""
                cleaned = clean_text(page_text)
                if cleaned:
                    pages.append({
                        "page": page_idx + 1,
                        "text": cleaned,
                        "source": filename,
                        "type": "page"
                    })
            doc.close()
        except Exception as fitz_err:
            print(f"[DocumentExtractor] PyMuPDF extraction warning: {fitz_err}. Falling back to pypdf...")
            pages = []

        # 2. Fallback to pypdf if PyMuPDF failed or wasn't available
        if not pages:
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    cleaned = clean_text(page_text)
                    if cleaned:
                        pages.append({
                            "page": page_idx + 1,
                            "text": cleaned,
                            "source": filename,
                            "type": "page"
                        })
            except Exception as pypdf_err:
                print(f"[DocumentExtractor] pypdf extraction error: {pypdf_err}")

        # Check total selectable text
        total_text_length = sum(len(p["text"]) for p in pages)
        if total_text_length < 25:
            raise ValueError(
                "This PDF appears to be scanned/image-based and contains no selectable text. "
                "Please upload a text-based PDF or export your document with selectable text."
            )

        return pages

    @classmethod
    def _extract_pptx(cls, file_path: str, filename: str) -> List[Dict[str, Any]]:
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            pages = []

            for slide_idx, slide in enumerate(prs.slides):
                slide_texts = []
                
                # Check for slide title
                if slide.shapes.title and slide.shapes.title.text:
                    title_text = slide.shapes.title.text.strip()
                    if title_text:
                        slide_texts.append(f"Title: {title_text}")

                # Iterate all shapes in slide
                for shape in slide.shapes:
                    if shape == slide.shapes.title:
                        continue
                    
                    # Extract from text frame
                    if hasattr(shape, "text_frame") and shape.text_frame:
                        for p in shape.text_frame.paragraphs:
                            p_text = p.text.strip()
                            if p_text:
                                slide_texts.append(p_text)
                    elif hasattr(shape, "text") and shape.text:
                        shape_text = shape.text.strip()
                        if shape_text:
                            slide_texts.append(shape_text)
                            
                    # Extract from tables
                    if hasattr(shape, "has_table") and shape.has_table:
                        table = shape.table
                        for row in table.rows:
                            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if row_cells:
                                slide_texts.append(" | ".join(row_cells))

                full_slide_text = clean_text("\n".join(slide_texts))
                if full_slide_text:
                    pages.append({
                        "page": slide_idx + 1,
                        "text": full_slide_text,
                        "source": filename,
                        "type": "slide"
                    })

            total_len = sum(len(p["text"]) for p in pages)
            if total_len < 10:
                raise ValueError("The presentation contains no readable text content.")

            return pages
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to process PowerPoint presentation ({filename}): {str(e)}")

    @classmethod
    def _extract_docx(cls, file_path: str, filename: str) -> List[Dict[str, Any]]:
        try:
            import docx
            doc = docx.Document(file_path)
            
            blocks = []
            for p in doc.paragraphs:
                p_text = p.text.strip()
                if not p_text:
                    continue
                # Note headings
                if p.style and p.style.name and p.style.name.startswith("Heading"):
                    blocks.append(f"\n## {p_text}\n")
                else:
                    blocks.append(p_text)

            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        blocks.append(" | ".join(row_cells))

            full_text = clean_text("\n\n".join(blocks))
            if len(full_text) < 10:
                raise ValueError("The Word document (.docx) contains no readable text content.")

            # Chunk into approximate pages of 500 words
            words = full_text.split()
            page_size_words = 500
            pages = []
            
            for i in range(0, len(words), page_size_words):
                page_words = words[i:i + page_size_words]
                page_text = " ".join(page_words)
                page_num = (i // page_size_words) + 1
                pages.append({
                    "page": page_num,
                    "text": page_text,
                    "source": filename,
                    "type": "section"
                })

            return pages
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to process Word document ({filename}): {str(e)}")

    @classmethod
    def _extract_txt(cls, file_path: str, filename: str) -> List[Dict[str, Any]]:
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        raw_text = None

        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc, errors="replace") as f:
                    raw_text = f.read()
                if raw_text:
                    break
            except Exception:
                continue

        if not raw_text or not clean_text(raw_text):
            raise ValueError("The text file is empty or unreadable.")

        cleaned = clean_text(raw_text)
        
        # Partition into ~500 word sections
        words = cleaned.split()
        page_size_words = 500
        pages = []
        
        for i in range(0, max(1, len(words)), page_size_words):
            page_words = words[i:i + page_size_words]
            page_text = " ".join(page_words)
            page_num = (i // page_size_words) + 1
            pages.append({
                "page": page_num,
                "text": page_text,
                "source": filename,
                "type": "page"
            })

        return pages


document_extractor = DocumentExtractor()

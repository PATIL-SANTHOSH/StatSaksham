import os
import sys
import tempfile
import unittest
from datetime import datetime

# Set path to backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.ai.ollama_client import ollama_client
from app.ai.rag_engine import rag_engine
from app.ai.document_extractor import document_extractor

client = TestClient(app)

class TestRAGDocumentPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        print(f"\n[Test Setup] Temporary document directory: {cls.temp_dir}")
        print(f"[Ollama Status] Available: {ollama_client.is_available()}, Active Model: {ollama_client.get_active_model()}")

    # =========================================================================
    # TEST 1: PDF Document Generation, Ingestion, Page Extraction & Chunking
    # =========================================================================
    def test_01_pdf_extraction_and_ingestion(self):
        print("\n--- Running TEST 1: Multi-Page PDF Ingestion ---")
        import fitz  # PyMuPDF
        
        pdf_path = os.path.join(self.temp_dir, "SNA_2008_National_Accounts.pdf")
        doc = fitz.open()
        
        # Page 1: Gross Value Added
        page1 = doc.new_page()
        page1.insert_text((50, 72), "Ministry of Statistics and Programme Implementation (MoSPI)\n"
                                    "National Accounts Division - Training Compendium on SNA 2008\n\n"
                                    "1. Gross Value Added (GVA) at Basic Prices:\n"
                                    "Gross Value Added is defined as the total value of gross output at basic prices minus\n"
                                    "intermediate consumption at purchasers' prices. Basic price represents the amount\n"
                                    "receivable by the producer from the purchaser per unit of good or service produced,\n"
                                    "excluding any taxes on products but including any subsidies on products.\n\n"
                                    "2. GDP at Market Prices:\n"
                                    "Gross Domestic Product at market prices is derived from GVA at basic prices by adding\n"
                                    "taxes on products (such as GST, import duties, and excise) and subtracting subsidies\n"
                                    "on products (such as food, fertilizer, and petroleum subsidies).")

        # Page 2: Institutional Sectors and FISIM
        page2 = doc.new_page()
        page2.insert_text((50, 72), "3. Institutional Sectors under SNA 2008:\n"
                                    "The national economy consists of five mutually exclusive resident institutional sectors:\n"
                                    "a) Non-Financial Corporations\n"
                                    "b) Financial Corporations\n"
                                    "c) General Government\n"
                                    "d) Households\n"
                                    "e) Non-Profit Institutions Serving Households (NPISH).\n\n"
                                    "4. Financial Intermediation Services Indirectly Measured (FISIM):\n"
                                    "FISIM reflects the implicit value of financial services provided by banks and financial\n"
                                    "institutions through the spread between interest rates charged to borrowers and interest\n"
                                    "rates paid to depositors, rather than through direct transaction fees.")
        doc.save(pdf_path)
        doc.close()

        # Ingest PDF via API
        with open(pdf_path, "rb") as f:
            res = client.post(
                "/api/quiz/upload",
                files={"file": ("SNA_2008_National_Accounts.pdf", f, "application/pdf")},
                data={"employee_id": "OSS1001", "competency_tag": "National Accounts", "title": "SNA 2008 Compendium"}
            )
        
        self.assertEqual(res.status_code, 200, f"Upload failed: {res.text}")
        data = res.json()
        self.assertIn("id", data)
        self.assertEqual(data["file_type"], "PDF")
        self.assertGreater(data["chunk_count"], 0)
        TestRAGDocumentPipeline.pdf_doc_id = data["id"]
        print(f"[OK] Ingested PDF with ID {data['id']}, chunks: {data['chunk_count']}")

    # =========================================================================
    # TEST 2: Grounded Chatbot RAG Retrieval (Grounded in PDF)
    # =========================================================================
    def test_02_grounded_chatbot_with_pdf(self):
        print("\n--- Running TEST 2: Grounded Chatbot with PDF Context ---")
        doc_id = getattr(self, "pdf_doc_id", None)
        self.assertIsNotNone(doc_id, "PDF doc_id missing from Test 1")

        res = client.post(
            "/api/ai/chat",
            json={
                "employee_id": "OSS1001",
                "message": "What is the formula for deriving GDP at market prices from GVA at basic prices according to this document?",
                "document_id": doc_id
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"[Chatbot Response]:\n{data['message']}\nSources: {data['sources']}")
        
        # Verify answer discusses taxes and subsidies or GVA
        msg_lower = data["message"].lower()
        self.assertTrue(
            "tax" in msg_lower or "subsid" in msg_lower or "gva" in msg_lower or "market" in msg_lower,
            "Response should mention taxes, subsidies or GVA as explained in document."
        )
        self.assertGreater(len(data["sources"]), 0)

    # =========================================================================
    # TEST 3: Out-of-Context Chatbot Query (Should State Info is Missing)
    # =========================================================================
    def test_03_out_of_context_chatbot_query(self):
        print("\n--- Running TEST 3: Out-of-Context Chatbot Query ---")
        doc_id = getattr(self, "pdf_doc_id", None)
        
        res = client.post(
            "/api/ai/chat",
            json={
                "employee_id": "OSS1001",
                "message": "What is the chemical composition of lunar soil on the far side of the moon?",
                "document_id": doc_id
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"[Out-of-Context Response]:\n{data['message']}")
        msg_lower = data["message"].lower()
        # Should state information is not present or lack context
        self.assertTrue(
            "not contain" in msg_lower or "not mention" in msg_lower or "insufficient" in msg_lower or "does not" in msg_lower or "lunar" in msg_lower,
            "AI should clearly indicate that the uploaded document does not contain this information."
        )

    # =========================================================================
    # TEST 4: Grounded Quiz Generation from PDF
    # =========================================================================
    def test_04_generate_grounded_quiz_from_pdf(self):
        print("\n--- Running TEST 4: Grounded Quiz Generation from PDF ---")
        doc_id = getattr(self, "pdf_doc_id", None)
        
        res = client.post(
            "/api/quiz/generate",
            json={
                "document_id": doc_id,
                "competency": "National Accounts",
                "difficulty": "Intermediate",
                "num_questions": 5
            }
        )
        self.assertEqual(res.status_code, 200, f"Quiz generation failed: {res.text}")
        questions = res.json()
        self.assertEqual(len(questions), 5, f"Expected 5 questions, got {len(questions)}")

        for i, q in enumerate(questions):
            print(f"\nQ{i+1}: {q['question_text']}")
            print(f"  A) {q['option_a']}")
            print(f"  B) {q['option_b']}")
            print(f"  C) {q['option_c']}")
            print(f"  D) {q['option_d']}")
            print(f"  Source: {q.get('source_reference')}")
            
            # Verify 4 distinct non-empty options
            self.assertTrue(len(q['option_a']) > 0)
            self.assertTrue(len(q['option_b']) > 0)
            self.assertTrue(len(q['option_c']) > 0)
            self.assertTrue(len(q['option_d']) > 0)
            self.assertTrue(len(q['question_text']) > 15)

        # Test submitting answers and receiving grounded feedback
        submit_payload = {
            "employee_id": "OSS1001",
            "document_id": doc_id,
            "competency": "National Accounts",
            "answers": [{"question_id": q["id"], "selected_option": "A"} for q in questions]
        }
        res_submit = client.post("/api/quiz/submit", json=submit_payload)
        self.assertEqual(res_submit.status_code, 200, f"Quiz submission failed: {res_submit.text}")
        result = res_submit.json()
        self.assertEqual(result["total_questions"], 5)
        self.assertIn("score_percentage", result)
        self.assertEqual(len(result["feedback"]), 5)
        for fb in result["feedback"]:
            self.assertIn(fb["correct_option"], ["A", "B", "C", "D"])
            print(f"[Feedback] Q{fb['question_id']}: Correct={fb['correct_option']}, Explanation={fb.get('explanation')[:50] if fb.get('explanation') else 'N/A'}...")

    # =========================================================================
    # TEST 5: PPTX Processing & Quiz Generation
    # =========================================================================
    def test_05_pptx_extraction_and_quiz(self):
        print("\n--- Running TEST 5: PPTX Ingestion & Quiz Generation ---")
        from pptx import Presentation
        from pptx.util import Inches, Pt
        
        pptx_path = os.path.join(self.temp_dir, "CPI_Methodology.pptx")
        prs = Presentation()
        
        # Slide 1
        slide1 = prs.slides.add_slide(prs.slide_layouts[0])
        slide1.shapes.title.text = "Consumer Price Index (CPI) Compilation in India"
        slide1.placeholders[1].text = "Price Statistics Division (PSD), MoSPI New Delhi"

        # Slide 2
        slide2 = prs.slides.add_slide(prs.slide_layouts[1])
        slide2.shapes.title.text = "Laspeyres Formula and Item Basket Weighting"
        slide2.placeholders[1].text = ("1. Base Year: Currently compiled with base year 2012=100.\n"
                                      "2. Basket: 299 items in Rural and 310 items in Urban baskets.\n"
                                      "3. Aggregation: Modified Laspeyres formula using geometric mean of price relatives.")

        prs.save(pptx_path)

        with open(pptx_path, "rb") as f:
            res = client.post(
                "/api/quiz/upload",
                files={"file": ("CPI_Methodology.pptx", f, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
                data={"employee_id": "OSS1001", "competency_tag": "Price Statistics", "title": "CPI Methodology Slides"}
            )
        self.assertEqual(res.status_code, 200, f"PPTX upload failed: {res.text}")
        data = res.json()
        self.assertEqual(data["file_type"], "PPTX")
        pptx_doc_id = data["id"]
        print(f"[OK] Ingested PPTX with ID {pptx_doc_id}, chunks: {data['chunk_count']}")

        # Generate Quiz from PPTX
        res_quiz = client.post(
            "/api/quiz/generate",
            json={
                "document_id": pptx_doc_id,
                "competency": "Price Statistics",
                "difficulty": "Intermediate",
                "num_questions": 3
            }
        )
        self.assertEqual(res_quiz.status_code, 200)
        qs = res_quiz.json()
        self.assertEqual(len(qs), 3)
        print(f"[OK] Generated {len(qs)} MCQs from PPTX.")

    # =========================================================================
    # TEST 6: DOCX Processing & Ingestion
    # =========================================================================
    def test_06_docx_extraction_and_ingestion(self):
        print("\n--- Running TEST 6: DOCX Ingestion ---")
        import docx
        docx_path = os.path.join(self.temp_dir, "PLFS_Survey_Design.docx")
        doc = docx.Document()
        doc.add_heading("Periodic Labour Force Survey (PLFS) Design", level=1)
        doc.add_paragraph("The Periodic Labour Force Survey is a nationwide survey conducted by the National Sample "
                          "Survey Office (NSSO) under MoSPI to estimate employment and unemployment indicators.")
        doc.add_paragraph("Key Activity Status Classifications:\n"
                          "1. Usual Principal Activity Status (UPS): Determines activity on which person spent relatively long time.\n"
                          "2. Usual Principal and Subsidiary Status (UPSS): Combines principal and subsidiary economic activities.\n"
                          "3. Current Weekly Status (CWS): Activity status based on reference period of 7 preceding days.")
        
        # Add table
        table = doc.add_table(rows=1, cols=2)
        hdr = table.rows[0].cells
        hdr[0].text = "Indicator Code"
        hdr[1].text = "Definition"
        r1 = table.add_row().cells
        r1[0].text = "LFPR"
        r1[1].text = "Labour Force Participation Rate = (Employed + Unemployed) / Population * 100"
        doc.save(docx_path)

        with open(docx_path, "rb") as f:
            res = client.post(
                "/api/quiz/upload",
                files={"file": ("PLFS_Survey_Design.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"employee_id": "OSS1001", "competency_tag": "Labour Statistics", "title": "PLFS Design Manual"}
            )
        self.assertEqual(res.status_code, 200, f"DOCX upload failed: {res.text}")
        data = res.json()
        self.assertEqual(data["file_type"], "DOCX")
        print(f"[OK] Ingested DOCX with ID {data['id']}, chunks: {data['chunk_count']}")

    # =========================================================================
    # TEST 7: TXT Processing & Ingestion
    # =========================================================================
    def test_07_txt_extraction_and_ingestion(self):
        print("\n--- Running TEST 7: UTF-8 TXT Ingestion ---")
        txt_path = os.path.join(self.temp_dir, "SDG_Indicators_NIF.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Sustainable Development Goals - National Indicator Framework (NIF)\n"
                    "Developed by Social Statistics Division, MoSPI.\n"
                    "Comprises 17 SDGs, 169 Global Targets, and 300+ National Indicators for India.\n"
                    "Data sources include NFHS, NSS Surveys, AISHE, and administrative data from line ministries.")

        with open(txt_path, "rb") as f:
            res = client.post(
                "/api/quiz/upload",
                files={"file": ("SDG_Indicators_NIF.txt", f, "text/plain")},
                data={"employee_id": "OSS1001", "competency_tag": "SDG Indicators", "title": "SDG NIF Overview"}
            )
        self.assertEqual(res.status_code, 200, f"TXT upload failed: {res.text}")
        data = res.json()
        self.assertEqual(data["file_type"], "TXT")
        print(f"[OK] Ingested TXT with ID {data['id']}, chunks: {data['chunk_count']}")

    # =========================================================================
    # TEST 8: Scanned / Empty Document Validation (Clear Error Response)
    # =========================================================================
    def test_08_empty_and_scanned_document_error_handling(self):
        print("\n--- Running TEST 8: Empty and Scanned File Validation ---")
        # 1. Empty 0-byte file
        empty_path = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_path, "w") as f:
            pass

        with open(empty_path, "rb") as f:
            res_empty = client.post(
                "/api/quiz/upload",
                files={"file": ("empty.txt", f, "text/plain")},
                data={"employee_id": "OSS1001", "competency_tag": "General"}
            )
        self.assertEqual(res_empty.status_code, 400)
        self.assertIn("empty", res_empty.json()["detail"].lower())
        print(f"[OK] Correctly rejected 0-byte empty file with 400.")

        # 2. PDF with no text (simulated scanned document)
        import fitz
        scanned_pdf_path = os.path.join(self.temp_dir, "scanned_doc.pdf")
        doc = fitz.open()
        doc.new_page() # blank page with no text
        doc.save(scanned_pdf_path)
        doc.close()

        with open(scanned_pdf_path, "rb") as f:
            res_scanned = client.post(
                "/api/quiz/upload",
                files={"file": ("scanned_doc.pdf", f, "application/pdf")},
                data={"employee_id": "OSS1001", "competency_tag": "General"}
            )
        self.assertEqual(res_scanned.status_code, 400)
        self.assertIn("scanned", res_scanned.json()["detail"].lower())
        print(f"[OK] Correctly detected scanned/image PDF: '{res_scanned.json()['detail']}'")

    # =========================================================================
    # TEST 9: RAG Search Diagnostic Endpoint
    # =========================================================================
    def test_09_rag_search_diagnostic(self):
        print("\n--- Running TEST 9: RAG Search Diagnostic Endpoint ---")
        doc_id = getattr(self, "pdf_doc_id", None)
        
        res = client.post(
            "/api/quiz/search",
            params={
                "document_id": doc_id,
                "query": "FISIM financial intermediation interest spread",
                "top_k": 2
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"RAG Search Query: '{data['query']}', Found: {len(data['results'])} chunks")
        self.assertGreater(len(data["results"]), 0)
        top_result = data["results"][0]
        self.assertIn("similarity_score", top_result)
        self.assertIn("excerpt", top_result)
        print(f"Top Similarity Score: {top_result['similarity_score']}, Excerpt: {top_result['excerpt'][:100]}...")

    # =========================================================================
    # TEST 10: AI Health Endpoint
    # =========================================================================
    def test_10_ai_health_endpoint(self):
        print("\n--- Running TEST 10: AI Health Endpoint ---")
        res = client.get("/api/ai/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ollama_connected", data)
        self.assertIn("active_model", data)
        self.assertIn("embedding_model", data)
        print(f"[OK] AI Health: {data}")


if __name__ == "__main__":
    unittest.main()

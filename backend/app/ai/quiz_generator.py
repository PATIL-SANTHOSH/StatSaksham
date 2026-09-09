import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ai.ollama_client import ollama_client
from app.ai.rag_engine import rag_engine
from app.ai.fallback_ai import fallback_ai
from app.models.quiz import QuizDocument, QuizChunk, QuizQuestion

class QuizGenerator:
    def __init__(self, db: Session):
        self.db = db

    def generate_quiz_from_document(
        self,
        document_id: int,
        competency: str = "General Statistics",
        difficulty: str = "Intermediate",
        num_questions: int = 5
    ) -> List[QuizQuestion]:
        doc = self.db.query(QuizDocument).filter(QuizDocument.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found")

        chunks = self.db.query(QuizChunk).filter(QuizChunk.document_id == document_id).order_by(QuizChunk.chunk_index).all()
        if not chunks:
            raise ValueError(f"No indexed text chunks found for document {document_id}")

        # Use semantic RAG search to retrieve the most informative chunks
        chunk_dicts = [
            {
                "id": c.id,
                "chunk_index": c.chunk_index,
                "content": c.content,
                "embedding_json": c.embedding_json
            }
            for c in chunks
        ]

        if len(chunk_dicts) <= 6:
            selected_chunks = chunk_dicts
        else:
            search_query = f"{competency} statistical definitions concepts methodology formula guidelines"
            selected_chunks = rag_engine.similarity_search(search_query, chunk_dicts, top_k=6)

        # Build context with chunk/page markers
        context_blocks = []
        for c in selected_chunks:
            context_blocks.append(f"[Excerpt {c['chunk_index'] + 1}]:\n{c['content']}")
        full_context = "\n\n".join(context_blocks)

        generated_raw_questions = []

        # 1. Try LLM generation if Ollama is available
        if ollama_client.is_available() and len(full_context.strip()) > 30:
            llm_questions = self._generate_with_llm(
                context=full_context,
                competency=competency,
                difficulty=difficulty,
                num_questions=num_questions,
                filename=doc.filename
            )
            if llm_questions:
                generated_raw_questions = llm_questions

        # 2. If LLM returned partial/no questions, use grounded fallback
        if len(generated_raw_questions) < num_questions:
            print(f"[QuizGenerator] Using grounded fallback for remaining {num_questions - len(generated_raw_questions)} questions...")
            fallback_qs = fallback_ai.generate_quiz_fallback(
                text=full_context,
                competency=competency,
                difficulty=difficulty,
                num_questions=num_questions
            )
            needed = num_questions - len(generated_raw_questions)
            generated_raw_questions.extend(fallback_qs[:needed])

        # 3. Validate & Save to database
        saved_questions = []
        for q_data in generated_raw_questions[:num_questions]:
            # Validate options
            opt_a = str(q_data.get("option_a", "")).strip() or "Option A"
            opt_b = str(q_data.get("option_b", "")).strip() or "Option B"
            opt_c = str(q_data.get("option_c", "")).strip() or "Option C"
            opt_d = str(q_data.get("option_d", "")).strip() or "Option D"
            
            corr = str(q_data.get("correct_option", "A")).upper().strip()
            if corr not in ["A", "B", "C", "D"]:
                corr = "A"

            matched_chunk = chunks[0] if chunks else None
            source_ref = q_data.get("source_reference")
            if not source_ref or "Document:" not in source_ref:
                source_ref = f"Document: {doc.filename}"

            question = QuizQuestion(
                document_id=doc.id,
                chunk_id=matched_chunk.id if matched_chunk else None,
                question_text=q_data.get("question_text", "Sample Question"),
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_option=corr,
                explanation=q_data.get("explanation", f"Based on {doc.filename} material."),
                competency=competency,
                difficulty=difficulty,
                source_reference=source_ref
            )
            self.db.add(question)
            saved_questions.append(question)

        self.db.commit()
        for q in saved_questions:
            self.db.refresh(q)

        return saved_questions

    def _generate_with_llm(
        self,
        context: str,
        competency: str,
        difficulty: str,
        num_questions: int,
        filename: str
    ) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an assessment designer for India's Ministry of Statistics (MoSPI). "
            "Generate multiple choice questions (MCQs) strictly and factually based on the provided text excerpts. "
            "Each question must have 4 distinct options (A, B, C, D) and exactly 1 correct answer. "
            "Output JSON ONLY as a list of question objects."
        )

        user_prompt = f"""Based ONLY on the following learning material excerpt from '{filename}', generate exactly {num_questions} multiple choice questions.

TARGET COMPETENCY: {competency}
DIFFICULTY: {difficulty}

EXCERPT:
\"\"\"
{context[:4000]}
\"\"\"

Return a valid JSON array matching this exact schema:
[
  {{
    "question_text": "Clear conceptual question",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_option": "A",
    "explanation": "Explanation citing the material",
    "competency": "{competency}",
    "difficulty": "{difficulty}",
    "source_reference": "Document: {filename}"
  }}
]

JSON ONLY:"""

        response = ollama_client.generate(
            prompt=user_prompt, 
            system=system_prompt, 
            json_mode=True,
            max_tokens=1200
        )
        if not response:
            return []

        return self._parse_and_validate_questions(response, competency, difficulty, filename)

    def _parse_and_validate_questions(
        self, 
        raw_text: str, 
        competency: str, 
        difficulty: str, 
        filename: str
    ) -> List[Dict[str, Any]]:
        parsed = None

        # Clean markdown codeblocks
        cleaned = re.sub(r'```json\s*', '', raw_text)
        cleaned = re.sub(r'```\s*', '', cleaned).strip()

        # 1. Direct JSON parse
        try:
            parsed = json.loads(cleaned)
        except Exception:
            # 2. Extract bracketed array
            match = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    pass

        if not parsed:
            # 3. Fallback: search for object wrapper
            match_obj = re.search(r'\{\s*".*"\s*:\s*\[.*\]\s*\}', cleaned, re.DOTALL)
            if match_obj:
                try:
                    obj_data = json.loads(match_obj.group(0))
                    for val in obj_data.values():
                        if isinstance(val, list):
                            parsed = val
                            break
                except Exception:
                    pass

        if not isinstance(parsed, list):
            return []

        valid_questions = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            
            q_text = item.get("question_text") or item.get("question")
            opt_a = item.get("option_a") or item.get("a")
            opt_b = item.get("option_b") or item.get("b")
            opt_c = item.get("option_c") or item.get("c")
            opt_d = item.get("option_d") or item.get("d")
            corr = str(item.get("correct_option") or item.get("correct_answer") or item.get("answer") or "A").upper().strip()
            
            # Map full answer text to option letter if LLM returned text
            if len(corr) > 1:
                if corr.lower() == str(opt_a).lower():
                    corr = "A"
                elif corr.lower() == str(opt_b).lower():
                    corr = "B"
                elif corr.lower() == str(opt_c).lower():
                    corr = "C"
                elif corr.lower() == str(opt_d).lower():
                    corr = "D"
                else:
                    corr = corr[0] if corr[0] in "ABCD" else "A"

            if corr not in ["A", "B", "C", "D"]:
                corr = "A"

            if q_text and opt_a and opt_b and opt_c and opt_d:
                valid_questions.append({
                    "question_text": str(q_text).strip(),
                    "option_a": str(opt_a).strip(),
                    "option_b": str(opt_b).strip(),
                    "option_c": str(opt_c).strip(),
                    "option_d": str(opt_d).strip(),
                    "correct_option": corr,
                    "explanation": str(item.get("explanation", "")).strip(),
                    "competency": competency,
                    "difficulty": difficulty,
                    "source_reference": str(item.get("source_reference", f"Document: {filename}"))
                })

        return valid_questions

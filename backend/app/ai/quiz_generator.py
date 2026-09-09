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
        chunk_texts = [c.content for c in chunks]
        full_context = "\n\n".join(chunk_texts[:10])

        generated_raw_questions = []

        # Try LLM generation first if Ollama is available
        if ollama_client.is_available() and full_context.strip():
            llm_questions = self._generate_with_llm(full_context, competency, difficulty, num_questions)
            if llm_questions:
                generated_raw_questions = llm_questions

        # If LLM didn't return enough questions or was offline, use intelligent fallback
        if len(generated_raw_questions) < num_questions:
            fallback_qs = fallback_ai.generate_quiz_fallback(
                text=full_context,
                competency=competency,
                difficulty=difficulty,
                num_questions=num_questions
            )
            # Fill in remainder
            needed = num_questions - len(generated_raw_questions)
            generated_raw_questions.extend(fallback_qs[:needed])

        # Save to database
        saved_questions = []
        for q_data in generated_raw_questions:
            # Find matching chunk if possible
            matched_chunk = chunks[0] if chunks else None
            
            question = QuizQuestion(
                document_id=doc.id,
                chunk_id=matched_chunk.id if matched_chunk else None,
                question_text=q_data["question_text"],
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct_option=q_data["correct_option"].upper().strip(),
                explanation=q_data.get("explanation", ""),
                competency=competency,
                difficulty=difficulty,
                source_reference=q_data.get("source_reference", f"From document: {doc.filename}")
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
        num_questions: int
    ) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an expert psychometrician and statistical education designer for India's Ministry of Statistics (MoSPI). "
            "Generate high-quality multiple choice questions (MCQs) strictly based on the provided learning material. "
            "Output valid JSON ONLY matching the requested structure."
        )

        user_prompt = f"""Based ONLY on the following learning material excerpt, generate exactly {num_questions} multiple choice questions (MCQs).

TARGET COMPETENCY: {competency}
DIFFICULTY: {difficulty} (Appropriate for Government Statistical Officials)

EXCERPT:
\"\"\"
{context[:3500]}
\"\"\"

Output format MUST be a JSON list of objects with these exact keys:
[
  {{
    "question_text": "Clear professional question text",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_option": "A", // Must be one of 'A', 'B', 'C', or 'D'
    "explanation": "Detailed explanation citing the text rationale",
    "competency": "{competency}",
    "difficulty": "{difficulty}",
    "source_reference": "Specific concept or section cited from the material"
  }}
]

JSON ONLY:"""

        response = ollama_client.generate(user_prompt, system=system_prompt, json_mode=True)
        if not response:
            return []

        try:
            # Parse JSON
            data = json.loads(response)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Search for list in dict values
                for v in data.values():
                    if isinstance(v, list) and len(v) > 0 and "question_text" in v[0]:
                        return v
        except Exception as e:
            # Try regex extraction of JSON list
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            print(f"[QuizGenerator] JSON parsing error: {e}")

        return []

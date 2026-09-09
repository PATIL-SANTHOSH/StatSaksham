import re
import random
from typing import List, Dict, Any, Optional

class FallbackAIService:
    """
    Intelligent Heuristic / Rule-based NLP fallback service ensuring
    StatSaksham never breaks even if local Ollama is offline.
    """

    STATISTICAL_KNOWLEDGE_BASE = {
        "national accounts": (
            "National Accounts in India follow the System of National Accounts (SNA 2008) standard. "
            "Key metrics include Gross Domestic Product (GDP), Gross Value Added (GVA) at basic prices, "
            "Net Domestic Product (NDP), and Gross Fixed Capital Formation (GFCF). "
            "MoSPI's National Accounts Division (NAD) releases quarterly and annual estimates."
        ),
        "sampling": (
            "Sampling techniques in MoSPI surveys include Stratified Multi-Stage Sampling. "
            "First Stage Units (FSUs) are typically 2011 Census Villages (Rural) or Urban Frame Survey (UFS) blocks (Urban). "
            "Ultimate Stage Units (USUs) are sample households or enterprises. Weights (multipliers) are applied for population estimates."
        ),
        "survey design": (
            "Survey Design in India's National Sample Survey (NSS) involves questionnaire design, "
            "sampling frame preparation, stratification, allocation of sample sizes across sectors/states, "
            "and quality control measures through Field Operations Division (FOD)."
        ),
        "price statistics": (
            "Price Statistics are compiled by the Price Statistics Division (PSD) under MoSPI. "
            "Consumer Price Index (CPI) measures price changes in a basket of consumer goods & services (Rural, Urban, Combined). "
            "Index of Industrial Production (IIP) and Wholesale Price Index (WPI) track production and wholesale price trends."
        ),
        "python": (
            "In official statistical workflows, Python is used for data wrangling with pandas, "
            "survey analysis with numpy/scipy, data visualization with matplotlib/seaborn, "
            "and automated ETL pipelines for large-scale survey datasets like NSS, PLFS, and ASI."
        ),
        "r programming": (
            "R is heavily utilized in statistical computing, survey data analysis (using the 'survey' package), "
            "time-series econometrics, and demographic estimation in official statistical systems."
        ),
        "sdg": (
            "Sustainable Development Goals (SDG) National Indicator Framework (NIF) is coordinated by MoSPI "
            "to monitor progress on 17 UN SDGs with 300+ national indicators across social, economic, and environmental domains."
        )
    }

    def generate_quiz_fallback(
        self,
        text: str,
        competency: str = "Statistical Analysis",
        difficulty: str = "Intermediate",
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract meaningful sentences and build realistic MCQs from raw or chunked text.
        """
        # Clean text
        clean_text = re.sub(r'\s+', ' ', text).strip()
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', clean_text) if len(s.strip()) > 35]

        questions: List[Dict[str, Any]] = []

        # If text is too short, augment with domain statistical knowledge
        if len(sentences) < num_questions:
            domain_key = "national accounts"
            for k in self.STATISTICAL_KNOWLEDGE_BASE:
                if k in competency.lower() or k in text.lower():
                    domain_key = k
                    break
                extra_text = self.STATISTICAL_KNOWLEDGE_BASE[domain_key]
                sentences.extend([s.strip() for s in re.split(r'(?<=[.!?]) +', extra_text) if len(s.strip()) > 25])

        for idx, sentence in enumerate(sentences[:num_questions]):
            words = [w for w in re.findall(r'\b[A-Za-z]{4,}\b', sentence) if w.lower() not in [
                'this', 'that', 'with', 'from', 'have', 'were', 'which', 'their', 'about', 'under', 'these', 'those'
            ]]
            
            if not words:
                continue

            target_word = words[min(len(words)-1, idx % len(words))]
            
            # Create a fill-in or conceptual question
            blank_sentence = re.sub(rf'\b{re.escape(target_word)}\b', '______', sentence, count=1, flags=re.IGNORECASE)
            q_text = f"According to the learning material, complete the statement: \"{blank_sentence}\""

            # Distractor generation
            statistical_distractors = [
                "Systematic Calibration", "Variance Estimation", "Aggregated Index", "Stratified Multi-Stage",
                "Gross Value Added", "Confidence Interval", "Sampling Multiplier", "Standard Error",
                "Metadata Standard", "Data Imputation", "Harmonized Classification", "Survey Frame"
            ]
            random.shuffle(statistical_distractors)
            
            distractors = [d for d in statistical_distractors if d.lower() != target_word.lower()][:3]
            
            options = [target_word] + distractors
            random.shuffle(options)
            
            correct_idx = options.index(target_word)
            correct_letter = ["A", "B", "C", "D"][correct_idx]

            questions.append({
                "question_text": q_text,
                "option_a": options[0],
                "option_b": options[1],
                "option_c": options[2],
                "option_d": options[3],
                "correct_option": correct_letter,
                "explanation": f"Based on the text: '{sentence}', the correct term is '{target_word}'.",
                "competency": competency,
                "difficulty": difficulty,
                "source_reference": f"Section extract: \"{sentence[:80]}...\""
            })

            if len(questions) >= num_questions:
                break

        # If still need questions, add well-formed domain questions
        while len(questions) < num_questions:
            q_idx = len(questions) + 1
            questions.append({
                "question_text": f"What is the primary objective of data quality frameworks in {competency}?",
                "option_a": "To ensure accuracy, consistency, timeliness, and international comparability of official data",
                "option_b": "To eliminate the need for primary data collection surveys",
                "option_c": "To restrict public access to raw census microdata",
                "option_d": "To replace all sampling methodologies with complete enumeration",
                "correct_option": "A",
                "explanation": "Data quality frameworks establish strict benchmarks for statistical validity, accuracy, and reliability across official statistical agencies.",
                "competency": competency,
                "difficulty": difficulty,
                "source_reference": "National Statistical System Quality Standards"
            })

        return questions

    def get_assistant_response(
        self,
        user_message: str,
        employee_name: str = "Officer",
        job_role: str = "Statistical Official",
        document_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate contextual assistance for MoSPI learners.
        """
        msg_lower = user_message.lower()

        # Check document context first
        if document_context and len(document_context.strip()) > 20:
            return {
                "message": (
                    f"**Analysis of Uploaded Material**:\n\n"
                    f"Based on your document extract:\n> *\"{document_context[:250]}...\"*\n\n"
                    f"Key insight for your role as **{job_role}**: This material provides essential background for closing competency gaps. "
                    f"You can generate an AI Quiz directly from this document to assess and update your competency score in the system."
                ),
                "sources": ["Uploaded Document Excerpt", "StatSaksham RAG Engine"],
                "model_used": "StatSaksham Heuristic Rule Engine (Fallback Active)"
            }

        # Match domain topics
        for domain, info in self.STATISTICAL_KNOWLEDGE_BASE.items():
            if domain in msg_lower:
                return {
                    "message": (
                        f"Hello {employee_name}!\n\n"
                        f"Here is relevant domain intelligence for **{domain.title()}**:\n\n"
                        f"{info}\n\n"
                        f"**Competency Guidance for {job_role}**:\n"
                        f"- For your role, target reaching at least Level 4 (Advanced).\n"
                        f"- Check the **Personalized Learning Path** tab to view recommended iGOT Karmayogi modules and NSSTA workshops on this topic."
                    ),
                    "sources": ["MoSPI Official Statistics Reference Manual", "iGOT Competency Framework"],
                    "model_used": "StatSaksham Knowledge Engine (Fallback Active)"
                }

        # Check gap / recommendation inquiry
        if "gap" in msg_lower or "skill" in msg_lower or "recommend" in msg_lower:
            return {
                "message": (
                    f"Hello {employee_name},\n\n"
                    f"StatSaksham evaluates your skill gaps using the deterministic formula:\n"
                    f"$$\\text{{Skill Gap}} = \\max(0, \\text{{Required Level}} - \\text{{Current Level}})$$\n\n"
                    f"Your personalized recommendations combine gap severity, role priority weights, and your current assignment.\n\n"
                    f"To close your active gaps:\n"
                    f"1. Navigate to **Skill Gap Analysis** to view priority rankings.\n"
                    f"2. Enroll in targeted **iGOT Karmayogi** or **NSSTA** courses.\n"
                    f"3. Take an assessment or upload learning materials for an **AI Quiz** to update your certified competency level."
                ),
                "sources": ["StatSaksham Competency Architecture Guide"],
                "model_used": "StatSaksham Rules Engine"
            }

        # Default fallback response
        return {
            "message": (
                f"Greetings {employee_name}! I am your **StatSaksham AI Learning Assistant**.\n\n"
                f"I am designed to assist officers in India's Official Statistical System with:\n"
                f"1. **Statistical Methodologies**: Survey Design, National Accounts, Sampling, Price Indices (CPI/IIP), and SDG Indicators.\n"
                f"2. **Technical Tools**: Python, R, SQL, and Geospatial Analysis for official statistics.\n"
                f"3. **Skill Gap Guidance**: Interpreting required competency levels for your role as *{job_role}*.\n"
                f"4. **Document Q&A**: Upload PDFs or PPTXs to generate customized quizzes and extract key concepts.\n\n"
                f"How may I assist your capacity-building journey today?"
            ),
            "sources": ["StatSaksham AI Core Knowledge Base"],
            "model_used": "StatSaksham Intelligent Assistant"
        }

fallback_ai = FallbackAIService()

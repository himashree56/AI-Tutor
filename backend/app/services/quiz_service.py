import json
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.llm.local_model import llm_service
from app.rag.retriever import retriever_service
from app.rag.prompt_builder import prompt_builder
from app.core.config import settings
from app.utils.logger import logger


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    answer: str
    evidence_quote: str = ""
    hint: str = ""


@dataclass
class QuizResult:
    questions: List[QuizQuestion]
    topic: str
    num_generated: int


class QuizService:
    def __init__(self):
        self.llm = llm_service
        self.retriever = retriever_service
        self.prompt_builder = prompt_builder
        self.num_questions = settings.quiz_num_questions

    async def generate_quiz(
        self,
        topic: Optional[str] = None,
        context: Optional[str] = None,
        num_questions: Optional[int] = None
    ) -> QuizResult:
        num_q = num_questions or self.num_questions
        
        # Sanitize topic (strip newlines and extra spaces)
        if topic:
            topic = topic.strip().replace("\n", " ").replace("\r", " ")
        
        if context is None:
            if topic:
                context = await self._get_context_for_topic(topic)
            else:
                raise ValueError("Either topic or context must be provided")
        
        # BULLETPROOF RULE: If context is empty, don't even call the LLM
        if not context or context.strip() == "":
            logger.warning(f"No context found for topic '{topic}'. Refusing LLM call.")
            return QuizResult(
                questions=[QuizQuestion(
                    question=f"I could not find enough information about '{topic}' in the document to generate a quiz.",
                    options=[],
                    answer="",
                    evidence_quote="",
                    hint="Try using different keywords like 'Digital Literacy' or 'Activity 1'."
                )],
                topic=topic or "General",
                num_generated=0
            )

        prompt = self.prompt_builder.build_quiz_prompt(
            context=context,
            topic=topic,
            num_questions=num_q
        )
        
        response = await self.llm.generate(
            prompt,
            temperature=settings.quiz_temperature
        )
        
        if not response or response.strip() == "":
            logger.error("LLM returned an empty response for quiz generation")
            return QuizResult(
                questions=[QuizQuestion(
                    question="The AI could not generate questions at this time. Please try again.",
                    options=[],
                    answer="",
                    hint="This might be due to a temporary API issue."
                )],
                topic=topic or "General",
                num_generated=0
            )

        questions = self._parse_quiz_response(response)
        
        if len(questions) == 0:
            logger.error(f"Failed to generate ANY questions for topic '{topic}'. Raw LLM response: {response[:1000]}")
        elif len(questions) < num_q:
            logger.warning(
                f"Generated only {len(questions)} questions, expected {num_q}"
            )
        
        return QuizResult(
            questions=questions,
            topic=topic or "General",
            num_generated=len(questions)
        )

    async def _get_context_for_topic(self, topic: str, top_k: int = 10) -> str:
        chunks = await self.retriever.retrieve(
            query=topic,
            top_k=top_k,
            use_reranker=True
        )
        
        if not chunks:
            return "" # Return empty so prompt builder can handle "No context" state correctly
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("source", "Unknown")
            page = chunk.metadata.get("page", "N/A")
            context_parts.append(
                f"[Source {i}] (Page {page}, {source}):\n{chunk.text}"
            )
        
        return "\n\n".join(context_parts)

    def _parse_quiz_response(self, response: str) -> List[QuizQuestion]:
        questions = []
        
        try:
            # 1. Clean response (remove markdown code blocks if present)
            clean_response = response.strip()
            if clean_response.startswith("```"):
                # Find the first { after the start
                start_json = clean_response.find("{")
                end_json = clean_response.rfind("}")
                if start_json != -1 and end_json != -1:
                    clean_response = clean_response[start_json:end_json+1]
            
            # 2. Try primary regex search for "questions" block
            json_match = re.search(
                r'\{[\s\S]*"questions"[\s\S]*\}',
                clean_response
            )
            
            if json_match:
                json_str = json_match.group()
            else:
                # 3. Fallback: find first { and last }
                start_idx = clean_response.find("{")
                end_idx = clean_response.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    json_str = clean_response[start_idx:end_idx+1]
                else:
                    json_str = "{}" # Force fallback to markdown parser
            
            # Clean up common LLM mistake: trailing commas
            json_str = re.sub(r',\s*([\]\}])', r'\1', json_str)
            
            try:
                data = json.loads(json_str)
                
                for q in data.get("questions", []):
                    # Robust answer extraction: check multiple keys and clean the value
                    answer = (
                        q.get("answer") or 
                        q.get("correct_answer") or 
                        q.get("correct") or 
                        q.get("ans") or 
                        ""
                    )
                    
                    # Ensure answer is just a single uppercase letter (e.g. "A" instead of "A. Option A" or "A.")
                    if isinstance(answer, str) and answer:
                        answer_match = re.search(r'[A-D]', answer.upper())
                        if answer_match:
                            answer = answer_match.group()
                    
                    if not answer:
                         logger.warning(f"Question missing answer: {q.get('question', 'Unknown')}. Full item: {q}")

                    questions.append(QuizQuestion(
                        question=q.get("question", ""),
                        options=q.get("options", []),
                        answer=str(answer),
                        evidence_quote=q.get("evidence_quote", ""),
                        hint=q.get("hint", "")
                    ))
            except json.JSONDecodeError:
                # 4. Fallback to markdown parser if JSON is still malformed
                logger.warning("JSON parsing failed, falling back to markdown parser")
                questions = self._parse_markdown_quiz(response)
                
        except Exception as e:
            logger.error(f"Quiz parsing error: {str(e)}. Raw response: {response[:500]}...")
        
        return questions

    def _parse_markdown_quiz(self, text: str) -> List[QuizQuestion]:
        questions = []
        blocks = re.split(r'\n(?=\d+\.)', text)
        
        for block in blocks:
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            question_line = lines[0].strip()
            question_match = re.search(r'\d+\.\s*(.+)', question_line)
            
            if not question_match:
                continue
            
            question_text = question_match.group(1).replace("?", "")
            
            options = []
            answer = ""
            hint = ""
            
            for line in lines[1:]:
                if line.lower().startswith("hint:"):
                    hint = line[5:].strip()
                    continue
                opt_match = re.match(r'\s*([A-D])\.\s*(.+)', line)
                if opt_match:
                    letter = opt_match.group(1)
                    text = opt_match.group(2).strip()
                    options.append(f"{letter}. {text}")
                    
                    if "*" in text or "✓" in text:
                        answer = letter
            
            if options and len(options) == 4:
                if not answer:
                    answer = "A"
                
                questions.append(QuizQuestion(
                    question=question_text + "?",
                    options=options,
                    answer=answer,
                    hint=hint
                ))
        
        return questions


quiz_service = QuizService()

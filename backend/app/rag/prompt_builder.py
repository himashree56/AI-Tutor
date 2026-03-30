from typing import List, Dict, Any

from app.rag.retriever import RetrievedChunk


class PromptBuilder:
    SYSTEM_PROMPT = """You are an expert AI Tutor. Your role is to help students learn by answering questions based on the provided context from educational materials.

IMPORTANT RULES:
1. ONLY answer questions based on the provided context below
2. If the context doesn't contain enough information to fully answer the question, say so clearly
3. ALWAYS cite your sources using the format [Source X] where X is the source number
4. Be educational and helpful - explain concepts clearly
5. If you need to make assumptions, clearly state them
6. Do not hallucinate or make up information not present in the context

CONTEXT FROM DOCUMENT(S):
{context}

CONVERSATION HISTORY:
{history}

Current Question: {query}

Your Answer (cite sources as [Source X]):"""

    QUIZ_SYSTEM_PROMPT = """You are an expert quiz generator. Your task is to generate questions ONLY from the provided context that relate DIRECTLY to the specified topic: "{topic}".

RULES:
1. Generate exactly {num_questions} questions about "{topic}".
2. STRICT TOPIC ADHERENCE: All questions must relate to "{topic}". Do not ask about other concepts in the context (like general location potential, or unrelated parameters) unless they explain or involve "{topic}".
3. Each question MUST have exactly 4 options (A, B, C, D)
4. FORBIDDEN: Do not generate questions about the "process of learning", "how to write a summary", or "general concepts". 
5. GROUNDEDNESS: For EACH question, you MUST provide the `evidence_quote` which is a verbatim sentence from the provided context below.
6. If the context is insufficient or empty for the topic "{topic}", do not guess. 

CONTEXT:
{context}

OUTPUT FORMAT (JSON only):
{{
    "questions": [
        {{
            "question": "Question about {topic} based ONLY on the context?",
            "options": ["A. Option A", "B. Option B", "C. Option C", "D. Option D"],
            "answer": "A",
            "evidence_quote": "Verbatim sentence from the context here.",
            "hint": "A helpful hint based on the evidence."
        }}
    ]
}}"""

    EVALUATION_PROMPT = """Evaluate the following answer based on the context and question.

Question: {question}
Ground Truth Context: {context}
User's Answer: {answer}

Evaluate the answer on:
1. Faithfulness (does it stick to the context?)
2. Relevance (does it address the question?)
3. Correctness (is it factually accurate?)

Provide scores 0-1 for each criterion and explain briefly."""

    def build_rag_prompt(
        self,
        query: str,
        retrieved_chunks: List[RetrievedChunk],
        history: str = ""
    ) -> str:
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.metadata.get("source", "Unknown")
            page = chunk.metadata.get("page", "N/A")
            context_parts.append(
                f"[Source {i}] (Page {page}, {source}):\n{chunk.text}"
            )
        
        context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
        
        return self.SYSTEM_PROMPT.format(
            context=context,
            history=history or "No previous conversation.",
            query=query
        )

    def build_quiz_prompt(
        self,
        context: str,
        topic: str,
        num_questions: int = 5
    ) -> str:
        return self.QUIZ_SYSTEM_PROMPT.format(
            context=context,
            topic=topic,
            num_questions=num_questions
        )

    def build_evaluation_prompt(
        self,
        question: str,
        context: str,
        answer: str
    ) -> str:
        return self.EVALUATION_PROMPT.format(
            question=question,
            context=context,
            answer=answer
        )

    def extract_sources(
        self,
        retrieved_chunks: List[RetrievedChunk]
    ) -> List[Dict[str, Any]]:
        sources = []
        seen = set()
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            source_name = chunk.metadata.get("source", "Unknown")
            if source_name not in seen:
                seen.add(source_name)
                sources.append({
                    "id": i,
                    "source": source_name,
                    "page": chunk.metadata.get("page", "N/A"),
                    "text_preview": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                    "score": chunk.score
                })
        
        return sources


prompt_builder = PromptBuilder()

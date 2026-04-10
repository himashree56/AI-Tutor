import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.quiz_service import QuizService

def test_robust_parser():
    service = QuizService()
    
    # Test 1: Standard JSON
    res1 = '{"questions": [{"question": "Q1?", "options": ["A", "B"], "answer": "B"}]}'
    q1 = service._parse_quiz_response(res1)
    assert q1[0].answer == "B"
    
    # Test 2: Alternative key (correct_answer)
    res2 = '{"questions": [{"question": "Q2?", "options": ["A", "B"], "correct_answer": "A"}]}'
    q2 = service._parse_quiz_response(res2)
    assert q2[0].answer == "A"
    
    # Test 3: Mixed characters in answer (e.g. "A.")
    res3 = '{"questions": [{"question": "Q3?", "options": ["A", "B"], "answer": "C."}]}'
    q3 = service._parse_quiz_response(res3)
    assert q3[0].answer == "C"
    
    # Test 4: Ans key
    res4 = '{"questions": [{"question": "Q4?", "options": ["A", "B"], "ans": "D"}]}'
    q4 = service._parse_quiz_response(res4)
    assert q4[0].answer == "D"
    
    # Test 5: Full option in answer
    res5 = '{"questions": [{"question": "Q5?", "options": ["A", "B"], "answer": "A. Option A"}]}'
    q5 = service._parse_quiz_response(res5)
    assert q5[0].answer == "A"

    print("✅ All robust parser tests passed!")

if __name__ == "__main__":
    test_robust_parser()

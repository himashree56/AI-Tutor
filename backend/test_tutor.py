import requests
import json
import os

BASE_URL = "http://127.0.0.1:8001"

def print_header(title):
    print(f"\n{'='*50}\n {title}\n{'='*50}")

def chat():
    print_header("AI TUTOR CHAT")
    message = input("Ask a question about the document: ")
    
    url = f"{BASE_URL}/chat/stream"
    payload = {"query": message, "session_id": "cli_test_session"}
    
    print("\nAI Thinking...", end="", flush=True)
    try:
        with requests.post(url, json=payload, stream=True) as r:
            print("\r" + " " * 20 + "\r", end="") # clear line
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data = decoded[6:]
                        try:
                            chunk = json.loads(data)
                            if "done" in chunk: break
                            if "token" in chunk:
                                print(chunk["token"], end="", flush=True)
                        except:
                            pass
        print("\n")
    except Exception as e:
        print(f"\nError: {e}")

def quiz():
    print_header("QUIZ GENERATOR")
    topic = input("Enter topic for quiz (e.g. 'Activity 1 summary'): ").strip()
    
    url = f"{BASE_URL}/generate-quiz/"
    payload = {"topic": topic, "num_questions": 3}
    
    print("Generating Quiz...")
    try:
        res = requests.post(url, json=payload)
        questions = res.json().get("questions", [])
        if not questions:
            print("No questions were generated. Check server logs.")
            return
        for i, q in enumerate(questions, 1):
            print(f"\nQ{i}: {q['question']}")
            for opt in q['options']:
                print(f"   {opt}")
            print(f"Correct Answer: {q['answer']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        print("\n--- AI TUTOR TEST MENU ---")
        print("1. Chat with Document")
        print("2. Generate Quiz")
        print("3. Exit")
        choice = input("\nSelect an option: ")
        
        if choice == '1': chat()
        elif choice == '2': quiz()
        elif choice == '3': break

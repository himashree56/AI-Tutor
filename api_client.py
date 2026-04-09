import requests
from config import API_BASE_URL

# ✅ Health check
def check_health():
    res = requests.get(f"{API_BASE_URL}/health")
    return res.json()


# ✅ Chat endpoint
def chat(message):
    payload = {
        "message": message,
        "session_id": "student1"
    }

    res = requests.post(
        f"{API_BASE_URL}/chat/",
        json=payload
    )

    return res.json()


# ✅ Generate Quiz
def generate_quiz(topic):
    payload = {
        "topic": topic
    }

    res = requests.post(
        f"{API_BASE_URL}/generate-quiz/",
        json=payload
    )

    return res.json()
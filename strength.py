import re
import math

COMMON_PASSWORDS = ["123456", "password", "qwerty", "admin"]

def calculate_entropy(password):
    charset = 0
    if re.search(r"[a-z]", password): charset += 26
    if re.search(r"[A-Z]", password): charset += 26
    if re.search(r"[0-9]", password): charset += 10
    if re.search(r"[!@#$%^&*()_+=-]", password): charset += 32

    if charset == 0:
        return 0

    return round(math.log2(charset ** len(password)), 2)

def analyze_password(password):
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 30
    elif len(password) >= 8:
        score += 20
    else:
        feedback.append("Password too short")

    if re.search(r"[A-Z]", password): score += 10
    else: feedback.append("Add uppercase letters")

    if re.search(r"[a-z]", password): score += 10
    else: feedback.append("Add lowercase letters")

    if re.search(r"[0-9]", password): score += 10
    else: feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*()_+=-]", password): score += 10
    else: feedback.append("Add special characters")

    if password.lower() in COMMON_PASSWORDS:
        return {"score": 0, "strength": "Very Weak", "feedback": ["Common password detected"]}

    entropy = calculate_entropy(password)
    score += min(int(entropy / 10), 20)

    strength = "Weak"
    if score >= 70:
        strength = "Strong"
    elif score >= 40:
        strength = "Medium"

    return {
        "score": score,
        "strength": strength,
        "entropy": entropy,
        "feedback": feedback
    }

#!/usr/bin/env python3
"""
simple_offline_chatbot.py

A simple offline chatbot for answering questions about Moringa School course offerings.

USAGE:
    python simple_offline_chatbot.py

    The bot will start an interactive session. Type your questions and press Enter.
    Type 'quit' or 'exit' to end the session, or press Ctrl+D (Unix) / Ctrl+Z (Windows).

FEATURES:
    - Recognizes general commands: hello, help, study
    - Answers questions about Moringa School courses across multiple categories
    - Logs unrecognized queries to errors_log.csv for improvement tracking
    - Case-insensitive keyword matching with robust normalization

EXTENDING:
    To add new courses or responses, edit the RESPONSES dictionary below.
    Follow the existing pattern: map keywords to response strings.
"""

import csv
import re
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, List

# ============================================================================
# CONFIGURATION
# ============================================================================

# CSV file for logging unknown queries
ERROR_LOG_CSV = "errors_log.csv"

# Default response for unrecognized input
UNKNOWN_RESPONSE = "I'm still learning!"

# ============================================================================
# PRESET RESPONSES DATABASE
# ============================================================================
# This dictionary maps normalized keywords/phrases to bot responses.
# Keys should be lowercase; matching is case-insensitive.
# To add new courses: add entries following the existing pattern.

RESPONSES: Dict[str, str] = {
    # General commands
    "hello": "Hello! I'm the Moringa Courses bot. Ask me about courses (e.g., 'Tell me about the Data Science Bootcamp') or type 'help' for more options.",
    
    "help": "I can answer questions about Moringa School courses. Try: 'study' to see categories, or ask about 'data science', 'devops', 'generative ai', etc.",
    
    "study": "Categories: Software Engineering, Data Science, Cyber Security, AI, High School Bootcamp. Ask e.g. 'Tell me about the Full Stack Software Engineering Bootcamp.'",
    
    # Software Engineering courses
    "introduction to software engineering": "Introduction to Software Engineering — Beginner-friendly intro to HTML, CSS, JavaScript, web design and test automation. Hands-on; in-person or online; builds a technical foundation.",
    
    "full stack software engineering bootcamp": "Full Stack Software Engineering BootCamp — Intensive, project-based program covering Python, JavaScript, Git, and real-world web app development; prepares for careers in software and AI.",
    
    "full stack": "Full Stack Software Engineering BootCamp — Intensive, project-based program covering Python, JavaScript, Git, and real-world web app development; prepares for careers in software and AI.",
    
    "fullstack": "Full Stack Software Engineering BootCamp — Intensive, project-based program covering Python, JavaScript, Git, and real-world web app development; prepares for careers in software and AI.",
    
    "fundamentals of devops engineering": "Fundamentals of DevOps Engineering — Intro to DevOps concepts, CI/CD, Azure fundamentals, infrastructure as code and hands-on practice for beginners.",
    
    "aws devops engineering bootcamp": "AWS DevOps Engineering BootCamp — Advanced DevOps with AWS: design, automate, manage cloud systems; hands-on projects; prepares for AWS DevOps certification.",
    
    "devops": "We offer DevOps courses: Fundamentals of DevOps Engineering (beginner, Azure-focused) and AWS DevOps Engineering BootCamp (advanced, AWS certification prep).",
    
    "aws": "AWS DevOps Engineering BootCamp — Advanced DevOps with AWS: design, automate, manage cloud systems; hands-on projects; prepares for AWS DevOps certification.",
    
    "azure": "Fundamentals of DevOps Engineering — Intro to DevOps concepts, CI/CD, Azure fundamentals, infrastructure as code and hands-on practice for beginners.",
    
    "software engineering": "We offer multiple Software Engineering courses: Introduction to Software Engineering (beginner), Full Stack Software Engineering BootCamp (intensive), and DevOps programs.",
    
    # Data Science courses
    "data analytics with excel and power bi": "Data Analytics with Excel and Power BI — Learn Excel, Power BI, SQL and AI tools; build dashboards and business intelligence skills; includes Power BI certification.",
    
    "power bi": "Data Analytics with Excel and Power BI — Learn Excel, Power BI, SQL and AI tools; build dashboards and business intelligence skills; includes Power BI certification.",
    
    "powerbi": "Data Analytics with Excel and Power BI — Learn Excel, Power BI, SQL and AI tools; build dashboards and business intelligence skills; includes Power BI certification.",
    
    "excel": "Data Analytics with Excel and Power BI — Learn Excel, Power BI, SQL and AI tools; build dashboards and business intelligence skills; includes Power BI certification.",
    
    "data visualization with python": "Data Visualization with Python — Intro to analyzing data and creating interactive dashboards with Python; foundation for further Data Science learning.",
    
    "introduction to data science": "Introduction to Data Science — Beginner-friendly course in Python and Google Colab for students and professionals; no prior programming required.",
    
    "data science bootcamp": "Data Science BootCamp — Comprehensive program covering advanced analytics, ML/AI, data modeling with Python; recommended background in tech/math.",
    
    "data science": "We offer several Data Science programs: Introduction to Data Science (beginner), Data Science BootCamp (advanced), Data Analytics with Excel and Power BI, and Data Visualization with Python.",
    
    "data analytics": "Data Analytics with Excel and Power BI — Learn Excel, Power BI, SQL and AI tools; build dashboards and business intelligence skills; includes Power BI certification.",
    
    "visualization": "Data Visualization with Python — Intro to analyzing data and creating interactive dashboards with Python; foundation for further Data Science learning.",
    
    "visualisation": "Data Visualization with Python — Intro to analyzing data and creating interactive dashboards with Python; foundation for further Data Science learning.",
    
    # Cyber Security courses
    "introduction to cybersecurity": "Introduction to Cybersecurity — Foundational cybersecurity + AI course: networking, cryptography, incident response, and hands-on skills; no prior experience required.",
    
    "cybersecurity bootcamp": "Cybersecurity BootCamp — In-depth, hands-on labs and capstone projects preparing students for roles like SOC Analyst, Penetration Tester, or Incident Responder.",
    
    "cybersecurity": "We offer Cybersecurity courses: Introduction to Cybersecurity (foundational, no prerequisites) and Cybersecurity BootCamp (advanced, hands-on).",
    
    "cyber security": "We offer Cybersecurity courses: Introduction to Cybersecurity (foundational, no prerequisites) and Cybersecurity BootCamp (advanced, hands-on).",
    
    "security": "We offer Cybersecurity courses: Introduction to Cybersecurity (foundational, no prerequisites) and Cybersecurity BootCamp (advanced, hands-on).",
    
    "penetration": "Cybersecurity BootCamp — In-depth, hands-on labs and capstone projects preparing students for roles like SOC Analyst, Penetration Tester, or Incident Responder.",
    
    "pen test": "Cybersecurity BootCamp — In-depth, hands-on labs and capstone projects preparing students for roles like SOC Analyst, Penetration Tester, or Incident Responder.",
    
    # AI courses
    "generative ai essentials": "Generative AI Essentials — Two-week practical program teaching how to use Gen AI tools to boost productivity across functions; non-technical friendly.",
    
    "generative ai": "Generative AI Essentials — Two-week practical program teaching how to use Gen AI tools to boost productivity across functions; non-technical friendly.",
    
    "gen ai": "Generative AI Essentials — Two-week practical program teaching how to use Gen AI tools to boost productivity across functions; non-technical friendly.",
    
    # High School courses
    "high school holiday tech bootcamp": "High School Holiday Tech BootCamp — Ages 10–17; fun, hands-on coding experience; project-based; introduces young learners to real coding and tech careers.",
    
    "high school": "High School Holiday Tech BootCamp — Ages 10–17; fun, hands-on coding experience; project-based; introduces young learners to real coding and tech careers.",
    
    "holiday bootcamp": "High School Holiday Tech BootCamp — Ages 10–17; fun, hands-on coding experience; project-based; introduces young learners to real coding and tech careers.",
    
    "youth bootcamp": "High School Holiday Tech BootCamp — Ages 10–17; fun, hands-on coding experience; project-based; introduces young learners to real coding and tech careers.",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize(text: str) -> str:
    """
    Normalize input text for matching.
    
    - Converts to lowercase
    - Removes most punctuation (keeps spaces and hyphens for multi-word phrases)
    - Strips leading/trailing whitespace
    
    Args:
        text: Raw input string
        
    Returns:
        Normalized string suitable for keyword matching
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation except spaces and hyphens (for multi-word terms)
    # This regex keeps alphanumeric, spaces, and hyphens
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    
    # Normalize whitespace (collapse multiple spaces into one)
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def find_response(user_input: str) -> Optional[str]:
    """
    Find the best matching response for user input.
    
    Matching strategy:
    1. Exact match: Check if normalized input exactly matches a response key
    2. Phrase match: Check if any response key (as a phrase) appears in input
    3. Token match: Check if any individual word from response keys appears in input
    
    This prioritizes exact matches and longer phrases over single-word matches.
    
    Args:
        user_input: Raw user input string
        
    Returns:
        Matched response string, or None if no match found
    """
    if not user_input or not user_input.strip():
        return None
    
    normalized_input = normalize(user_input)
    
    # Strategy 1: Exact match
    if normalized_input in RESPONSES:
        return RESPONSES[normalized_input]
    
    # Strategy 2: Phrase match - check if any key phrase appears in the input
    # Sort keys by length (descending) to prefer longer, more specific matches
    sorted_keys = sorted(RESPONSES.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        # Check if the key phrase appears as a substring in the input
        # Use word boundaries to avoid false matches (e.g., "data" shouldn't match "update")
        # But be flexible with hyphens and spaces
        key_pattern = key.replace('-', r'[\s\-]')  # Allow space or hyphen
        if re.search(r'\b' + key_pattern + r'\b', normalized_input):
            return RESPONSES[key]
    
    # Strategy 3: Token match - check individual significant words
    # This is a fallback for very general queries
    input_tokens = set(normalized_input.split())
    
    # Filter out very common words that shouldn't trigger matches alone
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'tell', 
                 'me', 'what', 'is', 'are', 'how', 'can', 'i', 'want', 'learn'}
    input_tokens = input_tokens - stopwords
    
    # Look for keyword matches (but only for keys that are single words or clear keywords)
    for key in sorted_keys:
        key_tokens = set(key.split())
        # If this key is a single significant word and it appears in input
        if len(key_tokens) == 1 and key_tokens.issubset(input_tokens):
            return RESPONSES[key]
    
    return None


def log_unknown(user_message: str, previous_bot_message: str) -> None:
    """
    Log an unknown query to the CSV error log.
    
    Creates the CSV file with headers if it doesn't exist.
    Appends a new row with: timestamp, previous_bot_message, user_message
    
    Args:
        user_message: The user's input that wasn't recognized
        previous_bot_message: The bot's previous response (empty string if none)
    """
    try:
        # Check if file exists to determine if we need to write headers
        file_exists = False
        try:
            with open(ERROR_LOG_CSV, 'r', newline='', encoding='utf-8') as f:
                file_exists = True
        except FileNotFoundError:
            pass
        
        # Open in append mode
        with open(ERROR_LOG_CSV, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            
            # Write header if this is a new file
            if not file_exists:
                writer.writerow(['timestamp', 'previous_bot_message', 'user_message'])
            
            # Write the error log entry
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            writer.writerow([timestamp, previous_bot_message, user_message])
            
    except Exception as e:
        # If logging fails, print warning to stderr but don't crash
        print(f"Warning: Failed to log unknown query: {e}", file=sys.stderr)


def repl_loop() -> None:
    """
    Run the main Read-Eval-Print Loop (REPL) for interactive chatbot session.
    
    Continuously prompts user for input, finds matching responses, and handles
    unknown queries by logging them. Tracks previous bot message for logging context.
    
    Exit conditions:
    - User types 'quit' or 'exit'
    - EOF signal (Ctrl+D on Unix, Ctrl+Z on Windows)
    """
    print("=" * 60)
    print("Moringa School Courses Chatbot")
    print("=" * 60)
    print("Type 'hello' to start, 'help' for assistance, or 'quit' to exit.")
    print()
    
    previous_bot_message = ""  # Track last bot response for error logging
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit']:
                print("Bot: Goodbye! Happy learning!")
                break
            
            # Find appropriate response
            response = find_response(user_input)
            
            if response:
                # Known query - respond directly
                print(f"Bot: {response}")
                previous_bot_message = response
            else:
                # Unknown query - log it and respond with default message
                log_unknown(user_input, previous_bot_message)
                print(f"Bot: {UNKNOWN_RESPONSE}")
                previous_bot_message = UNKNOWN_RESPONSE
            
            print()  # Blank line for readability
            
        except EOFError:
            # Handle Ctrl+D (Unix) or Ctrl+Z (Windows)
            print("\nBot: Goodbye! Happy learning!")
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\nBot: Goodbye! Happy learning!")
            break


# ============================================================================
# EXAMPLE/TEST FUNCTIONS
# ============================================================================

def run_example_session() -> None:
    """
    Run a simulated example session to demonstrate bot functionality.
    
    This is not a formal unit test, but provides examples of expected behavior
    for various types of queries.
    """
    print("=" * 60)
    print("EXAMPLE SESSION (Simulated)")
    print("=" * 60)
    print()
    
    # Test cases: (user_input, expected_response_contains)
    test_cases = [
        ("hello", "Hello! I'm the Moringa Courses bot"),
        ("help", "I can answer questions"),
        ("study", "Categories:"),
        ("Tell me about Power BI", "Data Analytics with Excel and Power BI"),
        ("I want to learn AWS DevOps", "AWS DevOps Engineering BootCamp"),
        ("full stack bootcamp", "Full Stack Software Engineering"),
        ("cybersecurity", "Cybersecurity courses"),
        ("generative AI", "Generative AI Essentials"),
        ("high school bootcamp", "Ages 10–17"),
        ("What is quantum computing?", UNKNOWN_RESPONSE),
    ]
    
    previous_bot_message = ""
    
    for user_input, expected_keyword in test_cases:
        print(f"You: {user_input}")
        
        response = find_response(user_input)
        
        if response:
            print(f"Bot: {response}")
            previous_bot_message = response
            
            # Verify expected keyword is in response
            if expected_keyword.lower() in response.lower():
                print("✓ Response matches expected content")
            else:
                print(f"✗ Warning: Expected '{expected_keyword}' in response")
        else:
            log_unknown(user_input, previous_bot_message)
            print(f"Bot: {UNKNOWN_RESPONSE}")
            previous_bot_message = UNKNOWN_RESPONSE
            print("✓ Unknown query logged to CSV")
        
        print()
    
    print("=" * 60)
    print("Example session complete. Check errors_log.csv for logged queries.")
    print("=" * 60)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """
    Main entry point for the chatbot application.
    
    Uncomment run_example_session() to see a simulated demo,
    or run repl_loop() for interactive mode.
    """
    # Option 1: Run example session (for testing/demo)
    # run_example_session()
    
    # Option 2: Run interactive REPL (default)
    repl_loop()


if __name__ == "__main__":
    main()


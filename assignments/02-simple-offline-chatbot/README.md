# 🤖 Project: Simple Offline Chatbot

---

### 🎯 **Description**

Goal: Build a small chatbot that responds based on keywords.

```python
# Starter Code

msg = input("Say something: ").lower()

if "hello" in msg:
    print("Hello! Ready to study?")
elif "help" in msg:
    print("Sure! What topic do you need help with?")
elif "study" in msg:
    print("Let's learn something new today!")
else:
    print("I'm still learning. Try different words!")

Required Output

Keyword detection

Clear responsesmsg = input("Say something: ").lower()

if "hello" in msg:
    print("Hello! Ready to study?")
elif "help" in msg:
    print("Sure! What topic do you need help with?")
elif "study" in msg:
    print("Let's learn something new today!")
else:
    print("I'm still learning. Try different words!")

Required Output

Keyword detection

Clear responses

```

---

### 🎯 **The Prompt**

Note: I tried formatting my prompt as pseudo-XML to try giving the LLM bot a clear task definition.

```llm_prompt
<prompt>
  <meta>
    <title>Generate simple_offline_chatbot.py</title>
    <purpose>Create a single-file Python program that implements a small offline chatbot which replies with preset answers about Moringa School course offerings. The resulting file must be named <filename>simple_offline_chatbot.py</filename>.</purpose>
    <language>python</language>
    <output_format>single-file, runnable Python 3 script (no external dependencies required unless explicitly allowed)</output_format>
    <style_requirements>
      <commenting>extensive inline comments explaining design choices, functions, and edge-cases</commenting>
      <robustness>input validation, safe file handling, clear error messages, and unit-testable helper functions</robustness>
      <matching>case-insensitive substring token matching for keywords; prefer exact keyword matches first, then fallback to contains; ignore punctuation</matching>
      <logging>CSV append mode with safe quoting; create file if missing</logging>
      <defaults>unknown queries -> exact reply: "I'm still learning!"</defaults>
    </style_requirements>
  </meta>

  <task_description>
    <![CDATA[
    Build a small offline chatbot program named simple_offline_chatbot.py that:
    - Runs from the command line and accepts user messages in an interactive loop (REPL).
    - Recognizes a small set of general commands: "hello", "help", "study".
    - Recognizes subject-specific keywords derived from the dataset below and replies with short, helpful preset descriptions for each course or category.
    - If the bot cannot match the user's message to any preset response, it must reply verbatim: "I'm still learning!"
    - Whenever the bot replies "I'm still learning!" it must append a new line to an error-log CSV file with headers: timestamp,previous_bot_message,user_message.
      - timestamp: ISO 8601 UTC timestamp (e.g. 2025-11-29T12:00:00Z)
      - previous_bot_message: the last message bot sent before this reply (empty string if none)
      - user_message: the exact raw user input that triggered the unknown response
    - The matching should be robust (trim spaces, case-insensitive). Prefer exact keyword matches; allow simple plural/singular normalization.
    - The program should be easy for an operator to extend the preset responses (e.g., a dictionary at top of file).
    - Include a small test harness or example usage function (not a full test suite) demonstrating several example interactions.
    ]]>
  </task_description>

  <file_spec>
    <filename>simple_offline_chatbot.py</filename>
    <entry_point>main()</entry_point>
    <python_version>3.8+</python_version>
    <dependencies>Only Python standard library (datetime, csv, os, sys, typing, re)</dependencies>
    <csv_log>errors_log.csv (created in same directory as script)</csv_log>
  </file_spec>

  <dataset>
    <![CDATA[
    Categories and courses (use these as the source of preset responses; include short summaries pulled from the text):
    
    SOFTWARE_ENGINEERING:
      - "introduction to software engineering":
        "Beginner-friendly intro to HTML, CSS, JavaScript, web design and test automation. Hands-on; in-person or online; builds a technical foundation."
      - "full stack software engineering bootcamp":
        "Intensive, project-based program covering Python, JavaScript, Git, and real-world web app development; prepares for careers in software and AI."
      - "fundamentals of devops engineering":
        "Intro to DevOps concepts, CI/CD, Azure fundamentals, infrastructure as code and hands-on practice for beginners."
      - "aws devops engineering bootcamp":
        "Advanced DevOps with AWS: design, automate, manage cloud systems; hands-on projects; prepares for AWS DevOps certification."

    DATA_SCIENCE:
      - "data analytics with excel and power bi":
        "Learn Excel, Power BI, SQL and AI tools; build dashboards and business intelligence skills; includes Power BI certification."
      - "data visualization with python":
        "Intro to analyzing data and creating interactive dashboards with Python; foundation for further Data Science learning."
      - "introduction to data science":
        "Beginner-friendly course in Python and Google Colab for students and professionals; no prior programming required."
      - "data science bootcamp":
        "Comprehensive program covering advanced analytics, ML/AI, data modeling with Python; recommended background in tech/math."

    CYBER_SECURITY:
      - "introduction to cybersecurity":
        "Foundational cybersecurity + AI course: networking, cryptography, incident response, and hands-on skills; no prior experience required."
      - "cybersecurity bootcamp":
        "In-depth, hands-on labs and capstone projects preparing students for roles like SOC Analyst, Penetration Tester, or Incident Responder."

    AI:
      - "generative ai essentials":
        "Two-week practical program teaching how to use Gen AI tools to boost productivity across functions; non-technical friendly."

    HIGH_SCHOOL_BOOTCAMP:
      - "high school holiday tech bootcamp":
        "Ages 10–17; fun, hands-on coding experience; project-based; introduces young learners to real coding and tech careers."
    ]]>
  </dataset>

  <keywords_and_triggers>
    <![CDATA[
    Required explicit triggers the bot must recognize (case-insensitive):
      - hello  -> friendly greeting response and short usage hint
      - help   -> show available commands and how to use keywords
      - study  -> show a list of course categories and how to ask about them

    Example subject-specific trigger keywords to match content above (match if token appears anywhere in user message):
      - "software", "software engineering", "full stack", "full-stack", "fullstack"
      - "devops", "aws", "azure"
      - "data", "data science", "data analytics", "power bi", "powerbi", "excel", "visualization", "visualisation"
      - "cyber", "cybersecurity", "security", "pen test", "penetration"
      - "generative", "gen ai", "generative ai"
      - "high school", "holiday bootcamp", "youth bootcamp"
    ]]>
  </keywords_and_triggers>

  <response_spec>
    <unknown_response>"I'm still learning!"</unknown_response>
    <logging_action>
      <![CDATA[
      On unknown_response:
        1) Write (append) a CSV row to errors_log.csv (create with headers if not present).
        2) CSV columns: timestamp (UTC ISO8601), previous_bot_message, user_message
        3) Use safe CSV quoting. Handle concurrent runs gracefully by opening file in append mode with newline='' and using csv.writer.
      ]]>
    </logging_action>
    <response_examples>
      <![CDATA[
      - User: "hello"
        Bot: "Hello! I'm the Moringa Courses bot. Ask me about courses (e.g., 'Tell me about the Data Science Bootcamp') or type 'help' for more options."

      - User: "help"
        Bot: "I can answer questions about Moringa School courses. Try: 'study' to see categories, or ask about 'data science', 'devops', 'generative ai', etc."

      - User: "study"
        Bot: "Categories: Software Engineering, Data Science, Cyber Security, AI, High School Bootcamp. Ask e.g. 'Tell me about the Full Stack Software Engineering Bootcamp.'"

      - User: "Tell me about Power BI"
        Bot: "Data Analytics with Excel and Power BI — Master Excel, Power BI, SQL and AI tools for data analysis; includes Power BI certification and dashboard storytelling skills."

      - User: "I want to learn AWS DevOps"
        Bot: "AWS DevOps Engineering BootCamp — Learn to design, automate and manage cloud systems on AWS with hands-on projects; prepares you for AWS DevOps roles and certification."

      - User: "What is quantum computing?"
        Bot: "I'm still learning!"
        (append a CSV row with timestamp, previous bot message, and "What is quantum computing?")
      ]]>
    </response_examples>
  </response_spec>

  <implementation_guidelines>
    <![CDATA[
    - Data structure: place all preset responses in a single top-of-file dictionary mapping normalized keyword -> short response. Also include a category mapping so "study" can list categories.
    - Matching function: implement normalize(text) -> lowercase, strip punctuation (basic), tokenizes; matching should check for exact phrase keys first, then individual keyword tokens.
    - REPL loop:
      - print a simple prompt (e.g., "You: "), read input, exit on EOF or commands like "quit"/"exit".
      - on each iteration: determine reply, print reply, and update previous_bot_message variable.
    - CSV logging:
      - Filename constant at top (ERROR_LOG_CSV = "errors_log.csv")
      - On first creation, write header row.
      - Use csv module with newline='' to avoid blank lines on Windows.
    - Concurrency/safety: handle file exceptions; if logging fails, print a warning to stderr but continue execution.
    - Tests/example usage:
      - Provide a function `run_example_session()` that simulates a few inputs and prints the outputs (not required to be a formal test framework).
    - Code clarity:
      - split functionality into small functions: normalize(), find_response(), log_unknown(), repl_loop(), main().
      - include docstrings for each function and module-level header explaining purpose and usage.
    ]]>
  </implementation_guidelines>

  <constraints_and_edge_cases>
    <![CDATA[
    - Must not require an internet connection.
    - Keep responses concise (1-3 sentences).
    - Be defensive: handle empty input, whitespace-only input, extremely long input.
    - When previous_bot_message is undefined (first reply), log an empty string for that field.
    - The bot must be easy to extend: include clear comment where to add new courses/responses.
    ]]>
  </constraints_and_edge_cases>

  <deliverables>
    <code_file>simple_offline_chatbot.py (single file)</code_file>
    <readme_snippet>short header comments at top of the file describing how to run: `python simple_offline_chatbot.py` and how to exit the REPL</readme_snippet>
    <example_session>embedded in file as a runnable if __name__ == "__main__": main()</example_session>
  </deliverables>

</prompt>

```

---

### 🔗 Reference: Generated implementation

I used [Gemini](https://gemini.google.com/app) and [ClaudeAI](https://claude.ai/) to prompt and generate the code. You can view the generated implementation of the program hema function here:

[@ekiara/moringaschool-ai-foundations-2025/#TODO](#TODO)

This file contains the full Python implementation produced from the prompts and can be used as a reference or dropped into your project for testing.

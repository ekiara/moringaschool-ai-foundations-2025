# Beginners Toolkit with GenAI

## Learning Rust

### Overview

This document covers how I started learning Rust programming fundamentals by using AI Large Language Models (LLMs) and Generative AI tools. As a beginner to Rust, I used these tools to help my understanding of core concepts and build a functional program.

### Motivation

Rust is known for its steep learning curve, particularly around concepts like ownership, borrowing, and lifetimes. Traditional learning methods often require extensive reading of documentation and trial-and-error debugging. By incorporating AI assistants into my learning process, I aimed to:

- Get immediate explanations of complex concepts
- Receive real-time feedback on code quality and best practices
- Quickly troubleshoot errors and understand compiler messages
- Generate working code examples to learn from

### Learning Approach

#### Self-made Curriculum

I decided on using LLMs to begin learning Rust. I primarily write software in Python and Typescript, and occasionally do Golang and C# work as well, but since I had never touched Rust I decided on trying to learn it.
From what I have read, Rust is a very difficult language to effectively write software in so I decided to choose a very basic application to rewrite and focus on learning the basics of the language, as well as hopefully some useful patterns as well as things like testing, logs, network connections, and maybe even working with databases.
For the project I decided just to rewrite the assignment we had done earlier (a text/terminal chat bot) and maybe try to do some enhancements on features for that application when I implemented in Rust.
From Googling Rust language fundamentals I wrote up a step-by-step plan on what I wanted to learn:

* Setup a Rust dev environment and do "Hello, World!"
* Learn about Variables and Mutability
* Learn the Basic Data Types
* Learn how to write Functions and doing Control Flow
* Learn the Rust "Ownership" system
* Try to understand References and Borrowing
* Learn about Structs
* Learn how to define Eunums
* Learn about Pattern Matching
* Error Handling
* Learn the Rust Module System and structuring Code
* Learn How to do Logging
* Learn How to write tests
* Learn How to connect to sqlite3 database
* Learn how to connect to a remote PostgreSQL database
* Learn How to build a .EXE file with Rust on my Linux machine (and get it working on Windows)
* Learn How to build a windows service on my Linux machine (and get it working on Windows)

#### Interactive Learning

Rather than passively reading tutorials, I engaged in active dialogue with AI assistants. I would ask questions about specific Rust concepts, request clarifications when confused, and explore different approaches to solving problems. This conversational learning style allowed me to build understanding incrementally and at my own pace.

#### Concept Exploration

I used AI tools to break down intimidating Rust concepts into digestible explanations. Topics covered included:

- Rust's ownership system and memory management
- Borrowing rules and references
- Pattern matching and error handling
- Traits and generics
- Cargo package manager basics

#### Code Generation and Analysis

AI assistants helped me understand Rust syntax by generating example code snippets. I would then modify these examples, observe the results, and ask follow-up questions about why certain approaches worked or failed. This hands-on experimentation was crucial to internalizing Rust's unique paradigms.

#### Debugging Support

When encountering compiler errors (which in Rust can be verbose and intimidating for beginners), I would share the error messages with AI tools to get plain-language explanations and suggested fixes. This dramatically reduced the frustration typically associated with learning a systems programming language.

### The Project

Using the knowledge gained through AI-assisted learning, I successfully built a working Rust program. The development process involved:

1. **Planning**: Discussing program architecture and design patterns with AI
2. **Implementation**: Writing code with AI suggestions for best practices
3. **Testing**: Debugging with AI assistance when issues arose
4. **Refinement**: Improving code quality based on AI recommendations

#### Project Features

The original version of the chatbot (written in Python) was basic and very linear. I added the following features:

- Simulating a IM chat interface using the Rust ratatui crate
- Allowing the bot to choose a "mood" () and giving alternative versions of the same response based on that "mood"
- The preset responses were all stored in a JSON object in a separate file
- A chat transcript of the chat session is generated at the end of the chat
- I avoided trying to do network requests, or connecting to a database given the time that I had available

#### Implemention Failures

I wanted to also learn testing (i.e. unit tests) but did not have time to properly learn and implement it. ClaudeAI produced a seemingly working test setup but since I didn't understand it well enough to write my own tests yet, I did not include  that in the project.

I also wanted to learn logging but didn't have time to get into that.

### Key Takeaways

#### Accelerated Learning Curve

What might have taken weeks of independent study was compressed into a much shorter timeframe. The ability to get instant answers to specific questions eliminated much of the friction from the learning process.

#### Practical Understanding

By building a real project alongside theoretical learning, I developed practical skills rather than just memorizing syntax. The AI tools helped bridge the gap between concept and implementation.

#### Best Practices from Day One

AI assistants provided guidance on idiomatic Rust code and common pitfalls, helping me develop good habits early rather than learning bad patterns that would need to be unlearned later.

#### Confidence Building

Having an AI assistant available as a safety net made me more willing to experiment and try challenging features. This experimentation was essential to deepening my understanding.

### Challenges and Limitations

While AI tools were invaluable, they weren't perfect:

- Occasionally provided outdated information about Rust features or crate versions
- Sometimes generated code that compiled but wasn't idiomatic Rust
- Required critical thinking to evaluate whether suggestions aligned with best practices
- Still needed to consult official documentation for definitive information

### Recommendations for Others

If you're interested in using GenAI to learn Rust (or any programming language):

1. **Ask specific questions**: The more precise your questions, the better the responses
2. **Experiment actively**: Don't just copy code; modify it and see what breaks
3. **Verify important information**: Cross-reference AI suggestions with official docs
4. **Build something real**: Apply your learning to an actual project
5. **Iterate continuously**: Use AI throughout your project, not just at the beginning

### Conclusion

Generative AI has fundamentally changed how beginners can approach learning complex programming languages like Rust. By providing personalized, interactive instruction and immediate feedback, these tools make previously intimidating subjects accessible to newcomers. While they don't replace traditional learning resources, they serve as powerful complements that can significantly accelerate the journey from beginner to competent programmer.

The combination of AI assistance and hands-on project work created an effective learning environment that balanced theory with practice, ultimately enabling me to understand Rust fundamentals and write working code with confidence.

---

**Tools Used**: Claude, ChatGPT, Gemini, Google, and other LLM-based coding assistants

**Project Repository**: https://github.com/ekiara/moringaschool-ai-foundations-2025/tree/main/assignments/03-final-project


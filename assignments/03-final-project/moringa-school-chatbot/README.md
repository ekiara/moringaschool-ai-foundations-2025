# 🦀 **Moringa School Chatbot**

---

### 📝 **Description**

This is a simple, terminal-based chatbot application implemented in Rust. It utilizes the `ratatui` and `crossterm` libraries to create an interactive command-line interface (CLI). The chatbot's conversation flow is defined by an external JSON file, allowing for easy configuration of dialogue, response styles, and conversation paths.

### ✨ **Features**

* **Terminal User Interface (TUI):** Interactive chat interface built with `ratatui`.
* **Conversation Flow:** Dialogue logic is managed via a configurable `conversation_flow.json` file.
* **Style-Based Responses:** Bot responses can vary based on a randomly selected conversational style (e.g., 'formal', 'casual', 'humorous').
* **Typing Animation:** Bot messages are displayed with a realistic, character-by-character typing effect.
* **Transcript Logging:** All user and bot messages are logged to a timestamped file (e.g., `chat-YYYYMMDD-HHMM.log`).
* **Asynchronous Input Handling:** Uses `crossterm` for non-blocking input and redraws.

---

### 🚀 **Prerequisites**

To build and run this application, you need:

* **Rust and Cargo:** Ensure you have the Rust toolchain installed. You can install it via [rustup](https://rustup.rs/).

```bash
rustc --version
cargo --version
```

### ⚙️ Installation and Setup

#### 1. Clone the repository

```bash
git clone <repository_url>
cd <repository_directory>
```

#### 2. Notes on the `conversation_flow.json`

Ensure `conversation_flow.json` Exists: The application requires a file named `conversation_flow.json` in the root directory. This file defines the chatbot's dialogue structure using the specified Node format, which includes id, type, style-based message mappings, options, and a next_node.

The conversation must start with a node having the ID "start".

### 🏃 How to Run

Compile and run the application using Cargo. The application will automatically set up the TUI environment.

```bash
cargo run
```

### ⌨️ Usage

Once the application starts, it will enter raw terminal mode and display the chat interface.


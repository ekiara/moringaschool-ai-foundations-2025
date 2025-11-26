#![allow(warnings)]
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, Write};
use std::time::{Duration, Instant};
use chrono::{Local, DateTime};
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Wrap},
    Frame, Terminal,
};
use serde::Deserialize;
use rand::{seq::SliceRandom, thread_rng};

#[derive(Debug, Deserialize)]
struct Node {
    id: String,
    #[serde(rename = "type")]
    node_type: String,
    message: HashMap<String, String>,
    #[serde(default)]
    options: HashMap<String, String>,
    next_node: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ConversationFlow {
    nodes: HashMap<String, Node>,
}

#[derive(Clone)]
struct ChatMessage {
    text: String,
    is_bot: bool,
    displayed_chars: usize, // Number of characters currently displayed
    last_char_time: Option<Instant>, // Time when last character was displayed
    complete: bool, // Whether the message is fully displayed
}

impl ChatMessage {
    fn new(text: String, is_bot: bool) -> Self {
        ChatMessage {
            text,
            is_bot,
            displayed_chars: 0,
            last_char_time: None,
            complete: false,
        }
    }

    fn update_typing(&mut self) -> bool {
        if self.complete {
            return false;
        }

        let now = Instant::now();
        let should_add_char = match self.last_char_time {
            None => true,
            Some(last_time) => {
                let elapsed = now.duration_since(last_time);
                // Check if we just added a space (word boundary)
                if self.displayed_chars > 0 {
                    let last_char = self.text.chars().nth(self.displayed_chars - 1);
                    if last_char == Some(' ') {
                        elapsed >= Duration::from_millis(45)
                    } else {
                        elapsed >= Duration::from_millis(5)
                    }
                } else {
                    elapsed >= Duration::from_millis(5)
                }
            }
        };

        if should_add_char && self.displayed_chars < self.text.chars().count() {
            self.displayed_chars += 1;
            self.last_char_time = Some(now);
            
            if self.displayed_chars >= self.text.chars().count() {
                self.complete = true;
            }
            
            true
        } else {
            false
        }
    }

    fn get_displayed_text(&self) -> String {
        self.text.chars().take(self.displayed_chars).collect()
    }
}

struct App {
    messages: Vec<ChatMessage>,
    input: String,
    scroll_offset: usize,
    auto_scroll: bool, // Auto-scroll to bottom when new messages arrive
    transcript_file: File, // File handle for logging
}

impl App {
    fn new(transcript_file: File) -> App {
        App {
            messages: Vec::new(),
            input: String::new(),
            scroll_offset: 0,
            auto_scroll: true,
            transcript_file,
        }
    }

    fn add_message(&mut self, text: String, is_bot: bool) {
        self.messages.push(ChatMessage::new(text.clone(), is_bot));
        // Enable auto-scroll when new message is added
        self.auto_scroll = true;
        
        // Log to transcript
        self.log_message(&text, is_bot);
    }
    
    fn log_message(&mut self, text: &str, is_bot: bool) {
        let now: DateTime<Local> = Local::now();
        let timestamp = now.format("%H:%M");
        let sender = if is_bot { "Bot" } else { "User" };
        
        let log_line = format!("{} <{}>: {}\n", timestamp, sender, text);
        let _ = self.transcript_file.write_all(log_line.as_bytes());
        let _ = self.transcript_file.flush();
    }

    fn scroll_down(&mut self) {
        if self.scroll_offset > 0 {
            self.scroll_offset -= 1;
        }
        // Disable auto-scroll when user manually scrolls
        self.auto_scroll = false;
    }

    fn scroll_up(&mut self, max_messages: usize) {
        if self.messages.len() > max_messages {
            if self.scroll_offset < self.messages.len() - max_messages {
                self.scroll_offset += 1;
            }
        }
        // Disable auto-scroll when user manually scrolls
        self.auto_scroll = false;
    }

    fn update_scroll(&mut self, visible_area_height: u16) {
        if !self.auto_scroll {
            return;
        }
        
        // Calculate total height needed for all messages
        let mut total_height = 0;
        for msg in &self.messages {
            let display_text = msg.get_displayed_text();
            let max_width = 70; // Approximate
            let wrapped_lines = wrap_text(&display_text, max_width);
            total_height += wrapped_lines.len() + 3; // +3 for borders and spacing
        }
        
        // If content exceeds visible area, scroll to show latest messages
        if total_height > visible_area_height as usize {
            let excess = total_height - visible_area_height as usize;
            self.scroll_offset = (excess / 4).max(0); // Adjust scroll offset
        }
    }
}

fn run_app<B: ratatui::backend::Backend>(
    terminal: &mut Terminal<B>,
    mut app: App,
    flow: &ConversationFlow,
) -> io::Result<()> {
    // Define all available styles
    const STYLES: [&str; 9] = [
        "base", "formal", "casual", "humorous", "inquisitive",
        "narrative", "concise", "encouraging", "playful"
    ];

    // Select a style randomly at the start of the conversation
    let mut rng = thread_rng();
    let selected_style = STYLES.choose(&mut rng).unwrap();

    let mut current_node_id = "start".to_string();
    let mut waiting_for_input = false;
    let mut conversation_ended = false;

    loop {
        // Process current node if not waiting for input
        if !waiting_for_input && !conversation_ended {
            let node = match flow.nodes.get(&current_node_id) {
                Some(n) => n,
                None => {
                    app.add_message(
                        format!("ERROR: Invalid node ID '{}' found. Exiting.", current_node_id),
                        true,
                    );
                    conversation_ended = true;
                    waiting_for_input = true;
                    terminal.draw(|f| ui(f, &app))?;
                    continue;
                }
            };

            // Get the message corresponding to the selected style
            let message_text = node.message.get(*selected_style)
                .map(|s| s.as_str())
                .unwrap_or("I apologize, but I seem to have encountered a conversational glitch.");

            app.add_message(message_text.to_string(), true);

            // Check for the end of the conversation
            if node.node_type == "end" {
                conversation_ended = true;
            }

            waiting_for_input = true;
        }

        terminal.draw(|f| ui(f, &app))?;

        // Update typing animation for bot messages
        let mut needs_redraw = false;
        for msg in app.messages.iter_mut() {
            if msg.is_bot && !msg.complete {
                if msg.update_typing() {
                    needs_redraw = true;
                }
            }
        }

        // Check if we're waiting for typing to complete
        let typing_in_progress = app.messages.iter().any(|msg| msg.is_bot && !msg.complete);

        // Handle input
        if event::poll(Duration::from_millis(10))? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Char(c) => {
                        if !conversation_ended {
                            app.input.push(c);
                        }
                    }
                    KeyCode::Backspace => {
                        if !conversation_ended {
                            app.input.pop();
                        }
                    }
                    KeyCode::Enter => {
                        if conversation_ended {
                            break;
                        }
                        // Don't allow input while bot is typing
                        if typing_in_progress {
                            continue;
                        }
                        if !app.input.is_empty() {
                            let user_input = app.input.trim().to_lowercase();
                            let user_message = app.input.clone();
                            app.input.clear();
                            
                            // Add user message and mark it as complete immediately
                            let mut user_msg = ChatMessage::new(user_message.clone(), false);
                            user_msg.complete = true;
                            user_msg.displayed_chars = user_msg.text.chars().count();
                            app.messages.push(user_msg);
                            
                            // Log user message to transcript
                            app.log_message(&user_message, false);

                            // Process the input
                            let node = flow.nodes.get(&current_node_id).unwrap();
                            
                            const EXIT_COMMANDS: [&str; 4] = ["no", "bye", "quit", "exit"];

                            let next_id = node.options.iter()
                                .find_map(|(key, next_node_id)| {
                                    if user_input.starts_with(key.to_lowercase().as_str()) {
                                        Some(next_node_id.clone())
                                    } else {
                                        None
                                    }
                                });

                            if next_id.is_none() && EXIT_COMMANDS.iter().any(|&cmd| cmd == user_input) {
                                current_node_id = "exit_conversation".to_string();
                                waiting_for_input = false;
                            } else if let Some(id) = next_id {
                                current_node_id = id;
                                waiting_for_input = false;
                            } else if node.next_node.is_some() {
                                current_node_id = node.next_node.as_ref().unwrap().clone();
                                waiting_for_input = false;
                            } else {
                                let available_options: Vec<&String> = node.options.keys().collect();
                                let options_list = match available_options.len() {
                                    0 => String::from("No options available."),
                                    1 => format!("'{}'", available_options[0]),
                                    _ => {
                                        let last_index = available_options.len() - 1;
                                        let initial_part = available_options[0..last_index]
                                            .iter()
                                            .map(|k| format!("'{}'", k))
                                            .collect::<Vec<String>>()
                                            .join(", ");
                                        format!("{} or '{}'", initial_part, available_options[last_index])
                                    }
                                };
                                app.add_message(
                                    format!("I'm sorry, I didn't understand that. Please choose from: {}", options_list),
                                    true,
                                );
                            }
                        }
                    }
                    KeyCode::Esc => {
                        break;
                    }
                    KeyCode::Up => {
                        app.scroll_up(10);
                    }
                    KeyCode::Down => {
                        app.scroll_down();
                    }
                    _ => {}
                }
            }
        }
    }

    Ok(())
}

fn ui(f: &mut Frame, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Min(3), Constraint::Length(3)])
        .split(f.area());

    // Main chat area
    let chat_block = Block::default()
        .borders(Borders::ALL)
        .title("Chat with Bot");

    let inner_area = chat_block.inner(chunks[0]);
    f.render_widget(chat_block, chunks[0]);

    // Render messages with proper scrolling
    let mut y_offset = 0;
    let mut total_height = 0;
    
    // First pass: calculate total height
    for (i, msg) in app.messages.iter().enumerate() {
        let display_text = msg.get_displayed_text();
        let max_width = (inner_area.width as usize).saturating_sub(10);
        let wrapped_lines = wrap_text(&display_text, max_width);
        let msg_height = wrapped_lines.len() as u16;
        
        // Add gap if switching between user and bot
        if i > 0 {
            let prev_is_bot = app.messages[i - 1].is_bot;
            if prev_is_bot != msg.is_bot {
                total_height += 1; // Add gap
            }
        }
        
        total_height += msg_height;
    }
    
    // Calculate starting offset to show latest messages at bottom
    // If we're within 3 lines of the bottom, scroll up to keep showing new content
    let buffer_lines = 3;
    let start_offset = if total_height > inner_area.height {
        let base_offset = total_height - inner_area.height;
        // Add extra scroll if we're close to the bottom
        if total_height > inner_area.height && (total_height - base_offset) <= inner_area.height {
            base_offset + buffer_lines.min(base_offset)
        } else {
            base_offset
        }
    } else {
        0
    };
    
    let mut current_height = 0;
    for (i, msg) in app.messages.iter().enumerate() {
        let display_text = msg.get_displayed_text();
        let max_width = (inner_area.width as usize).saturating_sub(10);
        let wrapped_lines = wrap_text(&display_text, max_width);
        let msg_height = wrapped_lines.len() as u16;
        
        // Calculate gap
        let gap = if i > 0 {
            let prev_is_bot = app.messages[i - 1].is_bot;
            if prev_is_bot != msg.is_bot { 1 } else { 0 }
        } else {
            0
        };
        
        let total_msg_height = msg_height + gap;
        
        // Skip messages that are scrolled out of view
        if current_height + total_msg_height <= start_offset {
            current_height += total_msg_height;
            continue;
        }
        
        // Adjust y_offset if message is partially scrolled
        let visible_start = if current_height < start_offset {
            start_offset - current_height
        } else {
            0
        };
        
        if y_offset >= inner_area.height {
            break;
        }
        
        let prev_is_bot = if i > 0 { Some(app.messages[i - 1].is_bot) } else { None };
        let rendered_height = render_message(f, inner_area, msg, y_offset.saturating_sub(visible_start), prev_is_bot);
        y_offset += rendered_height;
        current_height += total_msg_height;
    }

    // Input area
    let input_block = Block::default()
        .borders(Borders::ALL)
        .title("Your message (Press Enter to send, Esc to quit)");

    let input_text = Paragraph::new(app.input.as_str())
        .block(input_block)
        .wrap(Wrap { trim: true });

    f.render_widget(input_text, chunks[1]);
}

fn render_message(f: &mut Frame, area: Rect, msg: &ChatMessage, y_offset: u16, prev_msg_is_bot: Option<bool>) -> u16 {
    // Get the displayed text (which may be partial if still typing)
    let display_text = msg.get_displayed_text();
    
    // Add vertical gap if switching between user and bot
    let gap = if let Some(was_bot) = prev_msg_is_bot {
        if was_bot != msg.is_bot { 1 } else { 0 }
    } else {
        0
    };
    
    let actual_y_offset = y_offset + gap;
    
    // Calculate message dimensions
    let max_width = (area.width as usize).saturating_sub(10);
    let wrapped_lines = wrap_text(&display_text, max_width);
    let msg_height = wrapped_lines.len() as u16; // No extra space for borders

    if actual_y_offset + msg_height > area.height {
        return gap;
    }

    // Position the message box
    let msg_width = max_width.min(display_text.len() + 4) as u16;
    let x_pos = if msg.is_bot {
        area.x + 2 // Bot messages on the left
    } else {
        area.x + area.width - msg_width - 2 // User messages on the right
    };

    let msg_area = Rect {
        x: x_pos,
        y: area.y + actual_y_offset,
        width: msg_width,
        height: msg_height,
    };

    // Choose color based on sender
    let bg_color = if msg.is_bot {
        Color::Indexed(93) // Purple
    } else {
        Color::Indexed(33) // Blue
    };

    // Create the message box without borders - just colored background
    let mut lines = Vec::new();

    for line in wrapped_lines {
        lines.push(Line::from(vec![
            Span::styled(
                format!(" {} ", line),
                Style::default().bg(bg_color).fg(Color::White)
            ),
        ]));
    }

    let msg_paragraph = Paragraph::new(lines)
        .alignment(Alignment::Left);

    f.render_widget(msg_paragraph, msg_area);

    msg_height + gap // Return total height including gap
}

fn wrap_text(text: &str, max_width: usize) -> Vec<String> {
    let mut lines = Vec::new();
    let mut current_line = String::new();

    for word in text.split_whitespace() {
        if current_line.len() + word.len() + 1 > max_width {
            if !current_line.is_empty() {
                lines.push(current_line.trim().to_string());
                current_line = String::new();
            }
        }
        if !current_line.is_empty() {
            current_line.push(' ');
        }
        current_line.push_str(word);
    }

    if !current_line.is_empty() {
        lines.push(current_line.trim().to_string());
    }

    if lines.is_empty() {
        lines.push(String::new());
    }

    lines
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Read and parse JSON
    const FILE_PATH: &str = "conversation_flow.json";
    let json_content = fs::read_to_string(FILE_PATH)?;
    let flow: ConversationFlow = serde_json::from_str(&json_content)?;

    // Create transcript file with timestamp in filename
    let now: DateTime<Local> = Local::now();
    let filename = now.format("chat-%Y%m%d-%H%M.log").to_string();
    let transcript_file = File::create(&filename)?;

    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app and run
    let app = App::new(transcript_file);
    let res = run_app(&mut terminal, app, &flow);

    // Restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        println!("Error: {:?}", err);
    }

    Ok(())
}

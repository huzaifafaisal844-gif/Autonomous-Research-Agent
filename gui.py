import os
import sys
import threading
from dotenv import load_dotenv
import customtkinter as ctk

from src.agent import Agent
from src.tools import TOOLS
from src.memory import VectorMemory
from src.prompts import AGENT_SYSTEM_PROMPT

# Configure CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AgentGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Autonomous Research Agent")
        self.geometry("1100x700")

        # --- Layout Configuration ---
        self.grid_columnconfigure(0, weight=3) # Main chat area gets more space
        self.grid_columnconfigure(1, weight=2) # Agent thoughts panel
        self.grid_rowconfigure(0, weight=1)    # Text areas expand
        self.grid_rowconfigure(1, weight=0)    # Input area fixed height

        # --- Main Chat Area ---
        self.chat_box = ctk.CTkTextbox(self, font=("Segoe UI", 15), wrap="word")
        self.chat_box.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew")
        self.chat_box.insert("0.0", "Welcome to the Autonomous Research Agent!\n\n")
        self.chat_box.configure(state="disabled")

        # --- Agent Thoughts Log ---
        # Using a monospaced font to clearly see tool outputs
        self.thought_log = ctk.CTkTextbox(self, font=("Consolas", 12), fg_color="#1E1E1E", text_color="#A9B7C6", wrap="word")
        self.thought_log.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), sticky="nsew")
        self.thought_log.insert("0.0", "Initializing System...\n")
        self.thought_log.configure(state="disabled")

        # --- Input Area ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="What would you like me to research?", height=45)
        self.input_entry.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ew")
        
        # Bind the Enter key to send
        self.input_entry.bind("<Return>", lambda event: self.start_agent())

        self.send_button = ctk.CTkButton(self.input_frame, text="Send Agent", command=self.start_agent, width=120, height=45)
        self.send_button.grid(row=0, column=1, padx=(0, 10), pady=10)

        # Initialize environment and Agent
        self.init_agent()

    def append_to_chat(self, text):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text + "\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def append_to_log(self, text):
        self.thought_log.configure(state="normal")
        self.thought_log.insert("end", text + "\n")
        self.thought_log.see("end")
        self.thought_log.configure(state="disabled")

    def init_agent(self):
        load_dotenv()
        if not os.environ.get("GEMINI_API_KEY"):
            self.append_to_chat("Error: GEMINI_API_KEY environment variable not found. Please create a .env file.")
            return

        self.append_to_log("Status: Initializing Vector Memory...")
        try:
            self.memory = VectorMemory()
            self.append_to_log("Status: Vector Memory Initialized.")
        except Exception as e:
            self.append_to_log(f"Warning: Could not initialize ChromaDB ({e}). Running without memory.")
            self.memory = None

        self.agent = Agent(
            name="ResearchAgent",
            system_prompt=AGENT_SYSTEM_PROMPT,
            tools=TOOLS,
            memory_module=self.memory
        )
        self.append_to_log("Status: Agent Initialized and Ready.\n")

    def on_step_callback(self, step_type, content):
        """Callback passed to the Agent to catch Thoughts, Actions, and Observations."""
        # Clean up output formatting stripped from the rich CLI version
        if step_type == "thought":
            formatted = f"\n🧠 Thought: {content.replace('Thought: ', '').strip()}"
        elif step_type == "action":
            formatted = f"🛠️ Action: {content}"
        elif step_type == "observation":
            formatted = f"👀 Obs: {content.strip()}"
        else:
            formatted = f"{content}"
        
        # GUI elements Must be updated from the main thread
        self.after(0, self.append_to_log, formatted)

    def start_agent(self, event=None):
        task = self.input_entry.get().strip()
        if not task:
            return

        self.input_entry.delete(0, "end")
        self.append_to_chat(f"You: {task}\n")
        self.append_to_log(f"\n--- New Task ---\n{task}\n")

        # Disable buttons to prevent duplicate runs
        self.send_button.configure(state="disabled", text="Thinking...")
        self.input_entry.configure(state="disabled")

        # Run the agent in a separate Daemon thread so the GUI does not freeze
        threading.Thread(target=self.run_agent_thread, args=(task,), daemon=True).start()

    def run_agent_thread(self, task):
        try:
            # This is a blocking call, running in the thread
            final_answer = self.agent.run(task=task, on_step=self.on_step_callback)
            
            # Post the final answer back to the main thread securely
            self.after(0, self.finish_agent, final_answer)
        except Exception as e:
            self.after(0, self.finish_agent, f"Error running agent: {e}")

    def finish_agent(self, final_answer):
        self.append_to_chat(f"Agent:\n{final_answer}\n")
        self.append_to_log("\nStatus: Task Complete.")
        
        # Re-enable inputs
        self.send_button.configure(state="normal", text="Send Agent")
        self.input_entry.configure(state="normal")
        self.input_entry.focus()

if __name__ == "__main__":
    app = AgentGUI()
    app.mainloop()

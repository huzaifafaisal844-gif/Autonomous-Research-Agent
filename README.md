# Autonomous Research Agent 🤖

> An autonomous, multi-step reasoning AI agent built from scratch in Python that dynamically searches the web, solves problems, and remembers context across sessions.

Building AI applications has moved beyond simple wrappers and into the era of **Agents**. This project is a complete, custom implementation of the **ReAct (Reason + Act)** framework. Built from the ground up without heavy abstractions like LangChain, this agent "thinks out loud," selects tools, processes raw observation data, and recursively acts until it finds a final answer.

---

## 🌟 Key Features

*   **Native Desktop GUI (NEW):** A smooth, multithreaded `CustomTkinter` desktop application that visualizes the agent's Thought/Action loop in real-time.
*   **Custom ReAct Loop:** Parses internal thoughts and commands native Python functions to execute real-world tasks.
*   **Semantic Memory:** Uses `ChromaDB` to generate embeddings from past research facts, granting the agent context across different terminal sessions.
*   **Live Web Capabilities:** Bypasses LLM knowledge cutoffs by leveraging DuckDuckGo for live internet searches and BeautifulSoup to scrape and read active webpages.
*   **Sandboxed Evaluator:** Calculates math strings locally to solve logic and arithmetic tasks without hallucinating.

## 🏗️ Architecture

1.  **`gui.py` - Desktop App:** A modern `CustomTkinter` UI that runs the agent in a background thread to prevent freezing.
2.  **`main.py` - CLI App:** Powers the beautiful `Rich` terminal interface.
3.  **`src/agent.py` - The Brain:** Houses the custom ReAct Python loop.
4.  **`src/prompts.py` - The Rules:** Defines the strictly formatted system instructions forcing the LLM to behave autonomously.
5.  **`src/memory.py` - The Hippocampus:** A wrapper around ChromaDB allowing semantic memory storage.
6.  **`src/tools.py` - The Hands:** Pure python tools (`search_web`, `read_webpage`, `calculate`).

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   A free Google Gemini API Key.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/autonomous-research-agent.git
    cd autonomous-research-agent
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up the Environment Variables:**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

### Usage

**Launch the Desktop GUI (Recommended):**
```bash
python gui.py
```
*(You can also use the Desktop Shortcut if generated)*

**Run the CLI Version:**
```bash
python main.py
```

## 🛠️ Tech Stack
*   **LLM Provider:** Google Gemini Flash (`google-genai`)
*   **GUI & CLI:** CustomTkinter (`customtkinter`), Rich (`rich`)
*   **Vector DB:** ChromaDB (`chromadb`)
*   **Web Scraping:** BeautifulSoup4, Requests
*   **Search Engine:** DuckDuckGo API

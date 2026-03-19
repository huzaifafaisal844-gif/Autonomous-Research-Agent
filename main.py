import os
import sys
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from src.agent import Agent
from src.tools import TOOLS
from src.memory import VectorMemory
from src.prompts import AGENT_SYSTEM_PROMPT

# Setup UI
console = Console()

def print_step(step_type: str, content: str):
    """Formats the agent's output beautifully in the terminal."""
    if step_type == "thought":
        console.print(f"[bold dim cyan]🧠 Thought:[/bold dim cyan] [cyan]{content.replace('Thought: ', '').strip()}[/cyan]")
    elif step_type == "action":
        console.print(f"[bold yellow]🛠️  Action:[/bold yellow] [yellow]{content}[/yellow]")
    elif step_type == "observation":
        console.print(f"[bold green]👀 Observation:[/bold green] [dim green]{content.strip()}[/dim green]")
        console.print("---")

def main():
    console.print(Panel.fit("[bold magenta]🤖 Autonomous Research Agent[/bold magenta]\n[dim]A multi-step reasoning AI with memory and tools.[/dim]", border_style="magenta"))
    
    # Load environment variables
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        console.print("[bold red]Error: GEMINI_API_KEY environment variable not found.[/bold red]")
        console.print("Please create a .env file with GEMINI_API_KEY=your_key")
        sys.exit(1)

    # Initialize Memory
    console.print("[dim]Initializing Vector Memory...[/dim]")
    try:
        memory = VectorMemory()
    except Exception as e:
        console.print(f"[red]Warning: Could not initialize ChromaDB ({e}). Running without memory.[/red]")
        memory = None

    # Initialize Agent
    agent = Agent(
        name="ResearchAgent",
        system_prompt=AGENT_SYSTEM_PROMPT,
        tools=TOOLS,
        memory_module=memory
    )

    topic = Prompt.ask("\n[bold cyan]What topic would you like me to research?[/bold cyan]")
    
    console.print(f"\n[bold green]Starting research on:[/bold green] {topic}\n")
    
    # Run Agent
    final_answer = agent.run(task=topic, on_step=print_step)
    
    # Print Final Answer
    console.print(Panel(Markdown(final_answer), title="[bold green]Final Research Report[/bold green]", border_style="green"))

if __name__ == "__main__":
    main()

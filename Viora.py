import sys
import warnings
# Suppress pywinauto COM threading warning
warnings.filterwarnings("ignore", message="Revert to STA COM threading mode")

# Set pywinauto threading mode before it's imported
try:
    import pywinauto
    pywinauto.threaded_mode = 'STA'
except:
    pass

from typing import Optional
import typer
import os
from dotenv import load_dotenv
from rich.console import Console
from agent.brain import Brain
from agent.memory import Memory
from skills.tools_factory import get_viora_tools

load_dotenv()

app = typer.Typer()
console = Console()
brain = Brain()
memory = Memory()
# tools_map still needs all tools to execute them when called
all_tools = get_viora_tools("ALL")
tools_map = {tool.name: tool for tool in all_tools}

def run_agent_loop(user_input: str, status=None):
    """Handles the execution of Viora's brain."""
    context = memory.get_relevant_context(user_input)
    return brain.run(user_input, status=status, context=context)

@app.command()
def chat(query: Optional[str] = typer.Argument(None, help="Optional query to run and exit immediately.")):
    """Start an agentic chat session with Viora. If a query is provided, it runs and exits."""
    if query:
        try:
            final_response = run_agent_loop(query)
            memory.log_interaction(query, final_response)
            console.print(f"[bold blue]Viora:[/bold blue] {final_response}")
            return
        except Exception as e:
            console.print(f"[bold red]An error occurred:[/bold red] {str(e)}")
            return

    console.print("[bold green]Viora is online. How can I help you today?[/bold green]")
    console.print("[italic]Type 'exit', 'quit', or 'bye' to quit.[/italic]")
    
    while not brain.should_exit:
        try:
            user_input = typer.prompt("You")
            user_input_lower = user_input.lower().strip()
            if user_input_lower in ["exit", "quit", "bye", "terminate", "stop"]:
                brain.should_exit = True
                break
            
            with console.status("[bold cyan]Viora is thinking...[/bold cyan]", spinner="dots") as status:
                final_response = run_agent_loop(user_input, status=status)
            
            memory.log_interaction(user_input, final_response)
            
            if final_response != "DONE":
                console.print(f"[bold blue]Viora:[/bold blue] {final_response}")
            
            # Display token usage if using Groq
            if "groq" in brain.reasoning_provider:
                usage = brain.get_token_usage()
                last = usage.get('last')
                session = usage.get('session')
                if last:
                    console.print(
                        f"[dim] Tokens: {last.get('total_tokens', 0)} "
                        f"(p: {last.get('prompt_tokens', 0)}, c: {last.get('completion_tokens', 0)}) | "
                        f"Session: {session['total']:,}[/dim]"
                    )
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred:[/bold red] {str(e)}")
            console.print("[italic]Viora recovered from the error and is ready for the next command.[/italic]")

    if brain.should_exit:
        console.print("[bold italic green]Viora is offline. Goodbye![/bold italic green]")
        import os
        os._exit(0)

@app.command()
def todo(task: str):
    """Add a todo item."""
    from skills.todo_skills import TodoSkills
    org = TodoSkills()
    msg = org.add_todo(task)
    console.print(f"[bold green]{msg}[/bold green]")

@app.command()
def todos():
    """List all pending todos."""
    from skills.todo_skills import TodoSkills
    org = TodoSkills()
    console.print(org.list_todos())

@app.command()
def open(app_name: str):
    """Open a Windows application (e.g. notepad, chrome)."""
    from skills.windows_skills import WindowsSkills
    console.print(f"[italic yellow]Opening {app_name}...[/italic yellow]")
    sys = WindowsSkills()
    msg = sys.open_application(app_name)
    console.print(f"[bold green]{msg}[/bold green]")

@app.command()
def time():
    """Get the current system time."""
    from skills.windows_skills import WindowsSkills
    sys = WindowsSkills()
    console.print(f"[bold cyan]Current Time:[/bold cyan] {sys.get_time()}")

if __name__ == "__main__":
    app()

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()

console = Console()

llm = init_chat_model(
    "gemini-3.5-flash-lite",
    model_provider="google_genai",
    temperature=0.5
)

# List directory method
def list_directory(path: str=".") -> str:
    """List all files and folders in the current directory. Fefault is current directory."""
    try:
        items = os.listdir()
        result =" "
        files = []
        folders = []

        for item in items:
            if os.path.isdir(item):
                folders.append(item)
            else:
                files.append(item)

        if folders:
            folders = "\nFolders:\n " + result + "\n".join(folders)
        if files:
            files = "\n\nFiles:\n" + result + "\n".join(files)

        return folders + files
    except Exception as e:
        return f"Error listing directories: {str(e)}"


# Write file method
def write_file(filepath: str, content: str) -> str:
    """Write content to a file. Creates new data.csv file or overwrites existing file"""
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        return f"File {filepath} created successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"


# Read file method
def read_file(filepath: str) -> str:
    """Read and return the contents of a file at the given filepath"""
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file {str(e)}"


# Create directory method
def create_directory(path: str):
    """Create a new directory at the given oath. Can create nested directories"""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"
    

system_prompt = """
You are a coding assistant that can help users navigate, read, and edit files.

You have access to four tools:
- list_directory: Show files and folders in a directory
- read_file: Read the contents of a file
- write_file: Create or edit files
- create_directory: Create new directories (including nested directories)

Be helpful and clear in your response. When editing files or creating directories, always confirm what changes you made.
"""

agent = create_agent(
    model=llm,
    tools=[list_directory, write_file, read_file, create_directory]
)

user_input = "Create me a hello world flask app in the current directory."
messages = [{
    "role": "user",
    "content": user_input
}]

chunks = agent.stream({"messages": messages}, stream_mode='updates')
for chunk in chunks:
    for step, data in chunk.items():
        if step == 'model':
            msg = data['messages'][-1]
            print("MSSG TOOL CALL", msg.tool_calls)
            if msg.tool_calls:
                tool = msg.tool_calls[0]['name']
                message = f"[bold yellow]Using tool: [/bold yellow] [cyan]{tool}[/cyan]"
                console.print(message)
            else:
                ai_message = msg.text
        elif step == 'tools':
            result = data['messages'][-1].text
            result = result if len(result) < 100 else result[:50] + "..."
            console.print(f"[bold green]Tool Result:[/bold green]\n [dim]{result}[/dim]")

markdown_output = Markdown(ai_message)
panel_output = Panel(markdown_output, title="[bold cyan]Assistant Response[/bold cyan]",
                      border_style="blue",
                      padding=(1,2)
                     )

console.print(panel_output)
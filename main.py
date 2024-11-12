import asyncio
import click
import signal
import sys
from rich.console import Console
from agent.autonomous_agent import AutonomousAgent
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
console = Console()

load_dotenv()

config = {
    'TWITTER_API_KEY': os.getenv('TWITTER_API_KEY'),
    'TWITTER_API_SECRET': os.getenv('TWITTER_API_SECRET'),
    'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
    'TWITTER_ACCESS_TOKEN': os.getenv('TWITTER_ACCESS_TOKEN'),
    'TWITTER_ACCESS_SECRET': os.getenv('TWITTER_ACCESS_SECRET'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    
    'CHECK_INTERVAL': 60,  # seconds
    'POST_INTERVAL': 3600,  # 1 hour
    'TARGET_ACCOUNTS': ['truth_terminal', 'luna_virtuals', 'dasha_terminal', 'MirraMrr', 'PraistSol']
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oracle.log'),
        logging.StreamHandler()
    ]
)

def signal_handler(sig, frame):
    console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    sys.exit(0)

# let's create a cli to chat with the ai agent, send tweets, and manage content generation
logger = logging.getLogger(__name__)

@click.command()
@click.option('--character-config', default='./config/characters/zara.yaml', help='Path to character config')
@click.option('--tasks-config', default='./config/tasks/zara.yaml', help='Path to tasks config')
def main(character_config: str, tasks_config: str):
    """Run the autonomous agent"""
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        agent = AutonomousAgent(character_config, tasks_config)
        asyncio.run(agent.start())
    except Exception as e:
        console.print(f"[bold red]Error running agent: {e}[/bold red]")
        raise

if __name__ == "__main__":
    main()

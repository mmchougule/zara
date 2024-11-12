import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from datetime import datetime
from characters.zara_character import ZaraCharacter
from agent.content_generator import ContentGenerator
from agent.task_manager import TaskManager

console = Console()

class ZaraDemo:
    def __init__(self):
        self.character = ZaraCharacter()
        self.content_generator = ContentGenerator(self.character)
        self.task_manager = TaskManager(self.character)
        self.console = Console()
        
    async def start_interactive_session(self):
        """Start interactive session with Zara"""
        self.console.print(Panel(
            f"[bold]Welcome to a conversation with {self.character.name}![/bold]\n"
            f"{''.join(self.character.bio)}\n\n"
            "Type your message or use these commands:\n"
            "/style - Get style analysis\n"
            "/trend - Get trend forecast\n"
            "/philosophy - Get fashion philosophy\n"
            "/quit - End conversation"
        ))
        
        while True:
            user_input = await self._get_user_input()
            if user_input.lower() == "/quit":
                break
                
            response = await self._process_input(user_input)
            self._display_response(response)

    async def _get_user_input(self) -> str:
        """Get user input with command handling"""
        return click.prompt("You", type=str)

    async def _process_input(self, user_input: str) -> Dict:
        """Process user input and generate appropriate response"""
        context = {
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "trends": await self._get_current_trends(),
            "type": self._determine_input_type(user_input)
        }
        
        if user_input.startswith("/"):
            return await self._handle_command(user_input, context)
        else:
            return await self._generate_conversation_response(context)

    def _display_response(self, response: Dict):
        """Display Zara's response with styling"""
        if response and 'content' in response:
            self.console.print(Panel(
                f"[bold]{self.character.name}[/bold]: {response['content']}",
                border_style="purple"
            ))

    async def _handle_command(self, command: str, context: Dict) -> Dict:
        """Handle special commands"""
        command_type = command[1:].lower()
        content_type = {
            "style": "style_analysis",
            "trend": "trend_forecast",
            "philosophy": "fashion_philosophy"
        }.get(command_type)
        
        if content_type:
            return await self.content_generator.generate_content(
                content_type, context
            )
        return {"content": "Invalid command. Try /style, /trend, or /philosophy"}

    async def _generate_conversation_response(self, context: Dict) -> Dict:
        """Generate conversational response"""
        return await self.content_generator.generate_content(
            "chat", context
        )

    async def _get_current_trends(self) -> List[str]:
        """Get current fashion and cultural trends"""
        # This would normally fetch real trends
        # For demo, returning placeholder trends
        return [
            "Sustainable Fashion",
            "Digital Wear",
            "Y2K Revival",
            "Minimalist Luxury"
        ]

    def _determine_input_type(self, input_text: str) -> str:
        """Determine the type of input for context"""
        if "?" in input_text:
            return "question"
        if "/" in input_text:
            return "command"
        return "statement"

@click.command()
def main():
    """Run the interactive Zara demo"""
    demo = ZaraDemo()
    asyncio.run(demo.start_interactive_session())

if __name__ == "__main__":
    main() 
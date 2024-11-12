from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class DisplayManager:
    def __init__(self, log_manager):
        self.console = Console()
        self.layout = Layout()
        self.log_manager = log_manager
        self.running = True
        self._create_layout()

    def _create_layout(self):
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        self.layout["left"].split(
            Layout(name="status", size=12),
            Layout(name="goals", size=12),
            Layout(name="trends", size=12)
        )
        self.layout["right"].split(
            Layout(name="activity", size=18),
            Layout(name="logs", size=18)
        )

    def _update_display(self):
        try:
            # Get recent logs
            recent_logs = list(self.log_manager.logs) #[-20:]  # Last 20 logs

            # Basic header
            self.layout["header"].update(
                Panel("Zara AI - Autonomous Agent", style="bold magenta")
            )

            # Status panel
            status = Table.grid()
            status.add_column(style="cyan")
            status.add_column(style="white")
            status.add_row("Status", "🟢 Running")
            status.add_row("Active Tasks", str(len([l for l in recent_logs if "Processing task" in l['message']])))
            self.layout["left"]["status"].update(Panel(status))

            # Goals panel
            goals = Table.grid()
            goals.add_column(style="cyan")
            goals.add_column(style="white")
            for log in recent_logs:
                if log['type'] == 'GOAL':
                    goals.add_row("Goal", log['message'])
            self.layout["left"]["goals"].update(Panel(goals))

            # Trends panel
            trends = Table.grid()
            trends.add_column(style="cyan")
            trends.add_column(style="white")
            for log in recent_logs:
                if log['type'] == 'TREND':
                    trends.add_row("Trend", log['message'])
            self.layout["left"]["trends"].update(Panel(trends))

            # Activity panel
            activity = Table.grid()
            activity.add_column(style="cyan")
            activity.add_column(style="white")
            for log in recent_logs:
                if log['type'] in ['ACTION', 'TASK']:
                    activity.add_row(
                        log['timestamp'].strftime('%H:%M:%S'),
                        log['message']
                    )
            self.layout["right"]["activity"].update(Panel(activity))

            # Logs panel
            logs_grid = Table.grid()
            logs_grid.add_column(style="cyan", width=10)
            logs_grid.add_column(style="magenta", width=10)
            logs_grid.add_column(style="white")
            for log in recent_logs:
                logs_grid.add_row(
                    log['timestamp'].strftime('%H:%M:%S'),
                    log['type'],
                    log['message']
                )
            self.layout["right"]["logs"].update(Panel(logs_grid))

            # Footer
            self.layout["footer"].update(
                Panel(f"Active since: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            )

        except Exception as e:
            logger.error(f"Display update error: {e}")
            print(f"Display error: {e}")

    def start(self):
        try:
            with Live(self.layout, refresh_per_second=4, screen=True) as live:
                while self.running:
                    self._update_display()
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Display error: {e}")
            print(f"Display error: {e}")

    def stop(self):
        self.running = False
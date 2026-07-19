from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

console = Console()

COLORS = {
    "primary": "#6C5CE7",
    "secondary": "#00B894",
    "warning": "#FDCB6E",
    "error": "#E17055",
    "muted": "#636E72",
    "bg_dark": "#2D3436",
    "white": "#DFE6E9",
}


class Display:
    @staticmethod
    def banner():
        title = Text("HUMAN-APPROVED EMAIL DRAFTER", style=f"bold {COLORS['primary']}")
        subtitle = Text("LangGraph  |  Human-in-the-Loop", style=COLORS["muted"])
        console.print()
        console.print(
            Panel(
                Columns([title, subtitle], align="center", expand=True),
                border_style=COLORS["primary"],
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )
        console.print()

    @staticmethod
    def input_fields(topic: str, recipient: str, tone: str):
        table = Table(
            title="Configuration",
            border_style=COLORS["muted"],
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 2),
        )
        table.add_column("Key", style=f"bold {COLORS['primary']}")
        table.add_column("Value", style=COLORS["white"])
        table.add_row("Topic", topic)
        table.add_row("Recipient", recipient)
        table.add_row("Tone", tone)
        console.print(table)
        console.print()

    @staticmethod
    def draft_panel(draft: str, version: int = 1):
        header = Text(f" DRAFT (v{version}) ", style=f"bold {COLORS['secondary']}")
        console.print(
            Panel(
                draft,
                title=header,
                border_style=COLORS["secondary"],
                box=box.ROUNDED,
                padding=(1, 2),
                width=min(console.width, 80),
            )
        )
        console.print()

    @staticmethod
    def status_bar(revision: int, max_rev: int, status: str):
        table = Table(
            border_style=COLORS["muted"],
            box=box.SIMPLE,
            show_header=False,
        )
        table.add_column("K", style=f"bold {COLORS['muted']}")
        table.add_column("V")
        table.add_row("Revisions", f"{revision}/{max_rev}")
        table.add_row("Status", Text(status, style=_status_color(status)))
        console.print(table)

    @staticmethod
    def approval():
        console.print(
            Panel(
                "[bold green]APPROVED[/bold green]",
                border_style=COLORS["secondary"],
                box=box.DOUBLE,
                padding=(0, 2),
            )
        )

    @staticmethod
    def revision(count: int):
        console.print(
            Panel(
                f"[bold yellow]REVISION {count}[/bold yellow]",
                border_style=COLORS["warning"],
                box=box.ROUNDED,
                padding=(0, 2),
            )
        )

    @staticmethod
    def error(msg: str):
        console.print(
            Panel(
                f"[bold red]{msg}[/bold red]",
                border_style=COLORS["error"],
                box=box.HEAVY,
                padding=(0, 2),
            )
        )

    @staticmethod
    def success(msg: str):
        console.print(
            Panel(
                f"[bold green]{msg}[/bold green]",
                border_style=COLORS["secondary"],
                box=box.ROUNDED,
                padding=(0, 2),
            )
        )

    @staticmethod
    def info(msg: str):
        console.print(f"  [dim]{msg}[/dim]")

    @staticmethod
    def prompt_input() -> str:
        return Prompt.ask(
            f"  [bold {COLORS['primary']}]Your response[/]",
            console=console,
        )

    @staticmethod
    def prompt_field(label: str, default: str = "") -> str:
        return Prompt.ask(
            f"  [bold {COLORS['primary']}]{label}[/]",
            default=default,
            console=console,
        )

    @staticmethod
    def spinner_start(msg: str = "Working..."):
        from rich.status import Status

        status = Status(msg, spinner="dots", console=console)
        status.start()
        return status

    @staticmethod
    def saved_path(path: str):
        console.print(f"  [dim]Saved to:[/dim] [link=file://{path}]{path}[/link]")


def _status_color(status: str) -> str:
    mapping = {
        "drafting": COLORS["warning"],
        "review": COLORS["primary"],
        "approved": COLORS["secondary"],
        "max_revisions": COLORS["error"],
    }
    return mapping.get(status, COLORS["white"])

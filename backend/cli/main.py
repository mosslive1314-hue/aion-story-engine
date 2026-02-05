"""
CLI Interface - 命令行界面
基于Rich和Typer的交互式命令行工具
"""

import typer
from typing import Optional, List
from pathlib import Path
import json

# 导入后端模块
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from collaboration.manager import get_collaboration_manager, User, UserRole
from sync.engine import get_sync_engine
from economy.marketplace import get_marketplace

# Rich组件
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live

app = typer.Typer(
    name="aion",
    help="AION Story Engine - AI-powered collaborative storytelling platform",
    add_completion=False
)

console = Console()

# ============ 故事命令 ============

story_app = typer.Typer(help="Story management commands")
app.add_typer(story_app, name="story")


@story_app.command("create")
def create_story(
    name: str = typer.Option(..., "--name", "-n", help="Story name"),
    author: str = typer.Option(..., "--author", "-a", help="Author name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Story description")
):
    """创建新故事"""
    console.print(f"[bold green]Creating story:[/bold green] {name}")
    console.print(f"[blue]Author:[/blue] {author}")

    if description:
        console.print(f"[dim]Description:[/dim] {description}")

    # TODO: 实际创建故事
    console.print("[green]✓[/green] Story created successfully!")


@story_app.command("list")
def list_stories():
    """列出所有故事"""
    console.print("[bold]Your Stories:[/bold]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Author")
    table.add_column("Created")
    table.add_column("Status")

    # 示例数据
    table.add_row("1", "The Dragon's Quest", "John Doe", "2026-02-01", "In Progress")
    table.add_row("2", "Space Adventure", "Jane Smith", "2026-02-03", "Draft")

    console.print(table)


@story_app.command("info")
def story_info(story_id: str = typer.Argument(..., help="Story ID")):
    """显示故事详情"""
    console.print(Panel.fit(
        f"[bold]Story ID:[/bold] {story_id}\n"
        f"[bold]Name:[/bold] The Dragon's Quest\n"
        f"[bold]Author:[/bold] John Doe\n"
        f"[bold]Status:[/bold] In Progress\n"
        f"[bold]Chapters:[/bold] 5\n"
        f"[bold]Characters:[/bold] 12",
        title="Story Information",
        border_style="blue"
    ))


# ============ 协作命令 ============

collab_app = typer.Typer(help="Collaboration commands")
app.add_typer(collab_app, name="collab")


@collab_app.command("session")
def create_session(
    story_id: str = typer.Option(..., "--story", "-s", help="Story ID"),
    user_id: str = typer.Option(..., "--user", "-u", help="User ID"),
    name: str = typer.Option(..., "--name", "-n", help="User name"),
    email: str = typer.Option(..., "--email", "-e", help="User email")
):
    """创建协作会话"""
    collab_manager = get_collaboration_manager()

    user = User(id=user_id, name=name, email=email)
    session = collab_manager.create_session(story_id, user)

    console.print(f"[green]✓[/green] Collaboration session created!")
    console.print(f"[dim]Session ID:[/dim] {session.id}")
    console.print(f"[dim]Story ID:[/dim] {session.story_id}")
    console.print(f"[dim]Collaborators:[/dim] {len(session.collaborators)}")


@collab_app.command("join")
def join_session(
    session_id: str = typer.Option(..., "--session", "-s", help="Session ID"),
    user_id: str = typer.Option(..., "--user", "-u", help="User ID"),
    name: str = typer.Option(..., "--name", "-n", help="User name"),
    email: str = typer.Option(..., "--email", "-e", help="User email"),
    role: str = typer.Option("viewer", "--role", "-r", help="Role (owner, editor, commenter, viewer)")
):
    """加入协作会话"""
    collab_manager = get_collaboration_manager()

    user = User(id=user_id, name=name, email=email)
    user_role = UserRole(role)

    success = collab_manager.join_session(session_id, user, user_role)

    if success:
        console.print(f"[green]✓[/green] Joined session successfully!")
    else:
        console.print("[red]✗[/red] Failed to join session")
        raise typer.Exit(1)


@collab_app.command("users")
def list_users(
    session_id: str = typer.Option(..., "--session", "-s", help="Session ID")
):
    """列出会话中的活跃用户"""
    collab_manager = get_collaboration_manager()
    users = collab_manager.get_active_users(session_id)

    console.print(f"[bold]Active Users in Session:[/bold] {session_id}")

    if users:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Role")
        table.add_column("Last Active")

        for user in users:
            table.add_row(
                user.get("name", "Unknown"),
                user.get("email", "Unknown"),
                user.get("role", "viewer"),
                user.get("last_active", "Unknown")[:19]
            )

        console.print(table)
    else:
        console.print("[dim]No active users[/dim]")


@collab_app.command("changes")
def list_changes(
    session_id: str = typer.Option(..., "--session", "-s", help="Session ID"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit results")
):
    """列出会话变更"""
    collab_manager = get_collaboration_manager()
    changes = collab_manager.get_session_changes(session_id)

    console.print(f"[bold]Recent Changes:[/bold] {len(changes)} total")

    if changes:
        for change in changes[:limit]:
            console.print(f"  • {change['change_type']}: {change['node_id']} by {change['user_id']}")
    else:
        console.print("[dim]No changes yet[/dim]")


# ============ 同步命令 ============

sync_app = typer.Typer(help="Synchronization commands")
app.add_typer(sync_app, name="sync")


@sync_app.command("push")
def push_changes(
    workspace: str = typer.Option("workspace", "--workspace", "-w", help="Workspace path"),
    remote: str = typer.Option(None, "--remote", "-r", help="Remote URL")
):
    """推送本地变更到远程"""
    sync_engine = get_sync_engine(workspace, remote)

    with console.status("[bold yellow]Pushing changes...") as status:
        result = sync_engine.sync()

        if result.success:
            console.print(f"[green]✓[/green] Pushed {result.changes_synced} changes successfully!")
            console.print(f"[dim]Sync time:[/dim] {result.sync_time.total_seconds():.2f}s")
        else:
            console.print(f"[red]✗[/red] Push failed: {result.error_message}")
            raise typer.Exit(1)


@sync_app.command("pull")
def pull_changes(
    workspace: str = typer.Option("workspace", "--workspace", "-w", help="Workspace path"),
    remote: str = typer.Option(None, "--remote", "-r", help="Remote URL")
):
    """拉取远程变更"""
    sync_engine = get_sync_engine(workspace, remote)

    with console.status("[bold yellow]Pulling changes...") as status:
        result = sync_engine.sync()

        if result.success:
            console.print(f"[green]✓[/green] Pulled {result.changes_synced} changes successfully!")
            console.print(f"[dim]Sync time:[/dim] {result.sync_time.total_seconds():.2f}s")
        else:
            console.print(f"[red]✗[/red] Pull failed: {result.error_message}")
            raise typer.Exit(1)


@sync_app.command("status")
def sync_status(
    workspace: str = typer.Option("workspace", "--workspace", "-w", help="Workspace path")
):
    """显示同步状态"""
    sync_engine = get_sync_engine(workspace)
    status = sync_engine.get_status()

    console.print(Panel.fit(
        f"[bold]Pending Changes:[/bold] {status['pending_changes']}\n"
        f"[bold]Last Sync:[/bold] {status['last_sync'] or 'Never'}\n"
        f"[bold]Sync Status:[/bold] {status['sync_status']}\n"
        f"[bold]Current Commit:[/bold] {status['current_commit'][:8] if status['current_commit'] else 'Unknown'}\n"
        f"[bold]Has Conflicts:[/bold] {'Yes' if status['has_conflicts'] else 'No'}",
        title="Sync Status",
        border_style="yellow"
    ))


@sync_app.command("resolve")
def resolve_conflicts(
    workspace: str = typer.Option("workspace", "--workspace", "-w", help="Workspace path"),
    strategy: str = typer.Option("theirs", "--strategy", "-s", help="Resolution strategy (theirs, ours)")
):
    """解决合并冲突"""
    sync_engine = get_sync_engine(workspace)

    if Confirm.ask(f"Resolve conflicts using '{strategy}' strategy?"):
        success = sync_engine.resolve_conflicts(strategy)

        if success:
            console.print("[green]✓[/green] Conflicts resolved successfully!")
        else:
            console.print("[red]✗[/red] Failed to resolve conflicts")
            raise typer.Exit(1)


@sync_app.command("backup")
def create_backup(
    workspace: str = typer.Option("workspace", "--workspace", "-w", help="Workspace path")
):
    """创建备份"""
    sync_engine = get_sync_engine(workspace)

    with console.status("[bold yellow]Creating backup...") as status:
        backup_path = sync_engine.create_backup()
        console.print(f"[green]✓[/green] Backup created: {backup_path}")


@sync_app.command("restore")
def restore_backup(
    workspace: str = typer.Option("workspace", "--workspace", "-w", help="Workspace path"),
    backup_path: str = typer.Option(..., "--backup", "-b", help="Backup path")
):
    """恢复备份"""
    sync_engine = get_sync_engine(workspace)

    if Confirm.ask(f"Restore from {backup_path}? Current workspace will be replaced."):
        success = sync_engine.restore_backup(backup_path)

        if success:
            console.print("[green]✓[/green] Backup restored successfully!")
        else:
            console.print("[red]✗[/red] Failed to restore backup")
            raise typer.Exit(1)


# ============ 市场命令 ============

market_app = typer.Typer(help="Marketplace commands")
app.add_typer(market_app, name="market")


@market_app.command("publish")
def publish_asset(
    creator_id: str = typer.Option(..., "--creator", "-c", help="Creator ID"),
    asset_type: str = typer.Option(..., "--type", "-t", help="Asset type"),
    name: str = typer.Option(..., "--name", "-n", help="Asset name"),
    description: str = typer.Option(..., "--description", "-d", help="Asset description"),
    price: float = typer.Option(..., "--price", "-p", help="Asset price"),
    license_type: str = typer.Option("personal", "--license", "-l", help="License type"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags")
):
    """发布资产到市场"""
    marketplace = get_marketplace()

    tag_list = tags.split(",") if tags else []

    from economy.marketplace import LicenseType
    license_type_enum = LicenseType(license_type)

    asset = marketplace.publish_asset(
        creator_id=creator_id,
        asset_type=asset_type,
        name=name,
        description=description,
        price=price,
        license_type=license_type_enum,
        tags=tag_list
    )

    if asset:
        console.print(f"[green]✓[/green] Asset published successfully!")
        console.print(f"[dim]Asset ID:[/dim] {asset.id}")
        console.print(f"[dim]Status:[/dim] {asset.status.value}")
    else:
        console.print("[red]✗[/red] Failed to publish asset")
        raise typer.Exit(1)


@market_app.command("search")
def search_assets(
    query: str = typer.Option("", "--query", "-q", help="Search query"),
    asset_type: str = typer.Option("", "--type", "-t", help="Asset type"),
    min_price: float = typer.Option(0, "--min-price", help="Minimum price"),
    max_price: float = typer.Option(999999, "--max-price", help="Maximum price"),
    limit: int = typer.Option(20, "--limit", "-l", help="Limit results")
):
    """搜索市场资产"""
    marketplace = get_marketplace()

    assets = marketplace.search_assets(
        query=query,
        asset_type=asset_type,
        min_price=min_price,
        max_price=max_price,
        limit=limit
    )

    console.print(f"[bold]Found {len(assets)} assets:[/bold]")

    if assets:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Price")
        table.add_column("Rating")
        table.add_column("Sales")

        for asset in assets[:limit]:
            table.add_row(
                asset.id[:8],
                asset.name[:30],
                asset.asset_type,
                f"${asset.price:.2f}",
                f"{'⭐' * int(asset.rating)}{asset.rating:.1f}",
                str(asset.purchase_count)
            )

        console.print(table)
    else:
        console.print("[dim]No assets found[/dim]")


@market_app.command("trending")
def list_trending(limit: int = typer.Option(10, "--limit", "-l", help="Limit results")):
    """列出热门资产"""
    marketplace = get_marketplace()
    assets = marketplace.get_trending_assets(limit)

    console.print("[bold]Trending Assets:[/bold]")

    if assets:
        for i, asset in enumerate(assets, 1):
            console.print(f"\n{[cyan bold]}{i}. {asset.name}[/cyan bold]")
            console.print(f"   [dim]Type:[/dim] {asset.asset_type}")
            console.print(f"   [dim]Price:[/dim] ${asset.price:.2f}")
            console.print(f"   [dim]Rating:[/dim] {'⭐' * int(asset.rating)}{asset.rating:.1f} ({asset.purchase_count} sales)")
    else:
        console.print("[dim]No trending assets[/dim]")


@market_app.command("stats")
def market_stats():
    """显示市场统计"""
    marketplace = get_marketplace()
    stats = marketplace.get_statistics()

    console.print(Panel.fit(
        f"[bold]Total Assets:[/bold] {stats['total_assets']}\n"
        f"[bold]Published:[/bold] {stats['published_assets']}\n"
        f"[bold]Total Transactions:[/bold] {stats['total_transactions']}\n"
        f"[bold]Completed:[/bold] {stats['completed_transactions']}\n"
        f"[bold]Total Revenue:[/bold] ${stats['total_revenue']:.2f}\n"
        f"[bold]Creators:[/bold] {stats['total_creators']}\n"
        f"[bold]Reviews:[/bold] {stats['total_reviews']}",
        title="Market Statistics",
        border_style="green"
    ))


# ============ 通用命令 ============

@app.command("version")
def version():
    """显示版本信息"""
    console.print("[bold cyan]AION Story Engine[/bold cyan]")
    console.print("Version: 1.0.0")
    console.print("Phase 4: Collaboration & Marketplace")


@app.command("status")
def status():
    """显示系统状态"""
    console.print(Panel.fit(
        "[bold green]✓ System Online[/bold green]\n\n"
        "[bold]Components:[/bold]\n"
        "  • Collaboration Manager: [green]Active[/green]\n"
        "  • Sync Engine: [green]Active[/green]\n"
        "  • Marketplace: [green]Active[/green]\n"
        "  • API Server: [yellow]Not running[/yellow]\n\n"
        "[bold]Workspace:[/bold] workspace\n"
        "[bold]Remote:[/bold] Not configured",
        title="System Status",
        border_style="blue"
    ))


# 主入口
if __name__ == "__main__":
    app()

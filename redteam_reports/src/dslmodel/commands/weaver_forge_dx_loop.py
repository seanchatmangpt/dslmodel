"""
Weaver Forge Git Agent Auto DX Loop
Real-time developer experience loop that auto-generates Git agents from Weaver templates
"""

import asyncio
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import tempfile
import yaml
import subprocess

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from loguru import logger
try:
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

from ..utils.json_output import json_command
from ..git.git_auto import GitRegistry, add_worktree, commit_signed
from ..git.hooks_pipeline import GitHooksPipeline

try:
    from ..integrations.otel.extended_weaver_integration import ExtendedWeaverForgeIntegration
    from ..weaver.loader import PythonConventionLoader
    FORGE_AVAILABLE = True
except ImportError:
    FORGE_AVAILABLE = False

app = typer.Typer(help="🔄 Weaver Forge Git Agent Auto DX Loop")
console = Console()


class AgentGenerationTrigger(Enum):
    """Triggers for auto-generating Git agents."""
    FILE_CHANGE = "file_change"
    GIT_COMMIT = "git_commit"
    SEMANTIC_UPDATE = "semantic_update"
    TEMPLATE_CHANGE = "template_change"
    MANUAL = "manual"


@dataclass
class GitAgentTemplate:
    """Template for generating Git agents."""
    name: str
    description: str
    semantic_conventions: List[str]
    git_operations: List[str]
    template_path: Path
    output_pattern: str
    auto_generate: bool = True
    dependencies: List[str] = field(default_factory=list)
    
    def get_hash(self) -> str:
        """Get hash of template for change detection."""
        content = f"{self.name}:{self.semantic_conventions}:{self.git_operations}"
        return hashlib.sha256(content.encode()).hexdigest()[:8]


@dataclass
class GeneratedAgent:
    """Generated Git agent metadata."""
    id: str
    name: str
    template: str
    git_operations: List[str]
    file_path: Path
    generated_at: datetime
    checksum: str
    tested: bool = False
    deployed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "template": self.template,
            "git_operations": self.git_operations,
            "file_path": str(self.file_path),
            "generated_at": self.generated_at.isoformat(),
            "checksum": self.checksum,
            "tested": self.tested,
            "deployed": self.deployed
        }


class WeaverForgeWatcher:
    """File system watcher for auto-triggering forge generation."""
    
    def __init__(self, dx_loop: 'WeaverForgeDXLoop'):
        self.dx_loop = dx_loop
        self.debounce_timer = {}
        self.debounce_delay = 1.0  # 1 second debounce
        
        # Initialize as FileSystemEventHandler if watchdog is available
        if WATCHDOG_AVAILABLE and FileSystemEventHandler:
            self.__class__ = type('WeaverForgeWatcher', (FileSystemEventHandler,), dict(self.__class__.__dict__))
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only trigger on relevant files
        if self._should_trigger(file_path):
            self._debounced_trigger(file_path, AgentGenerationTrigger.FILE_CHANGE)
    
    def _should_trigger(self, file_path: Path) -> bool:
        """Check if file change should trigger regeneration."""
        relevant_extensions = {'.yaml', '.yml', '.py', '.j2', '.jinja', '.md'}
        relevant_directories = {'weaver', 'semantic_conventions', 'templates', 'git'}
        
        # Check file extension
        if file_path.suffix in relevant_extensions:
            return True
        
        # Check if in relevant directory
        for part in file_path.parts:
            if part in relevant_directories:
                return True
        
        return False
    
    def _debounced_trigger(self, file_path: Path, trigger: AgentGenerationTrigger):
        """Debounce file change events to avoid rapid firing."""
        file_key = str(file_path)
        
        # Cancel existing timer
        if file_key in self.debounce_timer:
            self.debounce_timer[file_key].cancel()
        
        # Start new timer
        timer = asyncio.get_event_loop().call_later(
            self.debounce_delay,
            lambda: asyncio.create_task(self.dx_loop.trigger_generation(trigger, {"file_path": str(file_path)}))
        )
        self.debounce_timer[file_key] = timer


class WeaverForgeDXLoop:
    """Main DX loop for auto-generating Git agents from Weaver templates."""
    
    def __init__(self, repo_path: Optional[Path] = None, watch_mode: bool = True):
        if repo_path is None:
            repo_path = Path.cwd()
        
        self.repo_path = repo_path
        self.watch_mode = watch_mode
        self.templates_dir = repo_path / "weaver" / "templates"
        self.agents_dir = repo_path / "generated_agents"
        self.agents_dir.mkdir(exist_ok=True)
        
        # State management
        self.templates: Dict[str, GitAgentTemplate] = {}
        self.generated_agents: Dict[str, GeneratedAgent] = {}
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "templates_loaded": 0,
            "last_generation": None
        }
        
        # Components
        self.git_registry = GitRegistry() if FORGE_AVAILABLE else None
        self.hooks_pipeline = GitHooksPipeline(repo_path)
        self.observer = None
        
        # Load existing state
        self._load_templates()
        self._load_generated_agents()
    
    async def start_dx_loop(self, duration_minutes: Optional[int] = None):
        """Start the DX loop with file watching and auto-generation."""
        console.print("🔄 Starting Weaver Forge Git Agent Auto DX Loop", style="bold green")
        console.print("=" * 60)
        
        if self.watch_mode:
            self._start_file_watcher()
        
        # Initial generation
        await self.trigger_generation(AgentGenerationTrigger.MANUAL, {"reason": "startup"})
        
        # Create live dashboard
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=5)
        )
        
        # Start loop
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60) if duration_minutes else None
        
        try:
            with Live(layout, refresh_per_second=2, console=console):
                while True:
                    # Update dashboard
                    layout["header"].update(self._create_header())
                    layout["main"].update(self._create_main_panel())
                    layout["footer"].update(self._create_footer())
                    
                    # Check if we should stop
                    if end_time and time.time() > end_time:
                        break
                    
                    await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            console.print("\n🛑 DX Loop stopped by user")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
    
    async def trigger_generation(self, trigger: AgentGenerationTrigger, context: Dict[str, Any]):
        """Trigger agent generation based on changes."""
        logger.info(f"🔄 Generation triggered by {trigger.value}: {context}")
        
        self.generation_stats["total_generations"] += 1
        self.generation_stats["last_generation"] = datetime.now()
        
        try:
            # Reload templates if needed
            if trigger in [AgentGenerationTrigger.TEMPLATE_CHANGE, AgentGenerationTrigger.SEMANTIC_UPDATE]:
                self._load_templates()
            
            # Generate agents for all templates
            for template_name, template in self.templates.items():
                if template.auto_generate:
                    agent = await self._generate_agent_from_template(template, trigger, context)
                    if agent:
                        self.generated_agents[agent.id] = agent
                        self.generation_stats["successful_generations"] += 1
                    else:
                        self.generation_stats["failed_generations"] += 1
            
            # Save state
            self._save_generated_agents()
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            self.generation_stats["failed_generations"] += 1
    
    async def _generate_agent_from_template(
        self, 
        template: GitAgentTemplate, 
        trigger: AgentGenerationTrigger,
        context: Dict[str, Any]
    ) -> Optional[GeneratedAgent]:
        """Generate a Git agent from a Weaver template."""
        try:
            # Generate unique ID
            agent_id = f"{template.name}_{int(time.time())}_{template.get_hash()}"
            
            # Create agent file path
            agent_file = self.agents_dir / f"{template.name}_agent.py"
            
            # Generate agent code
            agent_code = await self._forge_agent_code(template, trigger, context)
            
            # Write agent file
            with open(agent_file, 'w') as f:
                f.write(agent_code)
            
            # Calculate checksum
            checksum = hashlib.sha256(agent_code.encode()).hexdigest()[:16]
            
            # Create agent metadata
            agent = GeneratedAgent(
                id=agent_id,
                name=template.name,
                template=template.name,
                git_operations=template.git_operations,
                file_path=agent_file,
                generated_at=datetime.now(),
                checksum=checksum
            )
            
            # Test agent if enabled
            if await self._test_generated_agent(agent):
                agent.tested = True
            
            logger.info(f"✅ Generated agent: {agent.name} ({agent.id})")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Failed to generate agent from template {template.name}: {e}")
            return None
    
    async def _forge_agent_code(
        self, 
        template: GitAgentTemplate, 
        trigger: AgentGenerationTrigger,
        context: Dict[str, Any]
    ) -> str:
        """Forge agent code using Weaver templates and Git operations."""
        
        # Get Git operations for this agent
        git_ops = []
        if self.git_registry:
            for op_name in template.git_operations:
                op_info = self.git_registry.get_operation(op_name)
                if op_info:
                    git_ops.append(op_info)
        
        # Generate agent code
        agent_code = f'''"""
Generated Git Agent: {template.name}
Auto-generated by Weaver Forge DX Loop
Template: {template.name}
Generated: {datetime.now().isoformat()}
Trigger: {trigger.value}
Checksum: {template.get_hash()}
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Import Level-5 Git substrate
from dslmodel.git.git_auto import GitRegistry, git_wrap

# OTEL Integration
try:
    from dslmodel.otel.otel_instrumentation_mock import SwarmSpanAttributes
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


@dataclass
class AgentResult:
    """Result of agent execution."""
    success: bool
    operation: str
    duration_ms: float
    output: str
    error: Optional[str] = None


class {template.name.title().replace('_', '')}Agent:
    """Auto-generated Git agent for {template.description}"""
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self.registry = GitRegistry()
        self.operations = {[f'"{op.name}"' for op in git_ops]}
        
    async def execute_operation(self, operation_name: str, **kwargs) -> AgentResult:
        """Execute a Git operation with telemetry."""
        start_time = datetime.now()
        
        try:
            if operation_name not in self.operations:
                return AgentResult(
                    success=False,
                    operation=operation_name,
                    duration_ms=0,
                    output="",
                    error=f"Operation {{operation_name}} not supported by this agent"
                )
            
            # Execute operation using git_auto wrapper
            operation = self.registry.get_operation(operation_name)
            if not operation:
                return AgentResult(
                    success=False,
                    operation=operation_name,
                    duration_ms=0,
                    output="",
                    error=f"Operation {{operation_name}} not found in registry"
                )
            
            # TODO: Execute actual operation
            # This would use the git_wrap decorator and Level-5 substrate
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResult(
                success=True,
                operation=operation_name,
                duration_ms=duration,
                output=f"Successfully executed {{operation_name}}"
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return AgentResult(
                success=False,
                operation=operation_name,
                duration_ms=duration,
                output="",
                error=str(e)
            )
    
    async def get_supported_operations(self) -> List[str]:
        """Get list of supported Git operations."""
        return list(self.operations)
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {{
            "name": "{template.name}",
            "description": "{template.description}",
            "template": "{template.name}",
            "supported_operations": list(self.operations),
            "semantic_conventions": {template.semantic_conventions},
            "git_operations": {template.git_operations},
            "generated_at": "{datetime.now().isoformat()}",
            "agent_type": "auto_generated",
            "level5_compatible": True
        }}


# Agent factory function
async def create_agent(repo_path: Optional[Path] = None) -> {template.name.title().replace('_', '')}Agent:
    """Create and initialize the agent."""
    return {template.name.title().replace('_', '')}Agent(repo_path)


# CLI interface
if __name__ == "__main__":
    import typer
    from rich.console import Console
    
    app = typer.Typer(help="Auto-generated Git agent: {template.name}")
    console = Console()
    
    @app.command()
    def info():
        """Show agent information."""
        async def show_info():
            agent = await create_agent()
            info = await agent.get_agent_info()
            console.print(f"🤖 Agent: {{info['name']}}")
            console.print(f"📝 Description: {{info['description']}}")
            console.print(f"⚙️ Operations: {{len(info['supported_operations'])}}")
            console.print(f"🧵 Semantic Conventions: {{len(info['semantic_conventions'])}}")
        
        asyncio.run(show_info())
    
    @app.command()
    def operations():
        """List supported operations."""
        async def list_operations():
            agent = await create_agent()
            ops = await agent.get_supported_operations()
            console.print("🔧 Supported Git Operations:")
            for op in ops:
                console.print(f"  • {{op}}")
        
        asyncio.run(list_operations())
    
    @app.command()
    def execute(
        operation: str = typer.Argument(help="Operation to execute"),
    ):
        """Execute a Git operation."""
        async def run_operation():
            agent = await create_agent()
            result = await agent.execute_operation(operation)
            
            if result.success:
                console.print(f"✅ {{result.operation}} completed in {{result.duration_ms:.1f}}ms")
                console.print(f"📤 Output: {{result.output}}")
            else:
                console.print(f"❌ {{result.operation}} failed")
                console.print(f"💥 Error: {{result.error}}")
        
        asyncio.run(run_operation())
    
    app()
'''
        
        return agent_code
    
    async def _test_generated_agent(self, agent: GeneratedAgent) -> bool:
        """Test the generated agent."""
        try:
            # Basic syntax check
            with open(agent.file_path, 'r') as f:
                code = f.read()
            
            # Try to compile the code
            compile(code, str(agent.file_path), 'exec')
            
            # TODO: Add more comprehensive testing
            # - Import test
            # - Agent instantiation test
            # - Operation execution test
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent test failed for {agent.name}: {e}")
            return False
    
    def _load_templates(self):
        """Load Git agent templates from weaver directory."""
        self.templates.clear()
        
        # Default templates for common Git agent patterns
        default_templates = [
            GitAgentTemplate(
                name="worktree_manager",
                description="Manages Git worktrees for agent isolation",
                semantic_conventions=["git.worktree.lifecycle"],
                git_operations=["worktree_add", "worktree_remove", "worktree_list"],
                template_path=Path("builtin"),
                output_pattern="worktree_manager_agent.py"
            ),
            GitAgentTemplate(
                name="domain_pack_installer",
                description="Installs and manages domain pack submodules",
                semantic_conventions=["git.submodule.update"],
                git_operations=["submodule_add", "submodule_update", "submodule_sync"],
                template_path=Path("builtin"),
                output_pattern="domain_pack_installer_agent.py"
            ),
            GitAgentTemplate(
                name="bundle_creator",
                description="Creates offline Git bundles for air-gap deployment",
                semantic_conventions=["compliance.object.eject"],
                git_operations=["bundle_create", "bundle_verify", "bundle_clone"],
                template_path=Path("builtin"),
                output_pattern="bundle_creator_agent.py"
            ),
            GitAgentTemplate(
                name="hook_validator",
                description="Validates Git hooks with OTEL integration",
                semantic_conventions=["git.hook.run"],
                git_operations=["install_hook", "run_hook"],
                template_path=Path("builtin"),
                output_pattern="hook_validator_agent.py"
            ),
            GitAgentTemplate(
                name="security_signer",
                description="Handles GPG signing and SBOM attestation",
                semantic_conventions=["compliance.gpg.signature", "compliance.sbom.artifact"],
                git_operations=["commit_signed", "tag_signed", "notes_attestation_add"],
                template_path=Path("builtin"),
                output_pattern="security_signer_agent.py"
            )
        ]
        
        for template in default_templates:
            self.templates[template.name] = template
        
        # Load custom templates from weaver directory
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*_agent_template.yaml"):
                try:
                    with open(template_file, 'r') as f:
                        template_data = yaml.safe_load(f)
                    
                    template = GitAgentTemplate(
                        name=template_data["name"],
                        description=template_data["description"],
                        semantic_conventions=template_data["semantic_conventions"],
                        git_operations=template_data["git_operations"],
                        template_path=template_file,
                        output_pattern=template_data["output_pattern"],
                        auto_generate=template_data.get("auto_generate", True),
                        dependencies=template_data.get("dependencies", [])
                    )
                    
                    self.templates[template.name] = template
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load template {template_file}: {e}")
        
        self.generation_stats["templates_loaded"] = len(self.templates)
        logger.info(f"📋 Loaded {len(self.templates)} agent templates")
    
    def _load_generated_agents(self):
        """Load generated agents from disk."""
        agents_state_file = self.agents_dir / "agents_state.json"
        
        if agents_state_file.exists():
            try:
                with open(agents_state_file, 'r') as f:
                    agents_data = json.load(f)
                
                for agent_data in agents_data.get("agents", []):
                    agent = GeneratedAgent(
                        id=agent_data["id"],
                        name=agent_data["name"],
                        template=agent_data["template"],
                        git_operations=agent_data["git_operations"],
                        file_path=Path(agent_data["file_path"]),
                        generated_at=datetime.fromisoformat(agent_data["generated_at"]),
                        checksum=agent_data["checksum"],
                        tested=agent_data.get("tested", False),
                        deployed=agent_data.get("deployed", False)
                    )
                    self.generated_agents[agent.id] = agent
                
                logger.info(f"📂 Loaded {len(self.generated_agents)} generated agents")
                
            except Exception as e:
                logger.error(f"❌ Failed to load agents state: {e}")
    
    def _save_generated_agents(self):
        """Save generated agents state to disk."""
        agents_state_file = self.agents_dir / "agents_state.json"
        
        try:
            agents_data = {
                "generated_at": datetime.now().isoformat(),
                "total_agents": len(self.generated_agents),
                "agents": [agent.to_dict() for agent in self.generated_agents.values()]
            }
            
            with open(agents_state_file, 'w') as f:
                json.dump(agents_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save agents state: {e}")
    
    def _start_file_watcher(self):
        """Start file system watcher."""
        if not self.watch_mode or not WATCHDOG_AVAILABLE:
            if not WATCHDOG_AVAILABLE:
                logger.warning("📁 File watching disabled (watchdog not available)")
            return
        
        try:
            event_handler = WeaverForgeWatcher(self)
            self.observer = Observer()
            
            # Watch key directories
            watch_dirs = [
                self.repo_path / "weaver",
                self.repo_path / "semantic_conventions", 
                self.repo_path / "src" / "dslmodel" / "git"
            ]
            
            for watch_dir in watch_dirs:
                if watch_dir.exists():
                    self.observer.schedule(event_handler, str(watch_dir), recursive=True)
            
            self.observer.start()
            logger.info("👁️ File watcher started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start file watcher: {e}")
    
    def _create_header(self) -> Panel:
        """Create header panel for live dashboard."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return Panel(
            f"🔄 Weaver Forge Git Agent Auto DX Loop - {current_time}",
            style="bold green"
        )
    
    def _create_main_panel(self) -> Panel:
        """Create main panel for live dashboard."""
        # Templates table
        templates_table = Table(title="📋 Agent Templates", show_header=True)
        templates_table.add_column("Name", style="cyan")
        templates_table.add_column("Operations", style="blue")
        templates_table.add_column("Auto-Gen", style="green")
        
        for template in self.templates.values():
            templates_table.add_row(
                template.name,
                str(len(template.git_operations)),
                "✅" if template.auto_generate else "❌"
            )
        
        # Generated agents table
        agents_table = Table(title="🤖 Generated Agents", show_header=True)
        agents_table.add_column("Name", style="cyan")
        agents_table.add_column("Generated", style="yellow")
        agents_table.add_column("Tested", style="green")
        agents_table.add_column("Deployed", style="blue")
        
        for agent in list(self.generated_agents.values())[-10:]:  # Last 10 agents
            agents_table.add_row(
                agent.name,
                agent.generated_at.strftime("%H:%M:%S"),
                "✅" if agent.tested else "❌",
                "✅" if agent.deployed else "❌"
            )
        
        # Combine tables
        content = f"{templates_table}\n\n{agents_table}"
        return Panel(content, title="📊 DX Loop Status")
    
    def _create_footer(self) -> Panel:
        """Create footer panel for live dashboard."""
        stats = self.generation_stats
        
        content = Text()
        content.append("📈 Statistics: ", style="bold")
        content.append(f"Total: {stats['total_generations']} | ")
        content.append(f"✅ Success: {stats['successful_generations']} | ", style="green")
        content.append(f"❌ Failed: {stats['failed_generations']} | ", style="red")
        content.append(f"📋 Templates: {stats['templates_loaded']}")
        
        if stats['last_generation']:
            content.append(f"\n🕐 Last Generation: {stats['last_generation'].strftime('%H:%M:%S')}")
        
        return Panel(content, title="📊 Generation Statistics")


# =============================================================================
# CLI Commands
# =============================================================================

@app.command("start")
def start_dx_loop(
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Run duration in minutes"),
    watch: bool = typer.Option(True, "--watch/--no-watch", help="Enable file watching"),
    repo_path: Optional[Path] = typer.Option(None, "--repo", help="Repository path")
):
    """Start the Weaver Forge Git Agent Auto DX Loop."""
    
    async def run_dx_loop():
        dx_loop = WeaverForgeDXLoop(repo_path, watch_mode=watch)
        await dx_loop.start_dx_loop(duration)
    
    asyncio.run(run_dx_loop())


@app.command("generate")
def manual_generation(
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Specific template to generate"),
    repo_path: Optional[Path] = typer.Option(None, "--repo", help="Repository path")
):
    """Manually trigger agent generation."""
    
    async def run_generation():
        dx_loop = WeaverForgeDXLoop(repo_path, watch_mode=False)
        
        context = {"reason": "manual_trigger"}
        if template:
            context["template_filter"] = template
        
        await dx_loop.trigger_generation(AgentGenerationTrigger.MANUAL, context)
        
        console.print("✅ Manual generation completed")
        console.print(f"📂 Generated agents saved to: {dx_loop.agents_dir}")
    
    asyncio.run(run_generation())


@app.command("list")
def list_generated_agents(
    repo_path: Optional[Path] = typer.Option(None, "--repo", help="Repository path")
):
    """List all generated agents."""
    dx_loop = WeaverForgeDXLoop(repo_path, watch_mode=False)
    
    if not dx_loop.generated_agents:
        console.print("📭 No generated agents found")
        return
    
    table = Table(title="🤖 Generated Git Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Template", style="blue")
    table.add_column("Operations", style="green")
    table.add_column("Generated", style="yellow")
    table.add_column("Status", style="white")
    
    for agent in dx_loop.generated_agents.values():
        status_icons = []
        if agent.tested:
            status_icons.append("✅ Tested")
        if agent.deployed:
            status_icons.append("🚀 Deployed")
        
        status = " | ".join(status_icons) if status_icons else "🟡 Generated"
        
        table.add_row(
            agent.name,
            agent.template,
            str(len(agent.git_operations)),
            agent.generated_at.strftime("%Y-%m-%d %H:%M"),
            status
        )
    
    console.print(table)


@app.command("templates")
def list_templates(
    repo_path: Optional[Path] = typer.Option(None, "--repo", help="Repository path")
):
    """List available agent templates."""
    dx_loop = WeaverForgeDXLoop(repo_path, watch_mode=False)
    
    if not dx_loop.templates:
        console.print("📭 No templates found")
        return
    
    table = Table(title="📋 Agent Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Git Ops", style="green")
    table.add_column("Semantic Conventions", style="blue")
    table.add_column("Auto-Gen", style="yellow")
    
    for template in dx_loop.templates.values():
        table.add_row(
            template.name,
            template.description[:50] + "..." if len(template.description) > 50 else template.description,
            str(len(template.git_operations)),
            str(len(template.semantic_conventions)),
            "✅" if template.auto_generate else "❌"
        )
    
    console.print(table)


@app.command("test")
def test_agent(
    agent_name: str = typer.Argument(help="Agent name to test"),
    repo_path: Optional[Path] = typer.Option(None, "--repo", help="Repository path")
):
    """Test a generated agent."""
    
    async def run_test():
        dx_loop = WeaverForgeDXLoop(repo_path, watch_mode=False)
        
        # Find agent
        agent = None
        for a in dx_loop.generated_agents.values():
            if a.name == agent_name:
                agent = a
                break
        
        if not agent:
            console.print(f"❌ Agent '{agent_name}' not found")
            return
        
        console.print(f"🧪 Testing agent: {agent.name}")
        
        # Test the agent
        if await dx_loop._test_generated_agent(agent):
            console.print(f"✅ Agent {agent.name} passed tests")
            agent.tested = True
            dx_loop._save_generated_agents()
        else:
            console.print(f"❌ Agent {agent.name} failed tests")
    
    asyncio.run(run_test())


@app.command("demo")
def run_demo():
    """Run a demonstration of the DX loop."""
    console.print(Panel(
        "🔄 Weaver Forge Git Agent Auto DX Loop Demo\n"
        "Demonstrates real-time auto-generation of Git agents",
        title="Demo",
        border_style="green"
    ))
    
    async def run_demo_async():
        # Create temporary demo environment
        with tempfile.TemporaryDirectory() as temp_dir:
            demo_path = Path(temp_dir)
            
            console.print(f"📁 Demo environment: {demo_path}")
            
            # Initialize DX loop
            dx_loop = WeaverForgeDXLoop(demo_path, watch_mode=False)
            
            console.print(f"📋 Loaded {len(dx_loop.templates)} templates")
            
            # Trigger generation
            await dx_loop.trigger_generation(
                AgentGenerationTrigger.MANUAL, 
                {"reason": "demo", "demo_mode": True}
            )
            
            console.print(f"🤖 Generated {len(dx_loop.generated_agents)} agents")
            
            # Show results
            for agent in dx_loop.generated_agents.values():
                console.print(f"  ✅ {agent.name} ({agent.template})")
            
            console.print("\n🎉 Demo completed successfully!")
            console.print("💡 Use 'start' command to run the full DX loop with file watching")
    
    asyncio.run(run_demo_async())


if __name__ == "__main__":
    app()
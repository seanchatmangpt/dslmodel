#!/usr/bin/env python3
"""
System Introspection - Echo Internal Structure
==============================================

Scripts to analyze and visualize the complex internal structure of DSLModel:
- Command hierarchy and dependencies
- Capability mapping and relationships  
- Telemetry flow and data pipelines
- System health and integration status
- Architecture visualization

Usage: dsl introspect <command>
"""

import typer
import json
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns

app = typer.Typer(help="System introspection and structure analysis")
console = Console()


@dataclass
class ModuleInfo:
    """Information about a module in the system"""
    name: str
    path: str
    commands: List[str]
    dependencies: List[str]
    imports: List[str]
    classes: List[str]
    functions: List[str]
    size_lines: int
    last_modified: str


@dataclass
class CommandHierarchy:
    """Command structure hierarchy"""
    name: str
    help_text: str
    module_source: str
    subcommands: List[str]
    parent: Optional[str]
    consolidation_target: Optional[str]


@dataclass
class SystemArchitecture:
    """Overall system architecture"""
    total_modules: int
    total_commands: int
    total_lines_of_code: int
    command_hierarchy: List[CommandHierarchy]
    module_dependencies: Dict[str, List[str]]
    capability_matrix: Dict[str, Dict[str, bool]]
    telemetry_flows: List[Dict[str, Any]]


class SystemIntrospector:
    """Analyze and visualize DSLModel internal structure"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.commands_path = self.base_path / "commands"
        self.system_info = None
        
    def analyze_module_structure(self) -> List[ModuleInfo]:
        """Analyze all modules in the commands directory"""
        modules = []
        
        console.print("🔍 Analyzing module structure...")
        
        for py_file in self.commands_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                module_info = self._analyze_single_module(py_file)
                modules.append(module_info)
            except Exception as e:
                console.print(f"⚠️ Failed to analyze {py_file.name}: {e}")
        
        return sorted(modules, key=lambda x: x.size_lines, reverse=True)
    
    def _analyze_single_module(self, module_path: Path) -> ModuleInfo:
        """Analyze a single Python module"""
        content = module_path.read_text()
        lines = content.split('\n')
        
        # Extract imports
        imports = []
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        
        # Try to dynamically import and analyze
        module_name = f"dslmodel.commands.{module_path.stem}"
        commands = []
        classes = []
        functions = []
        dependencies = []
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract commands (typer apps)
            if hasattr(module, 'app'):
                commands.append(f"{module_path.stem}.app")
            
            # Extract classes and functions
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == module_name:
                    classes.append(name)
                elif inspect.isfunction(obj) and obj.__module__ == module_name:
                    functions.append(name)
            
            # Extract dependencies from imports
            for imp in imports:
                if 'dslmodel' in imp:
                    dependencies.append(imp.split('.')[-1] if '.' in imp else imp)
        
        except Exception as e:
            # Fallback to text analysis
            console.print(f"🔍 Using text analysis for {module_path.name}: {e}")
            
            # Text-based extraction
            for line in lines:
                if 'class ' in line and ':' in line:
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    classes.append(class_name)
                elif 'def ' in line and ':' in line and not line.strip().startswith('#'):
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    functions.append(func_name)
                elif 'app = typer.Typer' in line:
                    commands.append(f"{module_path.stem}.app")
        
        return ModuleInfo(
            name=module_path.stem,
            path=str(module_path),
            commands=commands,
            dependencies=dependencies,
            imports=imports,
            classes=classes,
            functions=functions,
            size_lines=len(lines),
            last_modified=datetime.fromtimestamp(module_path.stat().st_mtime).isoformat()
        )
    
    def build_command_hierarchy(self) -> List[CommandHierarchy]:
        """Build the complete command hierarchy"""
        
        # Known command structure from CLI analysis
        cli_commands = {
            # Core consolidated commands
            "dsl": {"help": "🎯 Consolidated CLI - Core and Advanced commands", "module": "consolidated_cli", "parent": None},
            "core": {"help": "Core commands (80% usage)", "module": "consolidated_cli", "parent": "dsl"},
            "advanced": {"help": "Advanced commands (20% usage)", "module": "consolidated_cli", "parent": "dsl"},
            
            # Evolution systems
            "evolve": {"help": "Ultimate 8020 Evolution System", "module": "unified_8020_evolution", "parent": None},
            "evolve-unified": {"help": "Unified Evolution System", "module": "unified_evolution_cli", "parent": None},
            "evolve-legacy": {"help": "Legacy autonomous evolution", "module": "evolution", "parent": None},
            "auto-evolve": {"help": "Automatic evolution with SwarmAgent", "module": "auto_evolution", "parent": None},
            
            # Agent systems
            "agents": {"help": "Agent coordination with worktrees", "module": "agent_coordination_cli", "parent": None},
            "swarm": {"help": "SwarmAgent coordination", "module": "swarm", "parent": None},
            "swarm-worktree": {"help": "SwarmAgent worktree coordination", "module": "swarm_worktree", "parent": None},
            
            # Validation systems
            "validate": {"help": "OTEL validation and testing", "module": "validate_otel", "parent": None},
            "validate-weaver": {"help": "Weaver-first OTEL validation", "module": "validate_weaver", "parent": None},
            "validation-loop": {"help": "Continuous validation loop", "module": "validation_loop", "parent": None},
            "8020": {"help": "8020 feature validation", "module": "complete_8020_validation", "parent": None},
            
            # Development tools
            "forge": {"help": "Weaver Forge workflow", "module": "forge", "parent": None},
            "weaver": {"help": "Weaver semantic conventions", "module": "weaver", "parent": None},
            "weaver-health": {"help": "Weaver health checks", "module": "weaver_health_check", "parent": None},
            "worktree": {"help": "Git worktree management", "module": "worktree", "parent": None},
            
            # Specialized systems
            "ollama": {"help": "Ollama validation", "module": "ollama_validate", "parent": None},
            "ollama-auto": {"help": "Autonomous Ollama system", "module": "ollama_autonomous", "parent": None},
            "telemetry": {"help": "Real-time telemetry monitoring", "module": "telemetry_cli", "parent": None},
            "redteam": {"help": "Security testing", "module": "redteam", "parent": None},
            "demo": {"help": "Automated demonstrations", "module": "demo", "parent": None},
            "thesis": {"help": "SwarmSH thesis implementation", "module": "thesis_cli", "parent": None},
            "capability": {"help": "Capability mapping", "module": "capability_map", "parent": None},
            "slidev": {"help": "Slidev presentation tools", "module": "slidev", "parent": None},
            
            # Generation
            "gen": {"help": "Generate DSLModel classes", "module": "cli", "parent": None},
            "openapi": {"help": "Generate from OpenAPI", "module": "cli", "parent": None}
        }
        
        # Consolidation mapping
        consolidation_map = {
            "gen": "dsl core gen",
            "evolve": "dsl core evolve ultimate", 
            "agents": "dsl core agent coordinate",
            "validate": "dsl core validate otel",
            "8020": "dsl core validate 8020",
            "forge": "dsl core dev forge",
            "weaver": "dsl core dev weaver",
            "worktree": "dsl core dev worktree",
            "demo": "dsl core demo",
            "redteam": "dsl advanced security redteam",
            "telemetry": "dsl advanced telemetry monitor",
            "thesis": "dsl advanced research thesis"
        }
        
        hierarchy = []
        for cmd_name, info in cli_commands.items():
            hierarchy.append(CommandHierarchy(
                name=cmd_name,
                help_text=info["help"],
                module_source=info["module"],
                subcommands=[],  # Would need deeper analysis
                parent=info["parent"],
                consolidation_target=consolidation_map.get(cmd_name)
            ))
        
        return hierarchy
    
    def analyze_capability_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Analyze capability matrix across systems"""
        
        capabilities = [
            "OTEL_telemetry", "Weaver_conventions", "Git_worktree", "SwarmAgent_coordination",
            "AI_generation", "Validation_pipeline", "Security_testing", "Auto_evolution",
            "Performance_monitoring", "Error_handling", "Learning_patterns", "8020_validation"
        ]
        
        systems = [
            "unified_8020_evolution", "unified_evolution_cli", "auto_evolution", "evolution",
            "swarm", "agent_coordination_cli", "swarm_worktree", "validate_otel",
            "validate_weaver", "complete_8020_validation", "forge", "weaver", "redteam",
            "telemetry_cli", "ollama_autonomous", "worktree", "demo"
        ]
        
        # Build capability matrix based on known integrations
        matrix = {}
        for system in systems:
            matrix[system] = {}
            for capability in capabilities:
                # Logic based on system naming and known integrations
                has_capability = False
                
                if capability == "OTEL_telemetry":
                    has_capability = any(x in system for x in ["validate", "telemetry", "swarm", "8020", "evolution"])
                elif capability == "Weaver_conventions":
                    has_capability = any(x in system for x in ["weaver", "forge", "validate_weaver", "8020"])
                elif capability == "Git_worktree":
                    has_capability = any(x in system for x in ["worktree", "swarm_worktree", "evolution", "8020"])
                elif capability == "SwarmAgent_coordination":
                    has_capability = any(x in system for x in ["swarm", "agent", "coordination", "8020"])
                elif capability == "AI_generation":
                    has_capability = any(x in system for x in ["evolution", "auto", "forge", "ollama"])
                elif capability == "Validation_pipeline":
                    has_capability = any(x in system for x in ["validate", "8020", "validation"])
                elif capability == "Security_testing":
                    has_capability = "redteam" in system
                elif capability == "Auto_evolution":
                    has_capability = any(x in system for x in ["evolution", "auto", "8020"])
                elif capability == "Performance_monitoring":
                    has_capability = any(x in system for x in ["telemetry", "validate", "8020"])
                elif capability == "Error_handling":
                    has_capability = any(x in system for x in ["validate", "telemetry", "8020", "evolution"])
                elif capability == "Learning_patterns":
                    has_capability = any(x in system for x in ["evolution", "auto", "8020", "ollama"])
                elif capability == "8020_validation":
                    has_capability = any(x in system for x in ["8020", "unified_8020", "complete_8020"])
                
                matrix[system][capability] = has_capability
        
        return matrix
    
    def generate_telemetry_flows(self) -> List[Dict[str, Any]]:
        """Generate telemetry flow analysis"""
        
        flows = [
            {
                "name": "Evolution Telemetry Flow",
                "source": "unified_8020_evolution",
                "spans": ["evolution.analysis", "evolution.generation", "evolution.validation", "evolution.learning"],
                "targets": ["OTEL_collector", "Weaver_validator", "Learning_system"],
                "data_volume": "high",
                "criticality": "high"
            },
            {
                "name": "SwarmAgent Coordination Flow",
                "source": "swarm_worktree",
                "spans": ["swarm.coordination", "swarm.worktree", "swarm.validation", "swarm.telemetry"],
                "targets": ["OTEL_collector", "Coordination_engine"],
                "data_volume": "medium",
                "criticality": "high"
            },
            {
                "name": "8020 Validation Flow",
                "source": "complete_8020_validation",
                "spans": ["8020.analysis", "8020.worktree", "8020.validation", "8020.completion"],
                "targets": ["OTEL_collector", "Efficiency_analyzer"],
                "data_volume": "medium",
                "criticality": "medium"
            },
            {
                "name": "Weaver Convention Flow",
                "source": "validate_weaver",
                "spans": ["weaver.validation", "weaver.compliance", "weaver.reporting"],
                "targets": ["OTEL_collector", "Convention_store"],
                "data_volume": "low",
                "criticality": "medium"
            }
        ]
        
        return flows
    
    def get_system_architecture(self) -> SystemArchitecture:
        """Get complete system architecture analysis"""
        
        console.print("🏗️ Analyzing complete system architecture...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task1 = progress.add_task("Analyzing modules...", total=100)
            modules = self.analyze_module_structure()
            progress.update(task1, completed=100)
            
            task2 = progress.add_task("Building command hierarchy...", total=100)
            hierarchy = self.build_command_hierarchy()
            progress.update(task2, completed=100)
            
            task3 = progress.add_task("Analyzing capabilities...", total=100)
            capabilities = self.analyze_capability_matrix()
            progress.update(task3, completed=100)
            
            task4 = progress.add_task("Mapping telemetry flows...", total=100)
            flows = self.generate_telemetry_flows()
            progress.update(task4, completed=100)
        
        # Calculate totals
        total_lines = sum(m.size_lines for m in modules)
        total_commands = len(hierarchy)
        
        # Build module dependencies
        dependencies = {}
        for module in modules:
            dependencies[module.name] = module.dependencies
        
        return SystemArchitecture(
            total_modules=len(modules),
            total_commands=total_commands,
            total_lines_of_code=total_lines,
            command_hierarchy=hierarchy,
            module_dependencies=dependencies,
            capability_matrix=capabilities,
            telemetry_flows=flows
        )


@app.command("structure")
def show_structure():
    """Show complete system structure analysis"""
    
    introspector = SystemIntrospector()
    modules = introspector.analyze_module_structure()
    
    console.print("🏗️ DSLModel System Structure Analysis")
    console.print("=" * 45)
    
    # Summary panel
    total_lines = sum(m.size_lines for m in modules)
    total_classes = sum(len(m.classes) for m in modules)
    total_functions = sum(len(m.functions) for m in modules)
    
    console.print(Panel(
        f"📊 **System Metrics**:\n"
        f"• Total Modules: {len(modules)}\n"
        f"• Total Lines of Code: {total_lines:,}\n"
        f"• Total Classes: {total_classes}\n"
        f"• Total Functions: {total_functions}\n"
        f"• Average Module Size: {total_lines // len(modules):,} lines\n"
        f"• Largest Module: {modules[0].name} ({modules[0].size_lines:,} lines)",
        title="🔍 System Overview",
        border_style="blue"
    ))
    
    # Top modules table
    table = Table(title="📋 Top Modules by Size")
    table.add_column("Module", style="cyan")
    table.add_column("Lines", style="yellow")
    table.add_column("Classes", style="green")
    table.add_column("Functions", style="blue")
    table.add_column("Commands", style="red")
    
    for module in modules[:15]:  # Top 15
        table.add_row(
            module.name,
            f"{module.size_lines:,}",
            str(len(module.classes)),
            str(len(module.functions)),
            str(len(module.commands))
        )
    
    console.print(table)


@app.command("hierarchy")
def show_command_hierarchy():
    """Show command hierarchy and consolidation mapping"""
    
    introspector = SystemIntrospector()
    hierarchy = introspector.build_command_hierarchy()
    
    console.print("🌳 Command Hierarchy Analysis")
    console.print("=" * 35)
    
    # Build tree structure
    tree = Tree("🧬 DSLModel CLI Commands")
    
    # Group by consolidation status
    consolidated = [h for h in hierarchy if h.consolidation_target]
    legacy = [h for h in hierarchy if not h.consolidation_target and h.parent is None]
    core_sub = [h for h in hierarchy if h.parent == "dsl"]
    
    # Consolidated section
    consolidated_branch = tree.add("🎯 [bold green]Consolidated Commands[/bold green]")
    for cmd in consolidated:
        cmd_branch = consolidated_branch.add(f"[red]{cmd.name}[/red] → [green]{cmd.consolidation_target}[/green]")
        cmd_branch.add(f"📝 {cmd.help_text}")
        cmd_branch.add(f"📁 Module: {cmd.module_source}")
    
    # Core structure
    core_branch = tree.add("🎯 [bold blue]Core Structure[/bold blue]")
    dsl_branch = core_branch.add("[cyan]dsl[/cyan] (Consolidated Interface)")
    for cmd in core_sub:
        sub_branch = dsl_branch.add(f"[blue]{cmd.name}[/blue]")
        sub_branch.add(f"📝 {cmd.help_text}")
    
    # Legacy commands
    legacy_branch = tree.add("🏛️ [bold yellow]Legacy Commands[/bold yellow]")
    for cmd in legacy[:10]:  # Show first 10
        cmd_branch = legacy_branch.add(f"[yellow]{cmd.name}[/yellow]")
        cmd_branch.add(f"📝 {cmd.help_text}")
        cmd_branch.add(f"📁 Module: {cmd.module_source}")
    
    console.print(tree)
    
    # Consolidation summary
    console.print(Panel(
        f"📊 **Consolidation Impact**:\n"
        f"• Commands with consolidation target: {len(consolidated)}\n"
        f"• Legacy commands remaining: {len(legacy)}\n"
        f"• Core consolidated commands: {len(core_sub)}\n"
        f"• Consolidation ratio: {len(consolidated)}/{len(hierarchy)} = {len(consolidated)/len(hierarchy):.1%}",
        title="📈 Consolidation Summary",
        border_style="green"
    ))


@app.command("capabilities")
def show_capability_matrix():
    """Show capability matrix across all systems"""
    
    introspector = SystemIntrospector()
    matrix = introspector.analyze_capability_matrix()
    
    console.print("🎯 System Capability Matrix")
    console.print("=" * 32)
    
    # Create capability matrix table
    table = Table(title="🛠️ Capability Matrix")
    table.add_column("System", style="cyan", width=20)
    
    capabilities = list(next(iter(matrix.values())).keys())
    for cap in capabilities:
        table.add_column(cap.replace("_", "\n"), style="white", width=8)
    
    for system, caps in matrix.items():
        row = [system]
        for cap in capabilities:
            row.append("✅" if caps[cap] else "❌")
        table.add_row(*row)
    
    console.print(table)
    
    # Capability coverage analysis
    coverage = {}
    for cap in capabilities:
        count = sum(1 for system_caps in matrix.values() if system_caps[cap])
        coverage[cap] = count
    
    console.print(Panel(
        f"📊 **Capability Coverage**:\n" +
        "\n".join([f"• {cap.replace('_', ' ')}: {count}/{len(matrix)} systems ({count/len(matrix):.1%})" 
                  for cap, count in sorted(coverage.items(), key=lambda x: x[1], reverse=True)]),
        title="📈 Coverage Analysis",
        border_style="blue"
    ))


@app.command("telemetry")
def show_telemetry_flows():
    """Show telemetry flow analysis"""
    
    introspector = SystemIntrospector()
    flows = introspector.generate_telemetry_flows()
    
    console.print("📊 Telemetry Flow Analysis")
    console.print("=" * 30)
    
    for flow in flows:
        console.print(Panel(
            f"📡 **Source**: {flow['source']}\n"
            f"🎯 **Spans**: {', '.join(flow['spans'])}\n"
            f"📤 **Targets**: {', '.join(flow['targets'])}\n"
            f"📊 **Volume**: {flow['data_volume']}\n"
            f"🚨 **Criticality**: {flow['criticality']}",
            title=f"🔄 {flow['name']}",
            border_style="cyan"
        ))


@app.command("architecture")
def show_full_architecture():
    """Show complete system architecture analysis"""
    
    introspector = SystemIntrospector()
    arch = introspector.get_system_architecture()
    
    console.print("🏗️ Complete System Architecture")
    console.print("=" * 35)
    
    # Architecture overview
    console.print(Panel(
        f"🎯 **DSLModel Architecture Overview**:\n\n"
        f"📊 **Scale**:\n"
        f"• Modules: {arch.total_modules}\n"
        f"• Commands: {arch.total_commands}\n"
        f"• Lines of Code: {arch.total_lines_of_code:,}\n\n"
        f"🧬 **Evolution Systems**: 4 major systems\n"
        f"🤖 **Agent Coordination**: 3 specialized systems\n"
        f"✅ **Validation Pipeline**: 4 validation layers\n"
        f"🔧 **Development Tools**: 5 integrated tools\n"
        f"📊 **Telemetry Flows**: {len(arch.telemetry_flows)} active flows\n\n"
        f"🎯 **80/20 Consolidation**: {len([c for c in arch.command_hierarchy if c.consolidation_target])}/{arch.total_commands} commands consolidated",
        title="🏛️ System Architecture",
        border_style="blue"
    ))
    
    # System complexity metrics
    avg_deps = sum(len(deps) for deps in arch.module_dependencies.values()) / len(arch.module_dependencies)
    
    console.print(Panel(
        f"📈 **Complexity Metrics**:\n"
        f"• Average Dependencies per Module: {avg_deps:.1f}\n"
        f"• Capability Coverage: {sum(sum(caps.values()) for caps in arch.capability_matrix.values())} total capabilities\n"
        f"• Telemetry Integration: {len(arch.telemetry_flows)} active flows\n"
        f"• Command Consolidation: {len([c for c in arch.command_hierarchy if c.consolidation_target])} commands migrated\n"
        f"• Architecture Efficiency: {(arch.total_lines_of_code / arch.total_commands):.0f} lines per command",
        title="📊 Complexity Analysis",
        border_style="yellow"
    ))


@app.command("export")
def export_structure(
    format: str = typer.Option("json", help="Export format: json, yaml, txt"),
    output_file: str = typer.Option("system_structure.json", help="Output file path")
):
    """Export complete system structure to file"""
    
    introspector = SystemIntrospector()
    arch = introspector.get_system_architecture()
    
    console.print(f"📤 Exporting system structure to {output_file}...")
    
    # Convert to serializable format
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "system_metrics": {
            "total_modules": arch.total_modules,
            "total_commands": arch.total_commands,
            "total_lines_of_code": arch.total_lines_of_code
        },
        "command_hierarchy": [asdict(cmd) for cmd in arch.command_hierarchy],
        "module_dependencies": arch.module_dependencies,
        "capability_matrix": arch.capability_matrix,
        "telemetry_flows": arch.telemetry_flows
    }
    
    output_path = Path(output_file)
    
    if format == "json":
        output_path.write_text(json.dumps(export_data, indent=2))
    elif format == "yaml":
        import yaml
        output_path.write_text(yaml.dump(export_data, default_flow_style=False))
    elif format == "txt":
        # Simple text format
        lines = [
            "DSLModel System Structure Analysis",
            "=" * 40,
            f"Generated: {export_data['timestamp']}",
            "",
            "System Metrics:",
            f"- Total Modules: {export_data['system_metrics']['total_modules']}",
            f"- Total Commands: {export_data['system_metrics']['total_commands']}",
            f"- Total Lines: {export_data['system_metrics']['total_lines_of_code']:,}",
            "",
            "Command Hierarchy:",
        ]
        
        for cmd in export_data['command_hierarchy']:
            lines.append(f"- {cmd['name']}: {cmd['help_text']}")
            if cmd['consolidation_target']:
                lines.append(f"  → Consolidated to: {cmd['consolidation_target']}")
        
        output_path.write_text("\n".join(lines))
    
    console.print(f"✅ Exported to {output_path} ({format} format)")


if __name__ == "__main__":
    app()
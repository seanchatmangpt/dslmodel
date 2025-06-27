"""Capability Map command for SwarmAgent system visualization."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from rich.columns import Columns
from rich.text import Text

# Initialize console and app
console = Console()
app = typer.Typer(help="SwarmAgent capability mapping and visualization")


class CapabilityMapper:
    """Maps and visualizes SwarmAgent system capabilities."""
    
    def __init__(self):
        self.capabilities = self._load_capabilities()
        self.coordination_data = self._load_coordination_data()
    
    def _load_capabilities(self) -> Dict[str, Any]:
        """Load system capability definitions."""
        return {
            "agents": {
                "roberts": {
                    "name": "Roberts Rules Agent",
                    "domain": "Governance",
                    "states": ["IDLE", "MOTION_OPEN", "VOTING", "CLOSED"],
                    "triggers": {
                        "open": "Open motion for consideration",
                        "vote": "Call for votes",
                        "close": "Close motion with result"
                    },
                    "emits": ["scrum.sprint-planning", "lean.define-project"],
                    "capabilities": [
                        "Motion management",
                        "Voting coordination",
                        "Sprint approval",
                        "Governance decisions"
                    ]
                },
                "scrum": {
                    "name": "Scrum-at-Scale Agent",
                    "domain": "Delivery",
                    "states": ["IDLE", "PLANNING", "SPRINT_ACTIVE", "REVIEW"],
                    "triggers": {
                        "plan": "Plan sprint",
                        "start": "Start sprint execution",
                        "review": "Sprint review"
                    },
                    "emits": ["lean.define-project", "roberts.open"],
                    "capabilities": [
                        "Sprint planning",
                        "Backlog management",
                        "Velocity tracking",
                        "Quality monitoring"
                    ]
                },
                "lean": {
                    "name": "Lean Six Sigma Agent",
                    "domain": "Optimization",
                    "states": ["IDLE", "DEFINE", "MEASURE", "ANALYZE", "IMPROVE", "CONTROL"],
                    "triggers": {
                        "define": "Define improvement project",
                        "measure": "Measure current state",
                        "analyze": "Analyze root causes",
                        "improve": "Implement improvements",
                        "control": "Control and sustain"
                    },
                    "emits": ["scrum.plan", "roberts.open"],
                    "capabilities": [
                        "Process optimization",
                        "Root cause analysis",
                        "Metrics improvement",
                        "Quality control"
                    ]
                },
                "ping": {
                    "name": "Ping Test Agent",
                    "domain": "Testing",
                    "states": ["IDLE", "PING_SENT", "PONG_RECEIVED"],
                    "triggers": {
                        "ping": "Send ping",
                        "pong": "Receive pong"
                    },
                    "emits": ["ping.pong"],
                    "capabilities": [
                        "Connectivity testing",
                        "Latency measurement",
                        "Health checking"
                    ]
                }
            },
            "coordination_patterns": {
                "governance_delivery": {
                    "name": "Governance → Delivery",
                    "flow": ["roberts.close", "scrum.plan", "scrum.start"],
                    "description": "Motion approval triggers sprint planning"
                },
                "quality_optimization": {
                    "name": "Quality → Optimization",
                    "flow": ["scrum.review", "lean.define", "lean.measure"],
                    "description": "Quality issues trigger improvement projects"
                },
                "optimization_governance": {
                    "name": "Optimization → Governance",
                    "flow": ["lean.control", "roberts.open"],
                    "description": "Process changes require governance approval"
                }
            },
            "telemetry": {
                "span_types": {
                    "coordination": "Agent coordination events",
                    "transition": "State machine transitions",
                    "command": "Command emissions",
                    "decision": "Autonomous decisions"
                },
                "attributes": {
                    "required": ["name", "trace_id", "span_id", "timestamp"],
                    "agent_specific": ["motion_id", "sprint_number", "project_id", "voting_method"]
                }
            },
            "deployment": {
                "environments": {
                    "development": {
                        "storage": "Local JSONL files",
                        "agents": "Single process",
                        "monitoring": "Console logging"
                    },
                    "production": {
                        "storage": "Distributed (Kafka/Redis)",
                        "agents": "Kubernetes pods",
                        "monitoring": "OpenTelemetry + Prometheus"
                    }
                },
                "scaling": {
                    "horizontal": "Multiple agent instances",
                    "vertical": "Resource allocation",
                    "geographic": "Multi-region deployment"
                }
            }
        }
    
    def _load_coordination_data(self) -> Dict[str, Any]:
        """Load actual coordination data from telemetry."""
        coord_file = Path("/Users/sac/s2s/agent_coordination/telemetry_spans.jsonl")
        
        stats = {
            "total_spans": 0,
            "agent_activity": {},
            "coordination_flows": [],
            "recent_activity": []
        }
        
        if coord_file.exists():
            with open(coord_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            span = json.loads(line)
                            stats["total_spans"] += 1
                            
                            # Track agent activity
                            name = span.get("name", "")
                            if name.startswith("swarmsh."):
                                agent = name.split(".")[1]
                                stats["agent_activity"][agent] = stats["agent_activity"].get(agent, 0) + 1
                                
                                # Track recent activity
                                if len(stats["recent_activity"]) < 5:
                                    stats["recent_activity"].append({
                                        "name": name,
                                        "timestamp": span.get("timestamp", 0),
                                        "attributes": span.get("attributes", {})
                                    })
                        except:
                            continue
        
        return stats
    
    def generate_capability_tree(self) -> Tree:
        """Generate rich tree visualization of capabilities."""
        tree = Tree("🌟 [bold cyan]SwarmAgent Capabilities[/bold cyan]")
        
        # Agents branch
        agents_branch = tree.add("🤖 [bold yellow]Agents[/bold yellow]")
        for agent_id, agent_data in self.capabilities["agents"].items():
            agent_branch = agents_branch.add(f"[green]{agent_data['name']}[/green] ({agent_data['domain']})")
            
            # States
            states_branch = agent_branch.add("States")
            for state in agent_data["states"]:
                states_branch.add(f"[dim]{state}[/dim]")
            
            # Capabilities
            caps_branch = agent_branch.add("Capabilities")
            for cap in agent_data["capabilities"]:
                caps_branch.add(f"[cyan]• {cap}[/cyan]")
        
        # Coordination patterns branch
        patterns_branch = tree.add("🔗 [bold yellow]Coordination Patterns[/bold yellow]")
        for pattern_id, pattern_data in self.capabilities["coordination_patterns"].items():
            pattern_branch = patterns_branch.add(f"[green]{pattern_data['name']}[/green]")
            pattern_branch.add(f"[dim]{pattern_data['description']}[/dim]")
            flow_text = " → ".join(pattern_data["flow"])
            pattern_branch.add(f"[cyan]Flow: {flow_text}[/cyan]")
        
        # Deployment branch
        deploy_branch = tree.add("🚀 [bold yellow]Deployment Options[/bold yellow]")
        for env_name, env_data in self.capabilities["deployment"]["environments"].items():
            env_branch = deploy_branch.add(f"[green]{env_name.title()}[/green]")
            for key, value in env_data.items():
                env_branch.add(f"[dim]{key}: {value}[/dim]")
        
        return tree
    
    def generate_activity_table(self) -> Table:
        """Generate table of current system activity."""
        table = Table(title="📊 System Activity")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # Total spans
        total = self.coordination_data["total_spans"]
        table.add_row("Total Spans", str(total), "✅" if total > 0 else "❌")
        
        # Agent activity
        for agent, count in self.coordination_data["agent_activity"].items():
            table.add_row(f"{agent.title()} Agent", str(count), "🟢 Active")
        
        # Coordination flows
        if self.coordination_data["agent_activity"].get("roberts", 0) > 0 and \
           self.coordination_data["agent_activity"].get("scrum", 0) > 0:
            table.add_row("Governance→Delivery", "Detected", "✅")
        
        if self.coordination_data["agent_activity"].get("scrum", 0) > 0 and \
           self.coordination_data["agent_activity"].get("lean", 0) > 0:
            table.add_row("Quality→Optimization", "Detected", "✅")
        
        return table
    
    def generate_trigger_map(self) -> Dict[str, List[str]]:
        """Generate trigger dependency map."""
        trigger_map = {}
        
        for agent_id, agent_data in self.capabilities["agents"].items():
            for trigger_name, trigger_desc in agent_data["triggers"].items():
                full_trigger = f"{agent_id}.{trigger_name}"
                trigger_map[full_trigger] = {
                    "description": trigger_desc,
                    "emits": agent_data.get("emits", []),
                    "agent": agent_data["name"]
                }
        
        return trigger_map
    
    def generate_state_diagram(self, agent_id: str) -> str:
        """Generate ASCII state diagram for an agent."""
        agent = self.capabilities["agents"].get(agent_id)
        if not agent:
            return "Agent not found"
        
        states = agent["states"]
        diagram = f"\n{agent['name']} State Machine:\n\n"
        
        # Simple linear state flow
        for i, state in enumerate(states):
            if i > 0:
                diagram += "    ↓\n"
            diagram += f"  [{state}]"
            
            # Add trigger info
            for trigger_name, trigger_desc in agent["triggers"].items():
                if i < len(states) - 1:  # Not the last state
                    diagram += f"\n    └─ {trigger_name}: {trigger_desc}"
                    break
        
        diagram += "\n"
        return diagram
    
    def export_capability_map(self, format: str = "json") -> str:
        """Export capability map in various formats."""
        timestamp = datetime.now().isoformat()
        
        export_data = {
            "timestamp": timestamp,
            "capabilities": self.capabilities,
            "activity": self.coordination_data,
            "trigger_map": self.generate_trigger_map()
        }
        
        if format == "json":
            return json.dumps(export_data, indent=2)
        elif format == "markdown":
            md = f"# SwarmAgent Capability Map\n\n"
            md += f"Generated: {timestamp}\n\n"
            
            md += "## Agents\n\n"
            for agent_id, agent_data in self.capabilities["agents"].items():
                md += f"### {agent_data['name']}\n"
                md += f"- **Domain**: {agent_data['domain']}\n"
                md += f"- **States**: {', '.join(agent_data['states'])}\n"
                md += f"- **Capabilities**: {', '.join(agent_data['capabilities'])}\n\n"
            
            md += "## Coordination Patterns\n\n"
            for pattern_id, pattern_data in self.capabilities["coordination_patterns"].items():
                md += f"### {pattern_data['name']}\n"
                md += f"{pattern_data['description']}\n"
                md += f"**Flow**: {' → '.join(pattern_data['flow'])}\n\n"
            
            return md
        else:
            return str(export_data)


# CLI Commands
@app.command("show")
def show_capabilities(
    tree: bool = typer.Option(True, "--tree/--no-tree", help="Show capability tree"),
    activity: bool = typer.Option(True, "--activity/--no-activity", help="Show system activity"),
    triggers: bool = typer.Option(False, "--triggers", help="Show trigger map"),
    export_path: Optional[Path] = typer.Option(None, "--export", help="Export to file")
):
    """Display comprehensive capability map."""
    mapper = CapabilityMapper()
    
    if tree:
        console.print(mapper.generate_capability_tree())
        console.print()
    
    if activity:
        console.print(mapper.generate_activity_table())
        console.print()
    
    if triggers:
        trigger_map = mapper.generate_trigger_map()
        trigger_table = Table(title="🎯 Trigger Map")
        trigger_table.add_column("Trigger", style="cyan")
        trigger_table.add_column("Agent", style="green")
        trigger_table.add_column("Description", style="yellow")
        trigger_table.add_column("Emits", style="magenta")
        
        for trigger_id, trigger_data in trigger_map.items():
            emits_str = ", ".join(trigger_data["emits"]) if trigger_data["emits"] else "None"
            trigger_table.add_row(
                trigger_id,
                trigger_data["agent"],
                trigger_data["description"],
                emits_str
            )
        
        console.print(trigger_table)
    
    if export_path:
        format = "markdown" if export_path.suffix == ".md" else "json"
        content = mapper.export_capability_map(format)
        export_path.write_text(content)
        rprint(f"[green]✓[/green] Exported capability map to {export_path}")


@app.command("agent")
def show_agent_details(
    agent_name: str = typer.Argument(..., help="Agent name (roberts, scrum, lean, ping)"),
    states: bool = typer.Option(True, "--states/--no-states", help="Show state diagram"),
    triggers: bool = typer.Option(True, "--triggers/--no-triggers", help="Show triggers"),
    capabilities: bool = typer.Option(True, "--capabilities/--no-capabilities", help="Show capabilities")
):
    """Show detailed information about a specific agent."""
    mapper = CapabilityMapper()
    
    agent_data = mapper.capabilities["agents"].get(agent_name)
    if not agent_data:
        rprint(f"[red]Agent '{agent_name}' not found[/red]")
        rprint("Available agents: roberts, scrum, lean, ping")
        raise typer.Exit(1)
    
    # Agent header
    panel = Panel(
        f"[bold cyan]{agent_data['name']}[/bold cyan]\n"
        f"Domain: [yellow]{agent_data['domain']}[/yellow]",
        title=f"🤖 {agent_name.title()} Agent",
        border_style="cyan"
    )
    console.print(panel)
    
    if states:
        console.print(mapper.generate_state_diagram(agent_name))
    
    if triggers:
        trigger_table = Table(title="Triggers")
        trigger_table.add_column("Trigger", style="cyan")
        trigger_table.add_column("Description", style="yellow")
        
        for trigger_name, trigger_desc in agent_data["triggers"].items():
            trigger_table.add_row(f"{agent_name}.{trigger_name}", trigger_desc)
        
        console.print(trigger_table)
        console.print()
    
    if capabilities:
        cap_table = Table(title="Capabilities")
        cap_table.add_column("Capability", style="green")
        
        for cap in agent_data["capabilities"]:
            cap_table.add_row(cap)
        
        console.print(cap_table)
        
        # Show what this agent emits
        if agent_data.get("emits"):
            console.print(f"\n[yellow]Emits commands to:[/yellow] {', '.join(agent_data['emits'])}")


@app.command("patterns")
def show_coordination_patterns(
    visualize: bool = typer.Option(True, "--visualize/--no-visualize", help="Show visual flow")
):
    """Display coordination patterns between agents."""
    mapper = CapabilityMapper()
    
    for pattern_id, pattern_data in mapper.capabilities["coordination_patterns"].items():
        # Pattern panel
        flow_visual = " → ".join([f"[cyan]{step}[/cyan]" for step in pattern_data["flow"]])
        
        panel = Panel(
            f"{pattern_data['description']}\n\n"
            f"Flow: {flow_visual}",
            title=f"🔗 {pattern_data['name']}",
            border_style="green"
        )
        console.print(panel)
        console.print()


@app.command("validate")
def validate_system():
    """Validate system capabilities against actual implementation."""
    mapper = CapabilityMapper()
    
    validation_results = []
    
    # Check if agents are implemented
    agent_files = {
        "roberts": Path("/Users/sac/dev/dslmodel/src/dslmodel/agents/examples/roberts_agent.py"),
        "scrum": Path("/Users/sac/dev/dslmodel/src/dslmodel/agents/examples/scrum_agent.py"),
        "lean": Path("/Users/sac/dev/dslmodel/src/dslmodel/agents/examples/lean_agent.py"),
        "ping": Path("/Users/sac/dev/dslmodel/src/dslmodel/agents/examples/ping_agent.py")
    }
    
    for agent_name, agent_path in agent_files.items():
        if agent_path.exists():
            validation_results.append((f"{agent_name.title()} Agent Implementation", "✅", "Found"))
        else:
            validation_results.append((f"{agent_name.title()} Agent Implementation", "❌", "Not Found"))
    
    # Check coordination data
    if mapper.coordination_data["total_spans"] > 0:
        validation_results.append(("Coordination Data", "✅", f"{mapper.coordination_data['total_spans']} spans"))
    else:
        validation_results.append(("Coordination Data", "❌", "No spans found"))
    
    # Check Weaver schemas
    weaver_path = Path("/Users/sac/dev/dslmodel/src/dslmodel/weaver/registry/swarm_agents.yaml")
    if weaver_path.exists():
        validation_results.append(("Weaver Schema", "✅", "Found"))
    else:
        validation_results.append(("Weaver Schema", "❌", "Not Found"))
    
    # Display results
    table = Table(title="🔍 System Validation")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for component, status, details in validation_results:
        table.add_row(component, status, details)
    
    console.print(table)
    
    # Summary
    passed = sum(1 for _, status, _ in validation_results if status == "✅")
    total = len(validation_results)
    
    if passed == total:
        rprint(f"\n[bold green]✅ All {total} validations passed![/bold green]")
    else:
        rprint(f"\n[bold yellow]⚠️  {passed}/{total} validations passed[/bold yellow]")


@app.command("export")
def export_capabilities(
    output: Path = typer.Argument(..., help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, markdown)")
):
    """Export capability map to file."""
    mapper = CapabilityMapper()
    
    if format == "markdown":
        content = mapper.export_capability_map("markdown")
        if not output.suffix:
            output = output.with_suffix(".md")
    else:
        content = mapper.export_capability_map("json")
        if not output.suffix:
            output = output.with_suffix(".json")
    
    output.write_text(content)
    rprint(f"[green]✓[/green] Exported capability map to {output}")
    rprint(f"Format: {format}")
    rprint(f"Size: {len(content)} bytes")


if __name__ == "__main__":
    app()
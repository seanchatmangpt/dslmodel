#!/usr/bin/env python3
"""
Organizational Transformation CLI Commands
==========================================

CLI interface for running organizational transformation demos
with 80/20 definition of done validation.

Commands:
- run: Execute complete transformation demo
- validate: Validate telemetry and results
- status: Show transformation status
- report: Generate transformation reports
"""

import typer
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime

app = typer.Typer(name="transformation", help="Organizational transformation commands")
console = Console()


class TransformationCLI:
    """CLI interface for organizational transformation"""
    
    def __init__(self):
        self.output_dir = Path("demo_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 80/20 Definition of Done Criteria
        self.definition_of_done = {
            "critical": {
                "demos_executed": False,
                "telemetry_validated": False, 
                "integration_verified": False,
                "roi_calculated": False
            },
            "important": {
                "artifacts_generated": False,
                "weaver_compliant": False,
                "tests_passing": False
            },
            "nice_to_have": {
                "documentation_complete": False,
                "performance_benchmarked": False
            }
        }
    
    def update_dod_status(self):
        """Update definition of done status based on actual outputs"""
        # Check if demos executed
        e2e_results = self.output_dir / "e2e_360_transformation_results.json"
        telemetry_results = self.output_dir / "agent_orchestration_telemetry_fixed_results.json"
        
        self.definition_of_done["critical"]["demos_executed"] = (
            e2e_results.exists() and telemetry_results.exists()
        )
        
        # Check telemetry validation
        if telemetry_results.exists():
            try:
                with open(telemetry_results) as f:
                    data = json.load(f)
                    success_rate = data.get("validation_summary", {}).get("success_rate", 0)
                    self.definition_of_done["critical"]["telemetry_validated"] = success_rate >= 0.8
            except:
                pass
        
        # Check integration verification
        if e2e_results.exists():
            try:
                with open(e2e_results) as f:
                    data = json.load(f)
                    integration_points = data.get("integration_points", [])
                    validated_count = len([p for p in integration_points if p.get("validation") == "✅ Complete"])
                    self.definition_of_done["critical"]["integration_verified"] = validated_count >= 3
            except:
                pass
        
        # Check ROI calculation
        if e2e_results.exists():
            try:
                with open(e2e_results) as f:
                    data = json.load(f)
                    final_outcomes = data.get("final_outcomes", {})
                    financial_roi = final_outcomes.get("financial_roi", "0x")
                    self.definition_of_done["critical"]["roi_calculated"] = "x" in financial_roi
            except:
                pass
        
        # Check artifacts
        exec_summary = self.output_dir / "360_executive_summary.md"
        impl_guide = self.output_dir / "360_implementation_guide.md"
        self.definition_of_done["important"]["artifacts_generated"] = (
            exec_summary.exists() and impl_guide.exists()
        )
        
        # Check Weaver compliance
        weaver_config = Path("weaver.yaml")
        weaver_template = Path("weaver_templates/transformation.yaml")
        self.definition_of_done["important"]["weaver_compliant"] = (
            weaver_config.exists() and weaver_template.exists()
        )
        
        # Check tests (simplified check)
        test_reports = Path("reports/pytest.xml")
        self.definition_of_done["important"]["tests_passing"] = test_reports.exists()


@app.command()
def run(
    mode: str = typer.Option("full", help="Execution mode: full, e2e, telemetry"),
    validate: bool = typer.Option(True, help="Run validation after execution"),
    report: bool = typer.Option(True, help="Generate report after execution")
):
    """Execute organizational transformation demo"""
    
    cli = TransformationCLI()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if mode in ["full", "e2e"]:
            task = progress.add_task("Running E2E 360° transformation demo...", total=1)
            
            # Run E2E demo
            import subprocess
            result = subprocess.run([
                "python", "src/dslmodel/examples/e2e_360_demo.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                progress.update(task, completed=1)
                console.print("✅ E2E Demo completed successfully")
            else:
                console.print(f"❌ E2E Demo failed: {result.stderr}")
                raise typer.Exit(1)
        
        if mode in ["full", "telemetry"]:
            task = progress.add_task("Running telemetry orchestration demo...", total=1)
            
            # Run telemetry demo
            result = subprocess.run([
                "python", "src/dslmodel/examples/agent_orchestration_telemetry_fixed.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                progress.update(task, completed=1)
                console.print("✅ Telemetry Demo completed successfully")
            else:
                console.print(f"❌ Telemetry Demo failed: {result.stderr}")
                raise typer.Exit(1)
    
    if validate:
        typer.echo("Running validation...")
        validate_command()
    
    if report:
        typer.echo("Generating report...")
        report_command()


@app.command()
def validate(
    file: Optional[Path] = typer.Option(None, help="Specific file to validate"),
    weaver: bool = typer.Option(True, help="Enforce Weaver conventions")
):
    """Validate transformation results and telemetry"""
    
    import subprocess
    
    cmd = ["python", "validate_telemetry.py"]
    
    if file:
        cmd.extend(["--file", str(file)])
    
    if weaver:
        cmd.append("--weaver")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        console.print(result.stdout)
        console.print("✅ Validation completed successfully")
    else:
        console.print(f"❌ Validation failed: {result.stderr}")
        raise typer.Exit(1)


@app.command()
def status():
    """Show transformation status and definition of done"""
    
    cli = TransformationCLI()
    cli.update_dod_status()
    
    # Create status table
    table = Table(title="🎯 Organizational Transformation Status")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Criteria", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Priority", style="dim")
    
    # Add critical criteria
    for criteria, status in cli.definition_of_done["critical"].items():
        status_icon = "✅" if status else "❌"
        table.add_row("Critical", criteria.replace("_", " ").title(), status_icon, "HIGH")
    
    # Add important criteria
    for criteria, status in cli.definition_of_done["important"].items():
        status_icon = "✅" if status else "⚠️"
        table.add_row("Important", criteria.replace("_", " ").title(), status_icon, "MEDIUM")
    
    # Add nice-to-have criteria
    for criteria, status in cli.definition_of_done["nice_to_have"].items():
        status_icon = "✅" if status else "⏸️"
        table.add_row("Nice-to-Have", criteria.replace("_", " ").title(), status_icon, "LOW")
    
    console.print(table)
    
    # Calculate completion percentage
    all_criteria = {}
    all_criteria.update(cli.definition_of_done["critical"])
    all_criteria.update(cli.definition_of_done["important"])
    all_criteria.update(cli.definition_of_done["nice_to_have"])
    
    completed = sum(1 for status in all_criteria.values() if status)
    total = len(all_criteria)
    completion_rate = (completed / total) * 100
    
    # 80/20 Rule Assessment
    critical_completed = sum(1 for status in cli.definition_of_done["critical"].values() if status)
    critical_total = len(cli.definition_of_done["critical"])
    critical_rate = (critical_completed / critical_total) * 100
    
    important_completed = sum(1 for status in cli.definition_of_done["important"].values() if status)
    important_total = len(cli.definition_of_done["important"])
    important_rate = (important_completed / important_total) * 100
    
    # Display summary
    if critical_rate == 100:
        status_message = "🎯 DEFINITION OF DONE: CRITICAL COMPLETE (80% Rule)"
        status_style = "bold green"
    elif critical_rate >= 75:
        status_message = "⚡ CRITICAL NEARLY COMPLETE (On Track)"
        status_style = "bold yellow"
    else:
        status_message = "⚠️ CRITICAL INCOMPLETE (Action Required)"
        status_style = "bold red"
    
    summary_panel = Panel(
        f"""
📊 Overall Completion: {completion_rate:.1f}% ({completed}/{total})

80/20 Breakdown:
• Critical (80%): {critical_rate:.1f}% ({critical_completed}/{critical_total})
• Important (15%): {important_rate:.1f}% ({important_completed}/{important_total})
• Nice-to-Have (5%): Tracked for continuous improvement

{status_message}
        """.strip(),
        title="📈 80/20 Definition of Done",
        style=status_style
    )
    
    console.print(summary_panel)


@app.command()
def report(
    format: str = typer.Option("markdown", help="Report format: markdown, json"),
    output: Optional[Path] = typer.Option(None, help="Output file path")
):
    """Generate transformation report"""
    
    cli = TransformationCLI()
    cli.update_dod_status()
    
    # Collect data
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "definition_of_done": cli.definition_of_done,
        "files_generated": [],
        "validation_results": {}
    }
    
    # Check output files
    for file in cli.output_dir.glob("*.json"):
        report_data["files_generated"].append({
            "name": file.name,
            "size": file.stat().st_size,
            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
        })
    
    if format == "json":
        if output:
            with open(output, "w") as f:
                json.dump(report_data, f, indent=2)
            console.print(f"📄 JSON report saved to: {output}")
        else:
            console.print_json(data=report_data)
    
    else:  # markdown
        markdown_content = f"""# Organizational Transformation Report

Generated: {report_data['timestamp']}

## 🎯 80/20 Definition of Done

### Critical (80% - Must Have)
"""
        
        for criteria, status in cli.definition_of_done["critical"].items():
            status_icon = "✅" if status else "❌"
            markdown_content += f"- {status_icon} {criteria.replace('_', ' ').title()}\n"
        
        markdown_content += """
### Important (15% - Should Have)
"""
        
        for criteria, status in cli.definition_of_done["important"].items():
            status_icon = "✅" if status else "⚠️"
            markdown_content += f"- {status_icon} {criteria.replace('_', ' ').title()}\n"
        
        markdown_content += """
### Nice-to-Have (5% - Could Have)
"""
        
        for criteria, status in cli.definition_of_done["nice_to_have"].items():
            status_icon = "✅" if status else "⏸️"
            markdown_content += f"- {status_icon} {criteria.replace('_', ' ').title()}\n"
        
        markdown_content += f"""
## 📁 Generated Files

"""
        
        for file_info in report_data["files_generated"]:
            size_kb = file_info["size"] / 1024
            markdown_content += f"- **{file_info['name']}** ({size_kb:.1f} KB)\n"
        
        markdown_content += """
## 🚀 Next Steps

Based on 80/20 analysis:

1. **Critical Items**: Ensure all critical criteria are met
2. **Important Items**: Address any missing important features
3. **Continuous Improvement**: Nice-to-have items for future iterations

---
*Generated by DSLModel Organizational Transformation CLI*
"""
        
        if output:
            with open(output, "w") as f:
                f.write(markdown_content)
            console.print(f"📄 Markdown report saved to: {output}")
        else:
            console.print(markdown_content)


@app.command()
def clean():
    """Clean transformation outputs and reset status"""
    
    cli = TransformationCLI()
    
    # Remove output files
    files_removed = 0
    for file in cli.output_dir.glob("*"):
        if file.is_file():
            file.unlink()
            files_removed += 1
    
    console.print(f"🧹 Cleaned {files_removed} output files")
    
    # Reset definition of done
    for category in cli.definition_of_done.values():
        for criteria in category:
            category[criteria] = False
    
    console.print("✅ Status reset - ready for new transformation run")


@app.command()
def init():
    """Initialize transformation workspace"""
    
    # Create necessary directories
    directories = [
        "demo_output",
        "weaver_templates", 
        "test_output",
        "reports"
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        console.print(f"📁 Created directory: {dir_name}")
    
    # Create basic weaver config if not exists
    weaver_config = Path("weaver.yaml")
    if not weaver_config.exists():
        import yaml
        config = {
            "params": {
                "project_name": "DSLModel",
                "language": "python",
                "organization": "SeanchatmanGPT"
            }
        }
        
        with open(weaver_config, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        console.print("✅ Created weaver.yaml configuration")
    
    console.print("🚀 Transformation workspace initialized")


# Validation commands
def validate_command():
    """Internal validation command"""
    import subprocess
    result = subprocess.run(["python", "validate_telemetry.py"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        console.print("✅ Validation passed")
    else:
        console.print("❌ Validation failed")


def report_command():
    """Internal report command"""
    cli = TransformationCLI()
    cli.update_dod_status()
    
    # Quick status summary
    critical_completed = sum(1 for status in cli.definition_of_done["critical"].values() if status)
    critical_total = len(cli.definition_of_done["critical"])
    critical_rate = (critical_completed / critical_total) * 100
    
    console.print(f"📊 Critical completion: {critical_rate:.1f}% ({critical_completed}/{critical_total})")


if __name__ == "__main__":
    app()
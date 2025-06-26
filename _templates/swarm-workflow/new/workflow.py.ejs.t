---
to: src/dslmodel/workflows/<%= fileName %>.py
---
"""
<%= name.charAt(0).toUpperCase() + name.slice(1) %> Workflow - <%= description %>

This workflow coordinates <%= agents.join(', ') %> agents to execute
a <%= steps %>-step process with <%= has_rollback ? 'rollback capability' : 'no rollback' %>.
"""

import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class WorkflowStep:
    """Represents a single workflow step."""
    step_number: int
    agent: str
    action: str
    span_name: str
    attributes: Dict[str, Any]
    timeout: float = 30.0
    

class <%= name.charAt(0).toUpperCase() + name.slice(1) %>Workflow:
    """<%= description %>"""
    
    def __init__(self, span_file: Optional[Path] = None):
        self.span_file = span_file or Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
        self.workflow_id = f"<%= name %>_{int(time.time() * 1000)}"
        self.executed_steps: List[WorkflowStep] = []
        self.rollback_stack: List[WorkflowStep] = []
        
    def emit_span(self, span_name: str, attributes: Dict[str, Any]) -> bool:
        """Emit a telemetry span for agent coordination.
        
        Args:
            span_name: Name of the span (e.g., 'swarmsh.agent.action')
            attributes: Span attributes
            
        Returns:
            Success status
        """
        try:
            span_data = {
                "name": span_name,
                "trace_id": f"workflow_{self.workflow_id}",
                "span_id": f"span_{int(time.time() * 1e9)}",
                "timestamp": time.time(),
                "attributes": {
                    "workflow.id": self.workflow_id,
                    "workflow.type": "<%= name %>",
                    **attributes
                }
            }
            
            # Ensure directory exists
            self.span_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to JSONL file
            with self.span_file.open('a') as f:
                f.write(json.dumps(span_data) + '\n')
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error emitting span: {e}[/red]")
            return False
    
    def execute_step(self, step: WorkflowStep) -> bool:
        """Execute a single workflow step.
        
        Args:
            step: The workflow step to execute
            
        Returns:
            Success status
        """
        console.print(f"[blue]Step {step.step_number}:[/blue] {step.agent} - {step.action}")
        
        # Emit coordination span
        success = self.emit_span(step.span_name, step.attributes)
        
        if success:
            console.print(f"  [green]✓[/green] Span emitted: {step.span_name}")
            self.executed_steps.append(step)
<% if (has_rollback) { %>            self.rollback_stack.append(step)<% } %>
        else:
            console.print(f"  [red]✗[/red] Failed to emit span")
        
        # Simulate processing time
        time.sleep(0.5)
        
        return success
<% if (has_monitoring) { %>    
    def emit_monitoring_span(self, status: str, details: Dict[str, Any]):
        """Emit monitoring span for workflow status."""
        self.emit_span(
            "swarmsh.monitoring.<%= name %>_workflow",
            {
                "monitoring.status": status,
                "monitoring.workflow_id": self.workflow_id,
                "monitoring.steps_completed": len(self.executed_steps),
                **details
            }
        )
<% } %><% if (has_rollback) { %>    
    def rollback(self) -> bool:
        """Rollback executed steps in reverse order.
        
        Returns:
            Success status
        """
        console.print("\n[yellow]🔄 Initiating rollback...[/yellow]")
        
        rollback_success = True
        while self.rollback_stack:
            step = self.rollback_stack.pop()
            
            console.print(f"[yellow]Rolling back step {step.step_number}:[/yellow] {step.agent}")
            
            # Emit rollback span
            success = self.emit_span(
                f"{step.span_name}.rollback",
                {
                    **step.attributes,
                    "rollback": True,
                    "original_step": step.step_number
                }
            )
            
            if success:
                console.print(f"  [green]✓[/green] Rollback successful")
            else:
                console.print(f"  [red]✗[/red] Rollback failed")
                rollback_success = False
            
            time.sleep(0.3)
        
        return rollback_success
<% } %>    
    def run(self, dry_run: bool = False) -> bool:
        """Execute the complete <%= name %> workflow.
        
        Args:
            dry_run: If True, only display steps without executing
            
        Returns:
            Success status
        """
        console.print(f"\n[bold]🚀 <%= name.charAt(0).toUpperCase() + name.slice(1) %> Workflow[/bold]")
        console.print(f"[dim]Workflow ID: {self.workflow_id}[/dim]")
        
        # Define workflow steps
        steps = [
<% workflowSteps.forEach(function(step) { %>            WorkflowStep(
                step_number=<%= step.step %>,
                agent="<%= step.agent %>",
                action="<%= step.action %>",
                span_name="<%= step.span_name %>",
                attributes={
                    "step": <%= step.step %>,
                    "agent": "<%= step.agent %>",
                    "action": "<%= step.action %>"
                }
            ),
<% }); %>        ]
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - No spans will be emitted[/yellow]")
            table = Table(title="Workflow Steps")
            table.add_column("Step", style="cyan")
            table.add_column("Agent", style="green")
            table.add_column("Action", style="blue")
            table.add_column("Span", style="dim")
            
            for step in steps:
                table.add_row(
                    str(step.step_number),
                    step.agent,
                    step.action,
                    step.span_name
                )
            
            console.print(table)
            return True
        
<% if (has_monitoring) { %>        # Emit workflow start monitoring span
        self.emit_monitoring_span("started", {"total_steps": len(steps)})
        
<% } %>        # Execute workflow
        success = True
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Executing workflow...", total=len(steps))
            
            for step in steps:
                if not self.execute_step(step):
                    success = False
                    console.print(f"\n[red]Workflow failed at step {step.step_number}[/red]")
<% if (has_rollback) { %>                    self.rollback()<% } %>
                    break
                
                progress.update(task, advance=1)
        
        if success:
            console.print(f"\n[green]✅ Workflow completed successfully![/green]")
            console.print(f"[dim]Executed {len(self.executed_steps)} steps[/dim]")
<% if (has_monitoring) { %>            
            # Emit workflow completion monitoring span
            self.emit_monitoring_span("completed", {
                "duration": time.time() - float(self.workflow_id.split('_')[1]) / 1000,
                "success": True
            })
<% } %>        else:
<% if (has_monitoring) { %>            # Emit workflow failure monitoring span
            self.emit_monitoring_span("failed", {
                "failed_at_step": len(self.executed_steps) + 1,
                "success": False
            })
<% } %>            pass
        
        return success
    
    def get_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": "<%= name %>",
            "total_steps": <%= steps %>,
            "executed_steps": len(self.executed_steps),
            "success": len(self.executed_steps) == <%= steps %>,
            "agents_involved": <%= JSON.stringify(agents) %>,
<% if (has_rollback) { %>            "rollback_available": True,
            "rollback_stack_size": len(self.rollback_stack),<% } %>
<% if (has_monitoring) { %>            "monitoring_enabled": True,<% } %>
        }


def <%= functionName %>(dry_run: bool = False, span_file: Optional[Path] = None) -> bool:
    """Execute the <%= name %> workflow.
    
    Args:
        dry_run: If True, only display steps without executing
        span_file: Optional custom span file path
        
    Returns:
        Success status
    """
    workflow = <%= name.charAt(0).toUpperCase() + name.slice(1) %>Workflow(span_file=span_file)
    return workflow.run(dry_run=dry_run)


if __name__ == "__main__":
    import sys
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    # Execute workflow
    success = <%= functionName %>(dry_run=dry_run)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)